import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType

# READ CREDENTIALS FROM ENVIRONMENT
sf_user = os.getenv("SNOWFLAKE_USER")
sf_password = os.getenv("SNOWFLAKE_PASSWORD")
sf_account = os.getenv("SNOWFLAKE_ACCOUNT")

# Verify they exist (Debugging safety)
if not all([sf_user, sf_password, sf_account]):
    raise ValueError("Missing Snowflake Credentials in Environment Variables!")

snowflake_options = {
    "sfUrl": f"{sf_account}.snowflakecomputing.com",
    "sfUser": sf_user,
    "sfPassword": sf_password,
    "sfDatabase": "ECOMMERCE_DB",
    "sfSchema": "RAW_DATA",
    "sfWarehouse": "COMPUTE_WH"
}

def process_stream():
    # 2. Initialize Spark with Snowflake + Kafka Dependencies
    spark = SparkSession.builder \
        .appName("EcommerceOrderProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,net.snowflake:spark-snowflake_2.12:2.12.0-spark_3.4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 3. Define Schema (Same as before)
    order_schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("total_price", DoubleType(), True),
        StructField("status", StringType(), True),
        StructField("created_at", StringType(), True)
    ])

    # 4. Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "order_created") \
        .option("startingOffsets", "earliest") \
        .load()

    # 5. Transform
    parsed_df = df.select(from_json(col("value").cast("string"), order_schema).alias("data")).select("data.*")
    clean_df = parsed_df.withColumn("created_at", col("created_at").cast(TimestampType()))

    # 6. WRITE TO SNOWFLAKE (The Change)
    # We use "foreachBatch" because Snowflake streaming requires writing micro-batches
    def write_to_snowflake(batch_df, batch_id):
        if batch_df.count() > 0:
            print(f"Writing batch {batch_id} with {batch_df.count()} records to Snowflake...")
            batch_df.write \
                .format("snowflake") \
                .options(**snowflake_options) \
                .option("dbtable", "orders") \
                .mode("append") \
                .save()
            print("Done!")

    query = clean_df.writeStream \
        .foreachBatch(write_to_snowflake) \
        .outputMode("append") \
        .start()

    print("--- Spark Streaming to Snowflake Started ---")
    query.awaitTermination()

if __name__ == "__main__":
    process_stream()