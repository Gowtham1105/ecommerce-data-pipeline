import mysql.connector
import time

# Database Config
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'ecommerce_db',
    'port': 3307
}

def create_tables():
    # Retry logic: Wait for MySQL to be ready (useful if docker just started)
    retries = 5
    while retries > 0:
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            print("Connected to MySQL!")
            break
        except mysql.connector.Error as err:
            print(f"MySQL not ready yet... retrying in 5s. ({err})")
            time.sleep(5)
            retries -= 1
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        address VARCHAR(200),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        category VARCHAR(50),
        price DECIMAL(10, 2)
    )
    """)
    
    # 3. Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_id INT,
        quantity INT,
        total_price DECIMAL(10, 2),
        status VARCHAR(20) DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    print("All tables created successfully (Schema initialized).")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()