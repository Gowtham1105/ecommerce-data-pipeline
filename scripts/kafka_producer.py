import time
import json
import mysql.connector
from kafka import KafkaProducer
from decimal import Decimal

# --- Configuration ---
KAFKA_TOPIC = "order_created"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

# Database config
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'ecommerce_db',
    'port': 3307
}

# --- Initialize Kafka Producer ---
# We use a serializer to ensure data is sent as clean JSON bytes
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def get_db_connection():
    return mysql.connector.connect(**db_config)

def run_producer():
    print("Kafka Producer started... listening for new orders.")
    
    # We start tracking from ID 0. In a real app, you might save this to a file
    # so you don't re-send old orders if the script restarts.
    last_order_id = 0
    
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True) # dictionary=True gives us {'id': 1, ...} instead of (1, ...)
            
            # POLL: Get all orders that have an ID greater than what we last saw
            query = "SELECT * FROM orders WHERE order_id > %s ORDER BY order_id ASC"
            cursor.execute(query, (last_order_id,))
            new_orders = cursor.fetchall()
            
            if new_orders:
                print(f"Found {len(new_orders)} new orders. Streaming to Kafka...")
                
                for order in new_orders:
                    # FIX: Datetime objects are not JSON serializable, convert them to string
                    if 'created_at' in order:
                        order['created_at'] = str(order['created_at'])
                    
                    # 2. Convert Decimal to Float (The fix for your error)
                    # We check specifically for 'total_price' or any other decimal field
                    if 'total_price' in order and isinstance(order['total_price'], Decimal):
                        order['total_price'] = float(order['total_price'])   
                    
                    # Send to Kafka
                    producer.send(KAFKA_TOPIC, order)
                    
                    # Update our local bookmark
                    last_order_id = order['order_id']
                    print(f"   -> Sent Order ID: {last_order_id}")
                
                producer.flush() # Force send immediately
                print("Batch sent.")
            else:
                # No new data, just wait a bit
                print("zzZ No new orders. Waiting...", end='\r')
            
            cursor.close()
            conn.close()
            
            # Sleep for 5 seconds before checking again (The "Poll Interval")
            time.sleep(5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_producer()