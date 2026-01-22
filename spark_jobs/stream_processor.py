from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType

def process_stream():
    # 1. Initialize Spark Session
    # We need to download the Spark-Kafka connector jar at runtime, hence the 'config' line.
    spark = SparkSession.builder \
        .appName("EcommerceOrderProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN") # Reduce noise in the logs

    # 2. Define the Schema (What does our JSON look like?)
    # This must match the keys in your Python Producer script
    order_schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("total_price", DoubleType(), True),
        StructField("status", StringType(), True),
        StructField("created_at", StringType(), True) # We read as String first, cast to Timestamp later
    ])

    # 3. Read from Kafka
    # We are subscribing to the 'order_created' topic
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "order_created") \
        .option("startingOffsets", "earliest") \
        .load()

    # 4. Transform the Data
    # Kafka gives us binary 'value'. We cast it to String, then parse the JSON using our Schema.
    parsed_df = df.select(from_json(col("value").cast("string"), order_schema).alias("data")).select("data.*")

    # Let's clean the data types: Convert 'created_at' string to actual Timestamp
    clean_df = parsed_df.withColumn("created_at", col("created_at").cast(TimestampType()))

    # 5. Output to Console (Verification)
    # This will print the table in your terminal every time a batch arrives.
    query = clean_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    print("--- Spark Streaming Started ---")
    query.awaitTermination()

if __name__ == "__main__":
    process_stream()