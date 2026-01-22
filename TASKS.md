# Project Roadmap

## Phase 1: Infrastructure Setup
- [ ] Create `docker-compose.yml` with Airflow, Kafka, Zookeeper, and Spark.
- [ ] Verify all containers spin up and communicate.

## Phase 2: Source Data Simulation
- [ ] Design the MySQL schema (Tables: Users, Products, Orders).
- [ ] Write a Python `data_generator.py` script using the `faker` library.
- [ ] Verify data is landing in MySQL.

## Phase 3: Kafka Ingestion
- [ ] Create a Kafka Topic named `order_created`.
- [ ] Write a script (Producer) to push MySQL changes to Kafka.

## Phase 4: Spark Processing
- [ ] Initialize a PySpark session inside Docker.
- [ ] Write a generic Spark job to read from Kafka.
- [ ] Implement data cleaning logic (casting types, handling nulls).

## Phase 5: Snowflake Integration
- [ ] Set up a free trial Snowflake account.
- [ ] Create the Warehouse, Database, and Schema in Snowflake.
- [ ] Configure Spark to write data to Snowflake.

## Phase 6: Orchestration
- [ ] Create an Airflow DAG to trigger the Spark job daily.
- [ ] Create an Airflow DAG to trigger the Data Generator (simulation).