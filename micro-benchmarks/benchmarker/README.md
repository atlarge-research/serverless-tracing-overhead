## Python tests
```shell
make python-all
```

## Go tests
```shell
make go-all
```

## K6

```shell
K6_WEB_DASHBOARD=true k6 run --out csv=test_results.csv benchmark_test.js
``` 

### Thoughts

- Follow the Benchmark tests
- Run the tests for all cases -- **plaintext**
    - Python
    - Python-otel
    - Go
    - Go-otel
- Run the tests for all cases -- **json**
- Run the tests for all cases -- **single query**
- Run the tests for all cases -- **multiple queries**
- Compare the results (Nr of requests in total, Successful requests, request time, throughput etc.)