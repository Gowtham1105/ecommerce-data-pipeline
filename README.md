# Real-Time E-Commerce Data Engineering Pipeline

## Project Overview
This repository contains the source code for a scalable, end-to-end data engineering pipeline designed to process e-commerce transaction data in real-time. The system simulates a production environment where order data is generated, ingested, processed using distributed computing, and warehoused for analytical reporting.

The pipeline handles the full data lifecycle:
1.  **Generation:** Simulation of user, product, and order data stored in a relational database.
2.  **Ingestion:** Real-time streaming of transaction events via a message broker.
3.  **Processing:** Micro-batch processing and transformation using a distributed engine.
4.  **Storage:** Loading processed data into a cloud data warehouse.
5.  **Analytics:** Execution of complex SQL queries for anomaly detection and segmentation.
6.  **Visualization:** Real-time dashboarding for business intelligence.

## Architecture

**Data Flow:**
`Python Generator` -> `MySQL` -> `Apache Kafka` -> `Apache Spark` -> `Snowflake` -> `Snowsight Dashboard`

* **Source System:** A Python script populates a MySQL database with synthetic transactional data (Users, Products, Orders) to mimic a live e-commerce platform.
* **Message Broker:** Apache Kafka acts as the decoupling layer, buffering high-velocity order events to ensure zero data loss.
* **Stream Processing:** Apache Spark (Structured Streaming) consumes data from Kafka, enforces schema validation, performs transformations, and writes data to Snowflake in micro-batches.
* **Data Warehouse:** Snowflake serves as the final destination for analytical data storage (`ECOMMERCE_DB`).
* **Orchestration:** Apache Airflow is configured to schedule and monitor data generation tasks (optional execution mode).
* **Infrastructure:** All local components are containerized using Docker and Docker Compose.

## Technology Stack

* **Language:** Python 3.9+, SQL
* **Containerization:** Docker, Docker Compose
* **Database:** MySQL 8.0
* **Streaming:** Apache Kafka 3.6, Zookeeper 3.8
* **Processing:** Apache Spark 3.5 (PySpark)
* **Warehousing:** Snowflake
* **Orchestration:** Apache Airflow 2.7
* **Version Control:** Git

## Directory Structure

```
ecommerce-pipeline/
├── dags/                  # Airflow DAGs for task scheduling
├── scripts/               # Python utility scripts
│   ├── data_generator.py  # Generates mock data into MySQL
│   ├── kafka_producer.py  # Reads from MySQL and pushes to Kafka
│   └── init_db.py         # Database initialization logic
├── spark_jobs/            # Spark application logic
│   └── stream_processor.py# Spark Structured Streaming job
├── snowflake_sql/         # SQL scripts for warehousing logic
│   ├── 1_setup_and_schema.sql # DDL for tables and schema
│   └── 2_advanced_analytics.sql # DML for analytical queries
├── outputs/               # Execution logs and verification screenshots
├── docker/                # Docker configuration files
├── tests/                 # Unit and integration tests
├── .env                   # Environment variables (GitIgnored)
├── env.template           # Template for environment variables
├── docker-compose.yml     # Container service definitions
├── requirements.txt       # Python dependencies
└── run_pipeline.sh        # Master execution shell script
```
## Prerequisites

Ensure the following are installed and configured before running the pipeline:

1.  **Docker Desktop:** Required for running containerized services (MySQL, Kafka, Spark).
2.  **Git:** Required for version control and repository cloning.
3.  **Snowflake Account:** A valid account with sufficient permissions to create databases, schemas, and tables.

## Configuration Setup

The project relies on environment variables for secure credential management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gowtham1105/ecommerce-pipeline.git
    cd ecommerce-pipeline
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory by copying the provided template.
    ```bash
    cp env.template .env
    ```

3.  **Update Credentials:**
    Open the `.env` file and populate the fields with your Snowflake credentials.
    ```ini
    SNOWFLAKE_USER=your_username
    SNOWFLAKE_PASSWORD=your_password
    SNOWFLAKE_ACCOUNT=your_account_identifier
    MYSQL_PASSWORD=rootpassword
    ```
    *Note: The `SNOWFLAKE_ACCOUNT` must be the account identifier only (e.g., `xy12345.us-east-1`). Do not include `https://` or `.snowflakecomputing.com`.*

## Installation and Execution

### 1. Database Initialization
Before running the pipeline, the Snowflake resources must be provisioned.

1.  Log in to the Snowflake console.
2.  Open a new SQL Worksheet.
3.  Copy and execute the contents of `snowflake_sql/1_setup_and_schema.sql`.
    * This script creates the `ECOMMERCE_DB` database, `RAW_DATA` schema, and populates the `PRODUCTS` dimension table.

### 2. Pipeline Execution (Automated)
A master shell script is provided to automate the infrastructure startup and execution sequence.

Run the following command in your terminal:

```bash
./run_pipeline.sh

**Execution Sequence:**

1.  **Infrastructure Initialization:**
    * The script triggers `docker-compose up -d`.
    * Containers for MySQL, Kafka, Zookeeper, and Spark Master/Worker are provisioned in detached mode.

2.  **Service Health Verification:**
    * The script enters a polling loop, checking for active TCP listeners on:
        * Port **3307** (MySQL)
        * Port **9094** (Kafka)
        * Port **8080** (Spark Master UI)
    * Execution pauses until all critical services report as `Online`.

3.  **Data Generation (Source):**
    * `scripts/data_generator.py` is executed.
    * This script connects to the MySQL container and inserts synthetic transactional records (User profiles, Product inventory, and Orders).

4.  **Stream Ingestion (Producer):**
    * `scripts/kafka_producer.py` is executed.
    * The producer queries new records from MySQL and serializes them as JSON messages to the `ecommerce_orders` Kafka topic.

5.  **Distributed Processing (Spark Job):**
    * The script submits `spark_jobs/stream_processor.py` to the Spark Master using `spark-submit`.
    * **Configuration:** The job is deployed with constrained resources (512MB Driver/Executor) to ensure stability in the Docker environment.
    * **Logic:** The job reads from Kafka, enforces schema validation, transforms the stream, and writes micro-batches to the Snowflake `ORDERS` table.
```

### 3. Verification

**Terminal Output:**
The execution script provides real-time logs. Successful execution is indicated by:
* `✅ MySQL Database is Online!`
* `✅ Kafka Broker is Online!`
* Spark logs showing batch processing status (e.g., `Batch: 0`, `Batch: 1`).

**Snowflake Validation:**
Execute the following query in Snowflake to verify successful data ingestion:
```sql
SELECT COUNT(*) FROM ECOMMERCE_DB.RAW_DATA.ORDERS;
```
## Analytics and Reporting

Post-ingestion analytics are executed directly within the Snowflake Data Warehouse using the SQL scripts provided in `snowflake_sql/2_advanced_analytics.sql`. The pipeline supports the following analytical use cases:

1.  **Revenue Aggregation (Star Schema Join):**
    * **Logic:** Performs an inner join between the streaming `ORDERS` fact table and the static `PRODUCTS` dimension table.
    * **Output:** Aggregates total revenue and quantity sold per product category to identify top-performing inventory.

2.  **Statistical Anomaly Detection (Z-Score):**
    * **Logic:** Calculates the mean and standard deviation of transaction values. It computes the Z-Score for each incoming order to measure its distance from the mean.
    * **Output:** Flags transactions with a Z-Score absolute value greater than 2 (indicating a deviation of more than two standard deviations) as potential fraud or outliers.

3.  **Customer Segmentation (RFM Analysis):**
    * **Logic:** Utilizes SQL Window Functions (`NTILE`) to rank users based on their cumulative monetary spend.
    * **Output:** Segments the user base into tiered cohorts (VIP, Gold, Silver) for targeted analysis.

## Troubleshooting

### Common Runtime Errors

* **Spark Container Exit Code 137 (OOM):**
    * **Cause:** The Spark container exceeded the allocated memory limit.
    * **Resolution:** Increase the memory resource allocation in Docker Desktop settings to a minimum of 4GB. Alternatively, verify that the `spark-submit` command includes the `--driver-memory 512m` flag.

* **Snowflake Connection Failure:**
    * **Cause:** Incorrect formatting of the `SNOWFLAKE_ACCOUNT` environment variable.
    * **Resolution:** Ensure the variable contains only the account identifier (e.g., `xy12345.us-east-1`). It must not contain protocols (`https://`) or domain suffixes (`.snowflakecomputing.com`).

* **Port Bind Conflicts:**
    * **Cause:** The required ports (3307, 9094, 8080) are occupied by other host processes.
    * **Resolution:** Terminate the conflicting processes or modify the port mappings in `docker-compose.yml`.

## License

This project is open-source and licensed under the MIT License.

