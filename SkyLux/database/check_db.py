import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Varunloni@12',  # Change this to your MySQL password
    'database': 'skylux_airlines'
}

def check_database_connection():
    """Check the database connection and status"""
    try:
        # Connect to the database
        print(f"Attempting to connect to database {DB_CONFIG['database']}...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            
            # Get database info
            cursor.execute("SELECT DATABASE()")
            database_name = cursor.fetchone()[0]
            print(f"Connected to database: {database_name}")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\nTables in {database_name} database:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")
                
                # Get record count for each table
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - Records: {count}")
                
                # Show table structure
                cursor.execute(f"DESCRIBE {table[0]}")
                columns = cursor.fetchall()
                print(f"   - Columns:")
                for column in columns:
                    print(f"     * {column[0]} - {column[1]}")
                print()
                
            return True
            
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    check_database_connection() 