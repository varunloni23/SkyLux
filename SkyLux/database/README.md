# SkyLux Airlines Database Setup

This directory contains scripts to set up and manage the SkyLux Airlines database.

## Prerequisites

- MySQL Server installed and running
- Python 3.6 or higher
- `mysql-connector-python` package installed

## Files

- `skylux_db_setup.sql`: SQL script to create the database and tables
- `db_connect.py`: Script to connect to MySQL and execute the SQL file
- `sample_data.py`: Script to insert sample data into the database
- `check_db.py`: Utility to check database connection and status
- `setup_db.py`: Master script to run the complete setup process
- `setup.py`: Legacy setup script (to be replaced by the new scripts)

## Database Setup

### Quick Setup

For a complete database setup, run:

```bash
python setup_db.py
```

This will:
1. Create the database and tables
2. Insert sample data
3. Check the database status

### Manual Setup

If you prefer to run each step manually:

1. Create database and tables:
   ```bash
   python db_connect.py
   ```

2. Insert sample data:
   ```bash
   python sample_data.py
   ```

3. Check database status:
   ```bash
   python check_db.py
   ```

## Database Configuration

Database configuration is stored in each script. If you need to change the connection details, update the `DB_CONFIG` variable in each file:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Change this to your MySQL password
    'database': 'skylux_airlines'
}
```

## Tables

The database contains the following tables:

1. `users`: Stores user account information
2. `airports`: Stores airport information
3. `aircraft`: Stores aircraft information
4. `flights`: Stores flight information
5. `bookings`: Stores booking information
6. `cancellations`: Stores cancellation information

## Sample Data

The sample data includes:
- 2 users (admin and regular user)
- 8 airports
- 7 aircraft models
- 20 random flights
- 10 random bookings
- Cancellations for cancelled bookings

## Troubleshooting

If you encounter any issues:

1. Make sure MySQL Server is running
2. Check that the username and password in `DB_CONFIG` are correct
3. Make sure you have the required Python packages installed:
   ```bash
   pip install mysql-connector-python werkzeug
   ```
4. Check the MySQL error logs for more information 