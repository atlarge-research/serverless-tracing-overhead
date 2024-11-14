# Experiment 3 - Quantifiyng the Sources of Overhead in Distributed Tracing

## Running the Experiments

### Running the experiments

The number of iterations can be configured in the docker-compose files under the `docker-compose` directory.

1. Start the telemetry applications: `make telemetry`
2. Start the database: `make postgres`
3. Run one of the applications, for example: `make dynamic-html-cold`

## Creating a Flamegraph

1. Install the flameprof library: `pip install flameprof`
2. Use the .prof files to generate the flamegraph or run a single iteration by running the `main.py` file 
   1. `python main.py & flameprof workload.prof > flamegraph.svg`  