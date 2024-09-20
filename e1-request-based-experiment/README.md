# Microbenchmarks

The make targets can be found in the `Makefile`.
The tests run the [Techempower benchmarks](https://www.techempower.com/benchmarks/#hw=ph&test=json&section=data-r22) (JSON serialization, Single DB query, Multiple DB queries and plaintext)
Running the tests example:
```shell
make python
make java
make go
```

https://github.com/TechEmpower/FrameworkBenchmarks/wiki/Project-Information-Framework-Tests-Overview#single-database-query


## Throughput experiment

1. Run `make all`
2. Run `make rps-calibrator`

## Request duration experiment

1. Run `make all`
2. Run `make te-all` in the `benchmarker/docker` folder