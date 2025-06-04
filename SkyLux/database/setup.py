import mysql.connector
from mysql.connector import Error
import random
import string
import datetime
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Varunloni@12',  # Change this to your MySQL password if needed
}

# Function to create database and tables
def setup_database():
    connection = None
    try:
        # Connect to MySQL server with explicit password
        print("Attempting to connect to MySQL...")
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS skylux_airlines")
            cursor.execute("USE skylux_airlines")
            
            print("Connected to MySQL database, creating tables...")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('user', 'admin') DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Create airports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS airports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(3) NOT NULL UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    city VARCHAR(50) NOT NULL,
                    country VARCHAR(50) NOT NULL,
                    timezone VARCHAR(50) NOT NULL
                )
            """)
            
            # Create aircraft table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aircraft (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    model VARCHAR(50) NOT NULL,
                    capacity INT NOT NULL,
                    first_class_seats INT NOT NULL,
                    business_seats INT NOT NULL,
                    economy_seats INT NOT NULL
                )
            """)
            
            # Create flights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    flight_number VARCHAR(10) NOT NULL UNIQUE,
                    origin_airport_id INT NOT NULL,
                    destination_airport_id INT NOT NULL,
                    aircraft_id INT NOT NULL,
                    departure_time DATETIME NOT NULL,
                    arrival_time DATETIME NOT NULL,
                    economy_price DECIMAL(10, 2) NOT NULL,
                    business_price DECIMAL(10, 2) NOT NULL,
                    first_class_price DECIMAL(10, 2) NOT NULL,
                    status ENUM('Scheduled', 'On Time', 'Delayed', 'Boarding', 'Departed', 'Arrived', 'Cancelled') DEFAULT 'Scheduled',
                    gate VARCHAR(10),
                    terminal VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (origin_airport_id) REFERENCES airports(id),
                    FOREIGN KEY (destination_airport_id) REFERENCES airports(id),
                    FOREIGN KEY (aircraft_id) REFERENCES aircraft(id)
                )
            """)
            
            # Create bookings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    booking_reference VARCHAR(6) NOT NULL UNIQUE,
                    user_id INT,
                    flight_id INT NOT NULL,
                    passenger_name VARCHAR(100) NOT NULL,
                    passenger_email VARCHAR(100) NOT NULL,
                    travel_class ENUM('economy', 'business', 'first') NOT NULL,
                    seat_number VARCHAR(4),
                    booking_status ENUM('Pending', 'Confirmed', 'Cancelled') DEFAULT 'Pending',
                    total_amount DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (flight_id) REFERENCES flights(id)
                )
            """)
            
            # Create cancellations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cancellations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    booking_id INT NOT NULL,
                    cancellation_id VARCHAR(8) NOT NULL UNIQUE,
                    refund_amount DECIMAL(10, 2),
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id)
                )
            """)
            
            print("Tables created successfully!")
            
            # Insert sample data
            insert_sample_data(cursor, connection)
            
            connection.commit()
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# Function to insert sample data
def insert_sample_data(cursor, connection):
    try:
        # Insert admin user
        print("Inserting sample users...")
        admin_password = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """, ('Admin User', 'admin@skylux.com', admin_password, 'admin'))
        
        # Insert sample user
        user_password = generate_password_hash('password123')
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """, ('John Doe', 'john.doe@example.com', user_password, 'user'))
        
        connection.commit()
        
        print("Inserting sample airports...")
        # Insert sample airports
        airports = [
            ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 'America/New_York'),
            ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 'America/Los_Angeles'),
            ('LHR', 'Heathrow Airport', 'London', 'UK', 'Europe/London'),
            ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris'),
            ('DXB', 'Dubai International Airport', 'Dubai', 'UAE', 'Asia/Dubai'),
            ('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore'),
            ('HND', 'Haneda Airport', 'Tokyo', 'Japan', 'Asia/Tokyo'),
            ('SYD', 'Sydney Airport', 'Sydney', 'Australia', 'Australia/Sydney')
        ]
        
        cursor.executemany("""
            INSERT INTO airports (code, name, city, country, timezone)
            VALUES (%s, %s, %s, %s, %s)
        """, airports)
        
        connection.commit()
        
        print("Inserting sample aircraft...")
        # Insert sample aircraft
        aircraft = [
            ('Airbus A320', 180, 0, 20, 160),
            ('Airbus A330', 300, 8, 42, 250),
            ('Airbus A350', 350, 12, 48, 290),
            ('Airbus A380', 525, 14, 76, 435),
            ('Boeing 737', 170, 0, 16, 154),
            ('Boeing 777', 368, 8, 40, 320),
            ('Boeing 787', 330, 8, 42, 280)
        ]
        
        cursor.executemany("""
            INSERT INTO aircraft (model, capacity, first_class_seats, business_seats, economy_seats)
            VALUES (%s, %s, %s, %s, %s)
        """, aircraft)
        
        connection.commit()
        
        # Get airport IDs
        cursor.execute("SELECT id FROM airports")
        airport_ids = [row[0] for row in cursor.fetchall()]
        
        # Get aircraft IDs
        cursor.execute("SELECT id FROM aircraft")
        aircraft_ids = [row[0] for row in cursor.fetchall()]
        
        # Insert sample flights
        flights = []
        flight_numbers = []
        
        for _ in range(20):
            # Generate unique flight number
            while True:
                flight_number = 'SL' + ''.join(random.choices(string.digits, k=3))
                if flight_number not in flight_numbers:
                    flight_numbers.append(flight_number)
                    break
            
            # Select random origin and destination (ensure they're different)
            origin_id, destination_id = random.sample(airport_ids, 2)
            
            # Select random aircraft
            aircraft_id = random.choice(aircraft_ids)
            
            # Generate random departure time in the next 30 days
            days_ahead = random.randint(1, 30)
            departure_time = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
            
            # Flight duration between 2 and 12 hours
            duration_hours = random.randint(2, 12)
            arrival_time = departure_time + datetime.timedelta(hours=duration_hours)
            
            # Generate prices
            economy_price = random.randint(150, 500)
            business_price = economy_price * 2.5
            first_class_price = economy_price * 4
            
            # Flight status
            status = 'Scheduled'
            
            # Gate and terminal
            gate = f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 20)}"
            terminal = str(random.randint(1, 5))
            
            flights.append((
                flight_number,
                origin_id,
                destination_id,
                aircraft_id,
                departure_time,
                arrival_time,
                economy_price,
                business_price,
                first_class_price,
                status,
                gate,
                terminal
            ))
        
        cursor.executemany("""
            INSERT INTO flights (
                flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                departure_time, arrival_time, economy_price, business_price, first_class_price,
                status, gate, terminal
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, flights)
        
        # Get flight IDs
        cursor.execute("SELECT id, economy_price, business_price, first_class_price FROM flights")
        flight_data = [(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()]
        
        # Insert sample bookings
        bookings = []
        booking_references = []
        
        for _ in range(10):
            # Generate unique booking reference
            while True:
                booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if booking_reference not in booking_references:
                    booking_references.append(booking_reference)
                    break
            
            # Select random flight and user
            flight_id, economy_price, business_price, first_class_price = random.choice(flight_data)
            user_id = random.choice([1, 2])  # Admin or sample user
            
            # Passenger details
            passenger_name = 'John Doe' if user_id == 2 else 'Admin User'
            passenger_email = 'john.doe@example.com' if user_id == 2 else 'admin@skylux.com'
            
            # Travel class
            travel_class = random.choice(['economy', 'business', 'first'])
            
            # Seat number
            seat_number = f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}{random.randint(1, 30)}"
            
            # Booking status
            booking_status = random.choice(['Pending', 'Confirmed', 'Cancelled'])
            
            # Total amount based on travel class
            if travel_class == 'economy':
                total_amount = economy_price
            elif travel_class == 'business':
                total_amount = business_price
            else:
                total_amount = first_class_price
            
            bookings.append((
                booking_reference,
                user_id,
                flight_id,
                passenger_name,
                passenger_email,
                travel_class,
                seat_number,
                booking_status,
                total_amount
            ))
        
        cursor.executemany("""
            INSERT INTO bookings (
                booking_reference, user_id, flight_id, passenger_name, passenger_email,
                travel_class, seat_number, booking_status, total_amount
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, bookings)
        
        # Get cancelled booking IDs
        cursor.execute("SELECT id FROM bookings WHERE booking_status = 'Cancelled'")
        cancelled_booking_ids = [row[0] for row in cursor.fetchall()]
        
        # Insert sample cancellations
        cancellations = []
        
        for booking_id in cancelled_booking_ids:
            # Generate unique cancellation ID
            cancellation_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Random refund amount (50-100% of booking amount)
            cursor.execute("SELECT total_amount FROM bookings WHERE id = %s", (booking_id,))
            total_amount = cursor.fetchone()[0]
            refund_percentage = random.uniform(0.5, 1.0)
            refund_amount = float(total_amount) * refund_percentage
            
            # Cancellation reason
            reasons = [
                'Flight schedule changed',
                'Personal emergency',
                'Business trip cancelled',
                'Medical reasons',
                'Weather concerns'
            ]
            reason = random.choice(reasons)
            
            cancellations.append((booking_id, cancellation_id, refund_amount, reason))
        
        cursor.executemany("""
            INSERT INTO cancellations (booking_id, cancellation_id, refund_amount, reason)
            VALUES (%s, %s, %s, %s)
        """, cancellations)
        
        connection.commit()
        print("Sample data inserted successfully!")
        
    except Error as e:
        print(f"Error while inserting sample data: {e}")
        connection.rollback()

if __name__ == "__main__":
    setup_database() 