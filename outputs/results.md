# Execution Results & Output

This document serves as the **Verification Log** for the E-Commerce Data Pipeline. It captures the end-to-end flow from data generation to final visualization.

---

## 1. Orchestration (Airflow)
**Objective:** Verify that the DAG successfully schedules and triggers the pipeline tasks.

![Airflow Grid](1_airflow_dag_success.png)
*Figure 1: Airflow Grid View showing successful execution of the `simulate_user_orders` DAG. The green bars indicate that the `generate_mock_orders` task completed without errors.*

---

## 2. Pipeline Execution (Terminal Logs)
**Objective:** Verify the data flow through the Docker containers (Kafka & Spark).

![Terminal Logs](2_terminal_execution.png)
*Figure 2: Real-time logs from the `run_pipeline.sh` execution.*
* **Top-Left:** Data Generator creating mock orders (Python).
* **Bottom-Left:** Spark Structure Streaming processing batch #4.
* **Right:** Docker logs showing successful container health checks.

---

## 3. Data Warehousing (Snowflake)
**Objective:** Confirm that processed data successfully landed in the Cloud Data Warehouse.

![Snowflake Query](4_snowflake_data_preview.png)
*Figure 3: SQL Query execution in Snowflake verifying the schema and row count. The `ORDERS` table is successfully populated with streaming data.*

---

## 4. Business Intelligence (Dashboard)
**Objective:** Visualize real-time metrics and analytical insights.

![Snowflake Dashboard](3_snowflake_dashboard.png)
*Figure 4: The Final "Real-Time E-Commerce Monitor" Dashboard.*
* **KPIs:** Shows Total Revenue, Order Count, and Average Ticket Size.
* **Charts:** Live trend lines of sales over time and order status distribution.
* **Advanced Analytics:** Displays the "Top Selling Products" leaderboard generated via Star Schema joins.

---

## Conclusion
The pipeline successfully processed **500+ generated transactions** with a latency of **<10 seconds** from ingestion (Kafka) to visualization (Snowflake).