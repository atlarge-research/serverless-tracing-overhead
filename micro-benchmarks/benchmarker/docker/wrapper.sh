#!/bin/bash

DATE=$(date +'%Y-%m-%d')
DATETIME=$(date +'%Y-%m-%d_%H-%M')

MONITOR_SCRIPT="./cpu.sh"
RESULTS_DIR="results/$DATE"

K6_TEST_NAME=$1

mkdir -p $RESULTS_DIR
K6_TEST="k6 run --out csv=$RESULTS_DIR/$DATETIME.csv $K6_TEST_NAME"

# Start the monitoring script in the background
bash $MONITOR_SCRIPT &

MONITOR_PID=$!

# Start k6 test
$K6_TEST

# Once k6 test completes, kill the monitoring script if it's still running
if kill -0 $MONITOR_PID > /dev/null 2>&1; then
    echo "Stopping the CPU monitoring script."
    kill $MONITOR_PID
fi
