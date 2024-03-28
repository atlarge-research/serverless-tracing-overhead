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

	http.HandleFunc("/plain", plaintextHandler())
	http.HandleFunc("/json", jsonHandler())
	http.HandleFunc("/db", dbHandler(db))
	http.HandleFunc("/queries", queriesHandler(db))

	// Get Port number
	portNumber := os.Getenv("APP_PORT")
	if portNumber == "" {
		portNumber = "5100"
	}
	portNumber = fmt.Sprintf(":%s", portNumber)
	err = http.ListenAndServe(portNumber, nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

// plaintextHandler handles requests to the /plain route
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
