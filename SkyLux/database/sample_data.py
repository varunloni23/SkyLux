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
    'password': 'Varunloni@12',  # Change this to your MySQL password
    'database': 'skylux_airlines'
}

def get_db_connection():
    """Connect to MySQL database and return connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print(f"Connected to MySQL database: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def check_if_data_exists(cursor, table):
    """Check if a table already has data"""
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    return count > 0

def insert_sample_data():
    """Insert sample data into the database"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        tables_with_data = []
        for table in ['users', 'airports', 'aircraft', 'flights', 'bookings', 'cancellations']:
            if check_if_data_exists(cursor, table):
                tables_with_data.append(table)
        
        if tables_with_data:
            print(f"The following tables already have data: {', '.join(tables_with_data)}")
            choice = input("Do you want to proceed and add more data? This might cause errors with unique constraints. (y/n): ").lower()
            if choice != 'y':
                print("Sample data insertion cancelled.")
                return
        
        # Insert admin user
        print("Inserting sample users...")
        try:
            admin_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('Admin User', 'admin@skylux.com', admin_password, 'admin'))
            print("  - Admin user inserted")
        except Error as e:
            if "Duplicate entry" in str(e):
                print("  - Admin user already exists, skipping")
            else:
                raise e
        
        # Insert sample user
        try:
            user_password = generate_password_hash('password123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('John Doe', 'john.doe@example.com', user_password, 'user'))
            print("  - Sample user inserted")
        except Error as e:
            if "Duplicate entry" in str(e):
                print("  - Sample user already exists, skipping")
            else:
                raise e
        
        connection.commit()
        
        # Insert sample airports
        print("Inserting sample airports...")
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
        
        for airport in airports:
            try:
                cursor.execute("""
                    INSERT INTO airports (code, name, city, country, timezone)
                    VALUES (%s, %s, %s, %s, %s)
                """, airport)
                print(f"  - Airport {airport[0]} inserted")
            except Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  - Airport {airport[0]} already exists, skipping")
                else:
                    raise e
        
        connection.commit()
        
        # Insert sample aircraft
        print("Inserting sample aircraft...")
        aircraft = [
            ('Airbus A320', 180, 0, 20, 160),
            ('Airbus A330', 300, 8, 42, 250),
            ('Airbus A350', 350, 12, 48, 290),
            ('Airbus A380', 525, 14, 76, 435),
            ('Boeing 737', 170, 0, 16, 154),
            ('Boeing 777', 368, 8, 40, 320),
            ('Boeing 787', 330, 8, 42, 280)
        ]
        
        for plane in aircraft:
            try:
                cursor.execute("""
                    INSERT INTO aircraft (model, capacity, first_class_seats, business_seats, economy_seats)
                    VALUES (%s, %s, %s, %s, %s)
                """, plane)
                print(f"  - Aircraft {plane[0]} inserted")
            except Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  - Aircraft {plane[0]} already exists, skipping")
                else:
                    raise e
        
        connection.commit()
        
        # Check if we have enough airports and aircraft to generate flights
        cursor.execute("SELECT COUNT(*) FROM airports")
        airport_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aircraft")
        aircraft_count = cursor.fetchone()[0]
        
        if airport_count < 2 or aircraft_count < 1:
            print("Not enough airports or aircraft to generate flights. Skipping flight generation.")
            return
        
        # Get airport IDs
        cursor.execute("SELECT id FROM airports")
        airport_ids = [row[0] for row in cursor.fetchall()]
        
        # Get aircraft IDs
        cursor.execute("SELECT id FROM aircraft")
        aircraft_ids = [row[0] for row in cursor.fetchall()]
        
        # Insert sample flights
        print("Inserting sample flights...")
        
        # Get existing flight numbers to avoid duplicates
        cursor.execute("SELECT flight_number FROM flights")
        existing_flight_numbers = [row[0] for row in cursor.fetchall()]
        
        # Generate new unique flight numbers
        flight_numbers = []
        while len(flight_numbers) < 5:  # Reduced from 20 to 5 to avoid too many flights
            flight_number = 'SL' + ''.join(random.choices(string.digits, k=3))
            if flight_number not in existing_flight_numbers and flight_number not in flight_numbers:
                flight_numbers.append(flight_number)
        
        # Generate and insert flights one by one
        flights_added = 0
        for flight_number in flight_numbers:
            try:
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
                
                cursor.execute("""
                    INSERT INTO flights (
                        flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                        departure_time, arrival_time, economy_price, business_price, first_class_price,
                        status, gate, terminal
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
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
                
                flights_added += 1
                print(f"  - Flight {flight_number} inserted")
                
            except Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  - Flight {flight_number} already exists, skipping")
                else:
                    print(f"  - Error adding flight {flight_number}: {e}")
        
        if flights_added == 0:
            print("No new flights were added. Skipping bookings and cancellations.")
            return
            
        connection.commit()
        
        # Get flight IDs
        cursor.execute("SELECT id, economy_price, business_price, first_class_price FROM flights")
        flight_data = [(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()]
        
        # Insert sample bookings
        print("Inserting sample bookings...")
        
        # Get existing booking references to avoid duplicates
        cursor.execute("SELECT booking_reference FROM bookings")
        existing_booking_refs = [row[0] for row in cursor.fetchall()]
        
        # Generate unique booking references
        booking_references = []
        while len(booking_references) < 3:  # Reduced from 10 to 3
            booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if booking_reference not in existing_booking_refs and booking_reference not in booking_references:
                booking_references.append(booking_reference)
        
        # Insert bookings one by one
        bookings_added = 0
        cancelled_bookings = []
        
        for booking_reference in booking_references:
            try:
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
                
                cursor.execute("""
                    INSERT INTO bookings (
                        booking_reference, user_id, flight_id, passenger_name, passenger_email,
                        travel_class, seat_number, booking_status, total_amount
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
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
                
                # Store ID and amount for cancelled bookings
                if booking_status == 'Cancelled':
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    booking_id = cursor.fetchone()[0]
                    cancelled_bookings.append((booking_id, total_amount))
                
                bookings_added += 1
                print(f"  - Booking {booking_reference} inserted")
                
            except Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  - Booking {booking_reference} already exists, skipping")
                else:
                    print(f"  - Error adding booking {booking_reference}: {e}")
        
        connection.commit()
        
        # If no new bookings were added or none were cancelled, skip cancellations
        if bookings_added == 0 or not cancelled_bookings:
            print("No new cancelled bookings. Skipping cancellations.")
            return
        
        # Insert sample cancellations
        print("Inserting sample cancellations...")
        
        # Get existing cancellation IDs
        cursor.execute("SELECT cancellation_id FROM cancellations")
        existing_cancellation_ids = [row[0] for row in cursor.fetchall()]
        
        # Process each cancelled booking
        for booking_id, total_amount in cancelled_bookings:
            # Check if cancellation already exists for this booking
            cursor.execute("SELECT COUNT(*) FROM cancellations WHERE booking_id = %s", (booking_id,))
            if cursor.fetchone()[0] > 0:
                print(f"  - Cancellation for booking ID {booking_id} already exists, skipping")
                continue
                
            # Generate unique cancellation ID
            while True:
                cancellation_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if cancellation_id not in existing_cancellation_ids:
                    break
            
            # Random refund amount (50-100% of booking amount)
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
            
            try:
                cursor.execute("""
                    INSERT INTO cancellations (booking_id, cancellation_id, refund_amount, reason)
                    VALUES (%s, %s, %s, %s)
                """, (booking_id, cancellation_id, refund_amount, reason))
                
                print(f"  - Cancellation {cancellation_id} for booking ID {booking_id} inserted")
                
            except Error as e:
                print(f"  - Error adding cancellation for booking ID {booking_id}: {e}")
        
        connection.commit()
        print("Sample data insertion completed!")
        
    except Error as e:
        print(f"Error while inserting sample data: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    insert_sample_data() 