import os
import sys
import time

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the header"""
    clear_screen()
    print("=" * 50)
    print("  SkyLux Airlines Database Setup")
    print("=" * 50)
    print()

def main():
    """Main function to set up the database"""
    print_header()
    
    print("This script will set up the SkyLux Airlines database.")
    print("It will create the database, tables, and insert sample data.")
    print()
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure we're in the database directory
    os.chdir(current_dir)
    
    # Check if the SQL file exists
    if not os.path.exists('skylux_db_setup.sql'):
        print("Error: skylux_db_setup.sql file not found!")
        return
    
    # Prompt the user to continue
    try:
        input("Press Enter to continue or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        return
    
    # Step 1: Execute SQL file to create database and tables
    print_header()
    print("Step 1/3: Creating database and tables...")
    print()
    
    try:
        from db_connect import main as db_connect_main
        db_connect_main()
    except Exception as e:
        print(f"Error during database creation: {e}")
        return
    
    print()
    print("Database and tables created successfully!")
    time.sleep(2)
    
    # Step 2: Insert sample data
    print_header()
    print("Step 2/3: Inserting sample data...")
    print()
    
    try:
        from sample_data import insert_sample_data
        insert_sample_data()
    except Exception as e:
        print(f"Error during sample data insertion: {e}")
        return
    
    print()
    print("Sample data inserted successfully!")
    time.sleep(2)
    
    # Step 3: Check database status
    print_header()
    print("Step 3/3: Checking database status...")
    print()
    
    try:
        from check_db import check_database_connection
        check_database_connection()
    except Exception as e:
        print(f"Error during database check: {e}")
        return
    
    print()
    print("=" * 50)
    print("  Database setup completed successfully!")
    print("=" * 50)
    print()
    print("You can now run the Flask application with:")
    print("  python app.py")
    print()

if __name__ == "__main__":
    main() 