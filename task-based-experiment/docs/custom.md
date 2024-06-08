

Storage start:
`./sebs.py storage start minio --port 9011 --output-json out_storage.json`

Storage stop:
`./sebs.py local stop out_benchmark.json`


Regression tests:
`./sebs.py benchmark regression test --config config/openwhisk.json --deployment openwhisk`