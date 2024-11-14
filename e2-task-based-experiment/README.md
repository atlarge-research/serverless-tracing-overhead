# Experiment 2 - Evaluation of Serverless Applications

## Running the Experiments

## Setup and Configuration

1. Setup Kubernetes with Kind and OpenWhisk through the README.md in the `infrastructure` directory under the root directory.
2. Set up the telemetry applications (OpenTelemetry Collector, Elasticsearch, and Kibana).
This can be done by running `make telemetry` in the experiment-1 directory.
3. Replace the IP in the OpenTelemetry endpoint to your local ip in all applications. E.g. http://192.168.1.109:4317. (TODO: This should be simpler and only set once)
4. Start the MinIO storage: `./sebs.py storage start minio --port 9011 --output-json out_storage.json`
5. Replace the configuration values of MinIO in all the configuration files. These files are located in the `config` directory. (TODO: Again, this should be set in one place and be simpler)
   1. Replace the `address` with your local IP
   2. Replace the `access_key` with the access key from `out_storage.json` file
   3. Replace the `secret_key` with the secret key from `out_storage.json` file
   4. Replace the `instance_id` with the instance id from `out_storage.json` file



### Running Python Experiments

1. Run `make python`

### Running Node.js Experiments

1. Run `make nodejs`

### Running All Experiments

1. Run `make all`
