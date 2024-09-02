import os

import requests
import multiprocessing
import time
from flask_app.app import configure_opentelemetry, create_app
from multiprocessing import Manager
from utils import save_aggregated_statistics, save_each_run_results


def run_flask_app(profiling_data):
    # Create a Flask app instance
    app, db = create_app(profiling_data)

    # Configure OpenTelemetry within the application context
    with app.app_context():
        configure_opentelemetry(app, db, "e3-request-based-flask")

    app.run(host="0.0.0.0", port=5000, debug=False)


def run_experiment(endpoint="updates", iterations=100000):
    url = f"http://localhost:5000/{endpoint}"

    params = {}
    if endpoint == "updates":
        params = {"queries": 10}

    # Start Flask app in a separate process
    flask_process = multiprocessing.Process(target=run_flask_app, args=(profiling_data,))
    flask_process.start()

    # Wait a moment for the Flask app to start
    time.sleep(2)

    # Run requests to the endpoint
    for i in range(iterations):
        print("Iteration:", i)
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")

    # Stop the Flask app
    flask_process.terminate()
    flask_process.join()


if __name__ == "__main__":
    # Create a Manager for the shared list
    manager = Manager()
    profiling_data = manager.list()

    _endpoint = os.getenv("EXPERIMENT_ENDPOINT", "updates")
    _iterations = int(os.getenv("EXPERIMENT_ITERATIONS", 10))
    print("Running experiment {} with {} iterations".format(_endpoint, _iterations))

    # Run the experiment and collect profiling data
    run_experiment(endpoint=_endpoint, iterations=_iterations)

    # Convert the manager's list to a regular list for processing
    profiling_data_list = list(profiling_data)

    # Save each run's results to a CSV file
    save_each_run_results(times_dict_list=profiling_data_list,
                          filename=f"output/{_endpoint}_{_iterations}_each_run_results.csv")

    # Save aggregated statistics to a CSV file
    save_aggregated_statistics(times_dict_list=profiling_data_list,
                               filename=f"output/{_endpoint}_{_iterations}_aggregated_statistics.csv")