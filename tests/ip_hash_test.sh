#!/bin/bash

# Function to simulate task requests
simulate_task_request() {
    local task_name=$1
    local source_ip=$2
    echo "Simulating $task_name task request from $source_ip..."
    curl -s -X GET -H "Content-Type: application/json" -H "Cache-Control: no-cache" "http://localhost:8080/$task_name" --interface $source_ip
    echo " "
}

# Test IP Hashed Load Balancer
echo "Testing IP Hashed Load Balancer..."
simulate_task_request "task1" "192.168.1.100"
simulate_task_request "task2" "192.168.1.100"
simulate_task_request "task3" "192.168.1.100"
simulate_task_request "task4" "192.168.1.101"
simulate_task_request "task5" "192.168.1.101"

# Add more tests for other load balancing algorithms if needed
