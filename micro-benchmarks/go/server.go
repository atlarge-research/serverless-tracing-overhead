package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	_ "github.com/lib/pq"
	"go.elastic.co/apm/module/apmhttp"
)

type Message struct {
	Message string `json:"message"`
}

type World struct {
	ID           int `json:"id"`
	RandomNumber int `json:"randomNumber"`
}

func main() {
	dsn := getDatabaseDSN()
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	http.HandleFunc("/plaintext", plaintextHandler())
	http.HandleFunc("/json", jsonHandler())
	http.HandleFunc("/db", dbHandler(db))
	http.HandleFunc("/queries", queriesHandler(db))
	http.HandleFunc("/updates", updateHandler(db))

	// Get Port number
	portNumber := os.Getenv("APP_PORT")
	if portNumber == "" {
		portNumber = "8080"
	}
	portNumber = fmt.Sprintf(":%s", portNumber)

	apmEnabled := os.Getenv("ELASTIC_APM_ENABLED") == "true"
	var handler http.Handler = nil
	if apmEnabled {
		handler = apmhttp.Wrap(http.DefaultServeMux)
	}

	err = http.ListenAndServe(portNumber, handler)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

// plaintextHandler handles requests to the /plaintext route
func plaintextHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		w.Header().Set("Content-Length", "13")
		w.Header().Set("Server", "Go HTTP Server")
		w.Header().Set("Date", time.Now().Format(http.TimeFormat))

		fmt.Fprint(w, "Hello, World!")
	}
}

// jsonHandler handles requests to the /json route
func jsonHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		msg := Message{Message: "Hello, World!"}

		// Serialize to JSON
		jsonResponse, err := json.Marshal(msg)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// Headers
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Content-Length", fmt.Sprintf("%d", len(jsonResponse)))
		w.Header().Set("Server", "Go HTTP Server")
		w.Header().Set("Date", time.Now().Format(http.TimeFormat))

		w.Write(jsonResponse)
	}
}

// dbHandler handles requests to the /db route
func dbHandler(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		randID := rand.Intn(10000) + 1

		var world World
		err := db.QueryRow("SELECT id, randomnumber FROM World WHERE id = $1", randID).Scan(&world.ID, &world.RandomNumber)
		if err != nil {
			http.Error(w, "Database error", http.StatusInternalServerError)
			return
		}

		// Serialize to JSON
		jsonResponse, err := json.Marshal(world)
		if err != nil {
			http.Error(w, "JSON serialization error", http.StatusInternalServerError)
			return
		}

		setResponseHeaders(w, len(jsonResponse))
		w.Write(jsonResponse)
	}
}

// queriesHandler handles requests to the /queries route
func queriesHandler(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Retrieve the queries parameter
		numQueries := getQueryCount(r)

		worlds := make([]World, numQueries)
		for i := 0; i < numQueries; i++ {
			randID := rand.Intn(10000) + 1
			err := db.QueryRow("SELECT id, randomNumber FROM World WHERE id = $1", randID).Scan(&worlds[i].ID, &worlds[i].RandomNumber)
			if err != nil {
				http.Error(w, "Database error", http.StatusInternalServerError)
				return
			}
		}

		jsonResponse, err := json.Marshal(worlds)
		if err != nil {
			http.Error(w, "JSON serialization error", http.StatusInternalServerError)
			return
		}

		setResponseHeaders(w, len(jsonResponse))
		w.Write(jsonResponse)
	}
}

// queriesHandler handles requests to the /update route
func updateHandler(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Retrieve the queries parameter
		numQueries := getQueryCount(r)

		if numQueries < 1 {
			numQueries = 1
		} else if numQueries > 500 {
			numQueries = 500
		}

		worlds := make([]World, 0, numQueries)

		// Start transaction
		tx, err := db.Begin()
		if err != nil {
			http.Error(w, "Database transaction start error", http.StatusInternalServerError)
			return
		}
		defer tx.Rollback()

		for i := 0; i < numQueries; i++ {
			// Select a random World object
			world := World{}
			if err := tx.QueryRow("SELECT id, randomNumber FROM World ORDER BY RANDOM() LIMIT 1").Scan(&world.ID, &world.RandomNumber); err != nil {
				http.Error(w, "Database query error", http.StatusInternalServerError)
				return
			}

			// Update randomNumber
			world.RandomNumber = rand.Intn(10000) + 1
			if _, err := tx.Exec("UPDATE World SET randomNumber = $1 WHERE id = $2", world.RandomNumber, world.ID); err != nil {
				http.Error(w, "Database update error", http.StatusInternalServerError)
				return
			}

			worlds = append(worlds, world)
		}

		// Commit transaction
		if err := tx.Commit(); err != nil {
			http.Error(w, "Database transaction commit error", http.StatusInternalServerError)
			return
		}

		// Response
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(worlds)
	}

}

func setResponseHeaders(w http.ResponseWriter, contentLength int) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Content-Length", strconv.Itoa(contentLength))
	w.Header().Set("Server", "Go HTTP Server")
	w.Header().Set("Date", time.Now().Format(http.TimeFormat))
}

// Parse and validate the query parameter
func getQueryCount(r *http.Request) int {
	queryParam := r.URL.Query().Get("queries")
	numQueries, err := strconv.Atoi(queryParam)
	if err != nil || numQueries < 1 {
		return 1
	} else if numQueries > 500 {
		return 500
	}
	return numQueries
}

func getDatabaseDSN() string {
	dbHost := os.Getenv("DB_HOST")
	if dbHost == "" {
		dbHost = "localhost"
	}
	dbUser := os.Getenv("DB_USER")
	if dbUser == "" {
		dbUser = "postgres"
	}
	dbPwd := os.Getenv("DB_PWD")
	if dbPwd == "" {
		dbPwd = "postgres"
	}
	dbName := os.Getenv("DB_NAME")
	if dbName == "" {
		dbName = "world"
	}

	// Construct the DSN string
	return fmt.Sprintf("host=%s user=%s password=%s dbname=%s sslmode=disable", dbHost, dbUser, dbPwd, dbName)
}
