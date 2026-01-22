import time
import random
from faker import Faker
import mysql.connector

# 1. SETUP: Connect to the Database
# We use port 3307 because that is what we exposed in docker-compose.yml
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'ecommerce_db',
    'port': 3307 
}

fake = Faker()

def get_connection():
    return mysql.connector.connect(**db_config)

def generate_users(n=25):
    conn = get_connection()
    cursor = conn.cursor()
    print(f"Generating {n} users...")
    for _ in range(n):
        sql = "INSERT INTO users (name, email, address) VALUES (%s, %s, %s)"
        val = (fake.name(), fake.email(), fake.address())
        cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()
    print("Users generated!")

def generate_products():
    # We only need to run this once to set up the catalog
    products = [
        ('Laptop', 'Electronics', 50000.00),
        ('Mouse', 'Electronics', 2500.50),
        ('Keyboard', 'Electronics', 4500.00),
        ('Headphones', 'Electronics', 2000.00),
        ('T-Shirt', 'Clothing', 1500.00),
        ('Jeans', 'Clothing', 4000.00),
        ('Sneakers', 'Clothing', 6000.00),
        ('Coffee Mug', 'Home', 1200.00),
        ('Water Bottle', 'Home', 500.00),
        ('Backpack', 'Accessories', 1500.00)
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    print("Seeding products...")
    for p in products:
        # 'IGNORE' prevents duplicate errors if we run this script twice
        sql = "INSERT IGNORE INTO products (name, category, price) VALUES (%s, %s, %s)" 
        cursor.execute(sql, p) # We don't verify duplicates for simplicity here, usually we check IDs
    conn.commit()
    cursor.close()
    conn.close()
    print("Products seeded!")

def generate_orders(n=100):
    conn = get_connection()
    cursor = conn.cursor()
    
    # First, get lists of valid IDs so we don't fake an order for a user who doesn't exist
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall() # List of (id, price) tuples
    
    if not user_ids or not products:
        print("Error: No users or products found. Run generate_users() and generate_products() first.")
        return

    print(f"Generating {n} orders...")
    for _ in range(n):
        user_id = random.choice(user_ids)
        product = random.choice(products)
        product_id = product[0]
        price = float(product[1])
        quantity = random.randint(1, 5)
        status = random.choice(["Pending","Delivered","Shipped"])
        total_price = price * quantity
        
        sql = "INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES (%s, %s, %s, %s, %s)"
        val = (user_id, product_id, quantity, total_price, status)
        cursor.execute(sql, val)
        
        # Simulate a tiny delay so timestamps differ slightly
        time.sleep(0.1) 
        
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{n} Orders generated successfully!")

if __name__ == "__main__":
    # Run the setup functions
    generate_users(100)      # Create 25 fake users
    generate_products()     # Create the product catalog
    generate_orders(500)     # Create 100 fake orders