# Microbenchmarks

The make targets can be found in the `Makefile`.
The tests run the [Techempower benchmarks](https://www.techempower.com/benchmarks/#hw=ph&test=json&section=data-r22) (JSON serialization, Single DB query, Multiple DB queries and plaintext)

https://github.com/TechEmpower/FrameworkBenchmarks/wiki/Project-Information-Framework-Tests-Overview#single-database-query

## Experiments

### Running Individual Experiment

1. Run `make telemetry`. This sets up the telemetry applications
2. Setup the postgres: `make postgres`
3. Run the experiment
   1. Throughput Python OpenTelemetry experiment: `make throughput-python` 
   2. Request Duration Python OpenTelemetry experiment: `make python-otel`

### Running Throughput Experiment

1. Run `make all`
2. Run `make throughput`

### Running Request Duration Experiment

The Requests Issued per Second can be configured in the JSON configuration file located at `request-duration/tests/test-config.json`.
The file contains the parameter values for each framework and endpoint

1. Run `make all`
2. Run `make te-all` in the `benchmarker/docker` folder