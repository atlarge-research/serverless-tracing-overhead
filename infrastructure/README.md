# E2 Setup (Task based serverless)

1. Spin up the Kind cluster in the `infrastructure/kind` folder via `start-kind.sh`
2. Install OpenWhisk `helm install owdev openwhisk/openwhisk -n openwhisk --create-namespace -f openwhisk/mycluster.yaml`
3. Configure OpenWhisk by setting the apihost and auth
4. Start telemetry services `make telemetry` in E1 folder
5. Set up the SeBS framework
   1. Create venv `python3 -m venv ./python-venv`
   2. Activate `. python-venv/bin/activate`
   3. Install dependencies `./install.py --openwhisk`

5. Set up the minio bucket
6. Configure the bucket IP and end port in the config files


## Charts

### Install OpenWhisk

```shell
helm repo add openwhisk https://openwhisk.apache.org/charts
helm install owdev openwhisk/openwhisk -n openwhisk --create-namespace -f openwhisk/mycluster.yaml
```

### OpenWhisk Setup

```
wsk property set --apihost localhost:31001
wsk property set --auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP
```

## Changes to OpenWhisk Configuration

actionsInvokesPerminute: 1000
    actionsInvokesConcurrent: 100
    actions Max memory

* Increased Actions Max memory
* Increased Actions Invokes per minute
* Increased Actions Invokes Concurrent value



