import mysql.connector
from werkzeug.security import generate_password_hash
import os
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Varunloni@12',  # Change this to your MySQL password
    'database': 'skylux_airlines'
}

def create_admin_user():
    """Create an admin user in the database"""
    # Admin credentials
    admin_name = "Admin User"
    admin_email = "admin@skylux.com"
    admin_password = "admin123"  # This is a simple password for testing purposes
    
    # Hash the password
    hashed_password = generate_password_hash(admin_password)
    
    try:
        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if the admin user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (admin_email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"Admin user '{admin_email}' already exists.")
            cursor.close()
            conn.close()
            return
        
        # Insert the admin user
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """, (admin_name, admin_email, hashed_password, 'admin'))
        
        conn.commit()
        print(f"Admin user '{admin_email}' created successfully with password '{admin_password}'")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Error creating admin user: {err}")
        sys.exit(1)

if __name__ == "__main__":
    create_admin_user() 