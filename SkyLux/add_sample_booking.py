import mysql.connector
import random
import string
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Varunloni@12',  # Change this to your MySQL password
    'database': 'skylux_airlines'
}

def add_sample_booking():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # First, ensure we have a user
        cursor.execute("SELECT id FROM users WHERE name = 'Vedha Homkar' LIMIT 1")
        user = cursor.fetchone()
        
        user_id = None
        if not user:
            # Create the user
            password_hash = generate_password_hash('password123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('Vedha Homkar', 'vedha@example.com', password_hash, 'user'))
            conn.commit()
            user_id = cursor.lastrowid
            print(f"Created new user with ID {user_id}")
        else:
            user_id = user[0]
            print(f"Using existing user with ID {user_id}")
        
        # Check if there are any flights
        cursor.execute("SELECT id FROM flights LIMIT 1")
        flight_id = cursor.fetchone()
        
        if not flight_id:
            print("No flights found. Creating a sample flight...")
            # Create a sample flight
            cursor.execute("SELECT id FROM airports WHERE code = 'JFK' LIMIT 1")
            jfk_id = cursor.fetchone()
            if not jfk_id:
                cursor.execute("""
                    INSERT INTO airports (code, name, city, country, timezone)
                    VALUES ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 'America/New_York')
                """)
                jfk_id = [cursor.lastrowid]
            
            cursor.execute("SELECT id FROM airports WHERE code = 'LAX' LIMIT 1")
            lax_id = cursor.fetchone()
            if not lax_id:
                cursor.execute("""
                    INSERT INTO airports (code, name, city, country, timezone)
                    VALUES ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 'America/Los_Angeles')
                """)
                lax_id = [cursor.lastrowid]
            
            cursor.execute("SELECT id FROM aircraft WHERE model = 'Boeing 737' LIMIT 1")
            aircraft_id = cursor.fetchone()
            if not aircraft_id:
                cursor.execute("""
                    INSERT INTO aircraft (model, capacity, first_class_seats, business_seats, economy_seats)
                    VALUES ('Boeing 737', 170, 0, 16, 154)
                """)
                aircraft_id = [cursor.lastrowid]
            
            # Create the flight
            flight_number = 'SL' + ''.join(random.choices(string.digits, k=3))
            cursor.execute("""
                INSERT INTO flights (
                    flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                    departure_time, arrival_time, economy_price, business_price, first_class_price,
                    status, gate, terminal
                ) VALUES (%s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 5 HOUR), 200, 500, 1000, 'Scheduled', 'A1', '1')
            """, (flight_number, jfk_id[0], lax_id[0], aircraft_id[0]))
            
            conn.commit()
            flight_id = [cursor.lastrowid]
            print(f"Created sample flight {flight_number} with ID {flight_id[0]}")
        
        # Check if booking already exists for this user and flight
        cursor.execute("""
            SELECT id FROM bookings 
            WHERE passenger_name = %s AND flight_id = %s LIMIT 1
        """, ('Vedha Homkar', flight_id[0]))
        existing_booking = cursor.fetchone()
        
        if existing_booking:
            print(f"Booking already exists with ID {existing_booking[0]}")
            return
        
        # Generate a random booking reference
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Insert sample booking
        cursor.execute("""
            INSERT INTO bookings (
                booking_reference, passenger_name, passenger_email, flight_id, 
                travel_class, seat_number, total_amount, booking_status, user_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            booking_ref, 
            'Vedha Homkar', 
            'vedha@example.com', 
            flight_id[0], 
            'business', 
            '12A', 
            500.00, 
            'Confirmed',
            user_id
        ))
        
        conn.commit()
        print(f"Sample booking '{booking_ref}' added successfully for Vedha Homkar!")
        
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    add_sample_booking() 