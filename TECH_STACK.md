# Tech Stack & Rationale

## 1. Infrastructure
* **Docker:** We use Docker to containerize our entire environment. This ensures that the project runs exactly the same on my machine as it does on yours. It eliminates "dependency hell."

## 2. Source System (OLTP)
* **MySQL:** This acts as our "Production Database." It simulates the e-commerce application backend where users place orders. We will treat this as the *Source of Truth*.

## 3. Ingestion & Streaming
* **Kafka:** Acts as the highly reliable buffer. When an order is placed in MySQL, it is streamed to Kafka. This decouples the slow database from the fast processing engine.
* **Zookeeper:** Necessary to manage the Kafka cluster metadata.

## 4. Processing
* **PySpark (Apache Spark):** The heavy lifter. Spark subscribes to the Kafka stream, reads the raw JSON data, performs transformations (cleaning, formatting, aggregation), and prepares it for the warehouse.

## 5. Storage & Warehousing (OLAP)
* **Snowflake:** Our Cloud Data Warehouse. This is where the clean, modeled data lives. It is optimized for reading large datasets for analytics, unlike MySQL which is optimized for writing individual transactions.

## 6. Orchestration
* **Apache Airflow:** The conductor. It manages the dependencies between tasks. For example: "Don't run the Daily Report until the Data Loading job is finished."