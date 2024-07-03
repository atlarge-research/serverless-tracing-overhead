# OpenWhisk install on Kubernetes Kind cluster

## Charts

### All

```shell
helm repo add openwhisk https://openwhisk.apache.org/charts
helm install owdev openwhisk/openwhisk -n openwhisk --create-namespace -f openwhisk/mycluster.yaml
# helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
# helm repo add elastic https://helm.elastic.co

# helm install otel-collector open-telemetry/opentelemetry-collector -n telemetry --create-namespace -f opentelemetry-collector/values.yaml
# helm install elasticsearch elastic/elasticsearch -n telemetry -f elastic/elasticsearch-values.yaml
# helm install apm-server elastic/apm-server -n telemetry -f elastic/apm-server-values.yaml
# helm install kibana elastic/kibana -n telemetry -f elastic/kibana-values.yaml

# sudo kubectl create ns telemetry
# sudo helm install my-otel-collector open-telemetry/opentelemetry-collector -n telemetry -f opentelemetry-collector/values.yaml
# sudo helm install elasticsearch elastic/elasticsearch -n telemetry -f elastic/elasticsearch-values.yaml --version 7.17.1
# sudo helm install kibana elastic/kibana -n telemetry -f elastic/kibana-values.yaml --version 7.17.1
# sudo helm install apm-server elastic/apm-server -n telemetry -f elastic/apm-server-values.yaml --version 7.17.1

```

### OpenWhisk

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

## OpenTelemetry Collector


