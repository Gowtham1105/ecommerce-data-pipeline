# Execution Flow

1.  **Generate:** The `scripts/data_generator.py` script runs. It creates a fake "Order" and writes it to **MySQL**.
2.  **Ingest:** A Producer script detects the new order in MySQL and sends a JSON message to the **Kafka** topic `order_created`.
3.  **Process:** **PySpark** is listening to that Kafka topic. It pulls the batch of messages.
4.  **Transform:** Spark cleans the data (e.g., calculates total price, formats dates).
5.  **Load:** Spark pushes the transformed data into **Snowflake** tables.
6.  **Analyze:** We can run SQL queries in Snowflake to see the results.