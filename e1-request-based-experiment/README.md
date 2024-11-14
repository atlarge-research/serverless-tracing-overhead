# Microbenchmarks

The make targets can be found in the `Makefile`.
The tests run the [Techempower benchmarks](https://www.techempower.com/benchmarks/#hw=ph&test=json&section=data-r22) (JSON serialization, Single DB query, Multiple DB queries and plaintext)

https://github.com/TechEmpower/FrameworkBenchmarks/wiki/Project-Information-Framework-Tests-Overview#single-database-query

## Experiments

### Running Individual Experiment

1. Run `make telemetry`. This sets up the 
2. Run the experiment
   1. Throughput Python OpenTelemetry experiment: `make throughput-python` 
   2. Request Duration Python OpenTelemetry experiment: `make python-otel`

### Running Throughput Experiment

1. Run `make all`
2. Run `make throughput`

### Running Request Duration Experiment

1. Run `make all`
2. Run `make te-all` in the `benchmarker/docker` folder