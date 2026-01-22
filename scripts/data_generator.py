import time
import random
from faker import Faker
import mysql.connector
import os

fake = Faker()

def get_db_connection():
    """
    Hybrid Connection Logic:
    1. Tries 'mysql' (Docker internal hostname) on port 3306.
       -> Used when running inside Airflow.
    2. Falls back to 'localhost' on port 3307.
       -> Used when running manually in VS Code.
    """
    # ATTEMPT 1: Docker Internal (Airflow)
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="root",
            password="root",
            database="ecommerce_db",
            port=3306
        )
        print("✅ Connected via Docker Network (mysql:3306)")
        return conn
    except Exception as e:
        print(f"⚠️  Docker connection failed ({e}). Trying localhost...")

    # ATTEMPT 2: Localhost (VS Code)
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ecommerce_db",
            port=3307
        )
        print("✅ Connected via Localhost (localhost:3307)")
        return conn
    except Exception as e:
        print(f"❌ FAILED to connect to DB: {e}")
        return None

def generate_users(n=25):
    conn = get_db_connection()
    if not conn: return
    
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
    conn = get_db_connection()
    if not conn: return

    cursor = conn.cursor()
    # Check if products already exist to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Products already seeded ({count} found). Skipping.")
        cursor.close()
        conn.close()
        return

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
    
    print("Seeding products...")
    for p in products:
        sql = "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)" 
        cursor.execute(sql, p)
    conn.commit()
    cursor.close()
    conn.close()
    print("Products seeded!")

def generate_orders(n=500):
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor()
    
    # Get valid IDs
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall() 
    
    # Safety Check: If empty, create them first
    if not user_ids:
        print("No users found! Generating some now...")
        generate_users(10)
        # re-fetch
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]

    if not products:
        print("No products found! Seeding catalog...")
        generate_products()
        # re-fetch
        cursor.execute("SELECT product_id, price FROM products")
        products = cursor.fetchall()

    print(f"Generating {n} orders...")
    for _ in range(n):
        user_id = random.choice(user_ids)
        product = random.choice(products)
        product_id = product[0]
        price = float(product[1])
        quantity = random.randint(1, 5)
        status = random.choice(["Pending", "Shipped", "Delivered"])
        total_price = price * quantity
        
        sql = "INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES (%s, %s, %s, %s, %s)"
        val = (user_id, product_id, quantity, total_price, status)
        cursor.execute(sql, val)
        
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {n} Orders generated successfully!")

if __name__ == "__main__":
    # We always run the checks to make sure the DB is ready
    generate_users(100)       # Add a few new users every time
    generate_products()     # Ensure products exist
    generate_orders(500)    # The main event