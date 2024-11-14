# Microbenchmarks

The make targets can be found in the `Makefile`.
The tests run the [Techempower benchmarks](https://www.techempower.com/benchmarks/#hw=ph&test=json&section=data-r22) (JSON serialization, Single DB query, Multiple DB queries and plaintext)

https://github.com/TechEmpower/FrameworkBenchmarks/wiki/Project-Information-Framework-Tests-Overview#single-database-query

## Experiments

### Setup and Configuration

1. Run `make telemetry`. This sets up the telemetry applications
2. Setup the postgres: `make postgres`
3. Start the applications: `make app-all`

### Running Individual Throughput Experiment

1. Start the python applications: `make python-all`
1. Python OpenTelemetry experiment: `make throughput-python`

### Running Throughput Experiment

1. Run `make throughput`

### Running Request Duration Experiment

The Requests Issued per Second can be configured in the JSON configuration file located at `request-duration/tests/test-config.json`.
The file contains the parameter values for each framework and endpoint

1. Run `make run` in the `request-duration` folder