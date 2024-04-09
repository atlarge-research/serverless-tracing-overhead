#!/bin/bash
DATE=$(date +'%Y-%m-%d_%H-%M-%S')
LOG_FILE="cpu_usage_$DATE.csv"

DURATION=6000
INTERVAL=1

echo "Starting CPU monitoring script."

# Clean previous log file
echo "Timestamp, Container, CPU_Percentage" > $LOG_FILE

END_TIME=$((SECONDS+DURATION))

while [ $SECONDS -lt $END_TIME ]; do
    # Append CPU usage with timestamp
    docker stats --no-stream --format "{{.Name}}, {{.CPUPerc}}" | while IFS= read -r line
    do
        echo "$(date +'%s'), $line" >> $LOG_FILE
    done
    sleep $INTERVAL
done

echo "CPU monitoring script finished."
