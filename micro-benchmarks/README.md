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

Steps:

* Write the program
* Benchmark it somehow (measure the execution time over 1000 requests for example)
* Add instrumentation
* Benchmark it again
* Compare
* Plot


# Benchmarker
* k6
* Parse the results
* Plot the results

# Setup TODO

* PostgreSQL docker with table and content
* Flask app
* 