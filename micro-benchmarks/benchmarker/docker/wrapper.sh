#!/bin/bash

MONITOR_SCRIPT="./cpu.sh"
K6_TEST_NAME=$1

K6_TEST="make ${K6_TEST_NAME}"

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
