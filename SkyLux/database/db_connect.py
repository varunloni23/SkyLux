import mysql.connector
from mysql.connector import Error
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Varunloni@12',  # Change this to your MySQL password if needed
}

def connect_mysql():
    """Connect to MySQL server and return connection"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        if connection.is_connected():
            print(f"Connected to MySQL server (Version: {connection.get_server_info()})")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
def execute_sql_file(connection, file_path):
    """Execute SQL commands from a file"""
    try:
        cursor = connection.cursor()
        
        # Read SQL file
        with open(file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        
        # Split SQL script into individual commands
        # This simple split won't work for all SQL files but works for our case
        sql_commands = sql_script.split(';')
        
        # Execute each command
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
                print(f"Executed: {command[:50]}...")
        
        connection.commit()
        print("SQL file executed successfully")
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE 'skylux_airlines'")
        if cursor.fetchone():
            cursor.execute("USE skylux_airlines")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Tables in skylux_airlines database:")
            for table in tables:
                print(f"- {table[0]}")
        
    except Error as e:
        print(f"Error executing SQL file: {e}")
    finally:
        if cursor:
            cursor.close()

def main():
    # Get the absolute path to the SQL file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_dir, 'skylux_db_setup.sql')
    
    # Check if SQL file exists
    if not os.path.exists(sql_file_path):
        print(f"SQL file not found: {sql_file_path}")
        return
    
    # Connect to MySQL
    connection = connect_mysql()
    if connection:
        try:
            # Execute SQL file
            execute_sql_file(connection, sql_file_path)
        finally:
            if connection.is_connected():
                connection.close()
                print("MySQL connection closed")

if __name__ == "__main__":
    main() 