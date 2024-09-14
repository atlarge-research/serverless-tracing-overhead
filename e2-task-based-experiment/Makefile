.PHONY: all python nodejs python-nodejs non-instrumented-python instrumented-python non-instrumented-nodejs instrumented-nodejs

all: python-nodejs

python-nodejs: non-instrumented-python instrumented-python non-instrumented-nodejs instrumented-nodejs

python: non-instrumented-python instrumented-python

nodejs: non-instrumented-nodejs instrumented-nodejs

custom-run:
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/110.dynamic-html.json --output-dir experiment-results/nodejs/non-instrumented/110.dynamic-html --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/640.video-processing.json --output-dir experiment-results/python/instrumented/640.video-processing-otel --deployment openwhisk

# Non-instrumented Python Experiments
non-instrumented-python:
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/110.dynamic-html.json --output-dir experiment-results/python/non-instrumented/110.dynamic-html --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/120.uploader.json --output-dir experiment-results/python/non-instrumented/120.uploader --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/210.thumbnailer.json --output-dir experiment-results/python/non-instrumented/210.thumbnailer --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/221.video-processing.json --output-dir experiment-results/python/non-instrumented/221.video-processing --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/501.graph-pagerank.json --output-dir experiment-results/python/non-instrumented/501.graph-pagerank --deployment openwhisk

# Instrumented Python Experiments
instrumented-python:
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/610.dynamic-html.json --output-dir experiment-results/python/instrumented/610.dynamic-html-otel --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/620.uploader.json --output-dir experiment-results/python/instrumented/620.uploader-otel --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/630.thumbnailer.json --output-dir experiment-results/python/instrumented/630.thumbnailer-otel --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/640.video-processing.json --output-dir experiment-results/python/instrumented/640.video-processing-otel --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/660.graph-pagerank.json --output-dir experiment-results/python/instrumented/660.graph-pagerank --deployment openwhisk

# Non-instrumented NodeJS Experiments
non-instrumented-nodejs:
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/110.dynamic-html.json --output-dir experiment-results/nodejs/non-instrumented/110.dynamic-html --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/120.uploader.json --output-dir experiment-results/nodejs/non-instrumented/120.uploader --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/210.thumbnailer.json --output-dir experiment-results/nodejs/non-instrumented/210.thumbnailer --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/221.video-processing.json --output-dir experiment-results/nodejs/non-instrumented/221.video-processing --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/501.graph-pagerank-nodejs.json --output-dir experiment-results/nodejs/non-instrumented/501.graph-pagerank --deployment openwhisk --language nodejs --language-version "12"


# Instrumented NodeJS Experiments
instrumented-nodejs:
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/610.dynamic-html.json --output-dir experiment-results/nodejs/instrumented/610.dynamic-html-otel --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/620.uploader.json --output-dir experiment-results/nodejs/instrumented/620.uploader-otel --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/630.thumbnailer.json --output-dir experiment-results/nodejs/instrumented/630.thumbnailer-otel --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/640.video-processing.json --output-dir experiment-results/nodejs/instrumented/640.video-processing-otel --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/660.graph-pagerank-nodejs.json --output-dir experiment-results/nodejs/instrumented/660.graph-pagerank --deployment openwhisk --language nodejs --language-version "12"


pagerank:
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/501.graph-pagerank.json --output-dir experiment-results/python/non-instrumented/501.graph-pagerank --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/660.graph-pagerank.json --output-dir experiment-results/python/instrumented/660.graph-pagerank --deployment openwhisk
	./sebs.py experiment invoke perf-cost --config config/experiments/non-instrumented/501.graph-pagerank-nodejs.json --output-dir experiment-results/nodejs/non-instrumented/501.graph-pagerank --deployment openwhisk --language nodejs --language-version "12"
	./sebs.py experiment invoke perf-cost --config config/experiments/instrumented/660.graph-pagerank-nodejs.json --output-dir experiment-results/nodejs/instrumented/660.graph-pagerank --deployment openwhisk --language nodejs --language-version "12"
