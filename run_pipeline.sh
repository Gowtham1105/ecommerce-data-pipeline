#!/bin/bash

# =================================================================
# E-COMMERCE PIPELINE: MASTER RUN SCRIPT (INTELLIGENT STARTUP)
# =================================================================

# --- HELPER FUNCTION: Wait for a Port to Open ---
wait_for_service() {
    local PORT=$1
    local SERVICE=$2
    echo "Waiting for $SERVICE to start on Port $PORT..."
    
    # Try to connect to the port every 2 seconds
    # Uses 'nc' (Netcat) which is built into most Linux/Codespaces terminals
    while ! nc -z localhost $PORT; do   
      sleep 2
      echo -n "."
    done
    echo ""
    echo "$SERVICE is Online!"
}

# 1. START INFRASTRUCTURE
echo "----------------------------------------------------"
echo "STARTING DOCKER CONTAINERS..."
echo "----------------------------------------------------"
docker-compose up -d

echo "Verifying services..."

# Check MySQL (Port 3307)
wait_for_service 3307 "MySQL Database"
# Give MySQL an extra 5s buffer to initialize the internal tables after port opens
sleep 5 

# Check Kafka (Port 9094)
wait_for_service 9094 "Kafka Broker"
sleep 2

# Check Spark Master Web UI (Port 8080)
wait_for_service 8080 "Spark Master UI"

echo "----------------------------------------------------"
echo "ALL SYSTEMS GO! PIPELINE STARTING..."
echo "----------------------------------------------------"

# 2. GENERATE DATA
echo "STEP 1: GENERATING MOCK ORDERS (Python -> MySQL)..."
python scripts/data_generator.py

# 3. STREAM TO KAFKA
echo "STEP 2: STREAMING TO KAFKA (MySQL -> Kafka Topic)..."
python scripts/kafka_producer.py

# 4. PROCESS WITH SPARK
echo "STEP 3: STARTING SPARK STREAMING (Kafka -> Snowflake)..."
echo "(Press CTRL+C to stop the stream)"
echo "----------------------------------------------------"

docker exec -u 0 -it spark-master /opt/bitnami/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,net.snowflake:spark-snowflake_2.12:2.12.0-spark_3.4 \
  --master spark://spark-master:7077 \
  --driver-memory 512m \
  --executor-memory 512m \
  --conf spark.cores.max=1 \
  /opt/bitnami/spark/jobs/stream_processor.py