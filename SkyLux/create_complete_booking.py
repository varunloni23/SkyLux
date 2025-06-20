import mysql.connector
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

def create_complete_booking():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("Creating complete booking with all required data...")
        
        # Step 1: Make sure we have an aircraft
        cursor.execute("SELECT id FROM aircraft LIMIT 1")
        aircraft = cursor.fetchone()
        
        if not aircraft:
            print("Creating aircraft...")
            cursor.execute("""
                INSERT INTO aircraft (model, capacity, first_class_seats, business_seats, economy_seats)
                VALUES ('Boeing 787', 330, 8, 42, 280)
            """)
            conn.commit()
            aircraft_id = cursor.lastrowid
            print(f"Created aircraft with ID {aircraft_id}")
        else:
            aircraft_id = aircraft['id']
            print(f"Using existing aircraft with ID {aircraft_id}")
        
        # Step 2: Make sure we have origin and destination airports
        cursor.execute("SELECT id, code, city FROM airports ORDER BY id LIMIT 2")
        airports = cursor.fetchall()
        
        if len(airports) < 2:
            print("Creating airports...")
            # Create origin airport
            cursor.execute("""
                INSERT INTO airports (code, name, city, country, timezone)
                VALUES ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 'America/New_York')
            """)
            origin_id = cursor.lastrowid
            
            # Create destination airport
            cursor.execute("""
                INSERT INTO airports (code, name, city, country, timezone)
                VALUES ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 'America/Los_Angeles')
            """)
            destination_id = cursor.lastrowid
            
            conn.commit()
            print(f"Created airports: JFK (ID: {origin_id}) and LAX (ID: {destination_id})")
        else:
            origin_id = airports[0]['id']
            destination_id = airports[1]['id']
            print(f"Using existing airports: {airports[0]['code']} (ID: {origin_id}) and {airports[1]['code']} (ID: {destination_id})")
        
        # Step 3: Create a flight
        flight_number = 'SL' + ''.join(random.choices(string.digits, k=3))
        
        # Departure time in 7 days
        departure_time = datetime.datetime.now() + datetime.timedelta(days=7)
        # Arrival time 5 hours later
        arrival_time = departure_time + datetime.timedelta(hours=5)
        
        print(f"Creating flight {flight_number} from airport {origin_id} to {destination_id}...")
        
        cursor.execute("""
            INSERT INTO flights (
                flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                departure_time, arrival_time, economy_price, business_price, first_class_price,
                status, gate, terminal
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            flight_number, 
            origin_id, 
            destination_id, 
            aircraft_id,
            departure_time,
            arrival_time,
            200.00,  # economy
            500.00,  # business
            1000.00,  # first class
            'Scheduled',
            'A10',
            '3'
        ))
        
        conn.commit()
        flight_id = cursor.lastrowid
        print(f"Created flight with ID {flight_id}")
        
        # Step 4: Make sure we have a user
        user_name = "Vedha Homkar"
        cursor.execute("SELECT id FROM users WHERE name = %s", (user_name,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Creating user {user_name}...")
            password_hash = generate_password_hash('password123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (user_name, 'vedha@example.com', password_hash, 'user'))
            conn.commit()
            user_id = cursor.lastrowid
            print(f"Created user with ID {user_id}")
        else:
            user_id = user['id']
            print(f"Using existing user with ID {user_id}")
        
        # Step 5: Create the booking
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        travel_class = random.choice(['economy', 'business', 'first'])
        if travel_class == 'economy':
            price = 200.00
            seat = f"{random.randint(20, 40)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
        elif travel_class == 'business':
            price = 500.00
            seat = f"{random.randint(10, 19)}{random.choice(['A', 'C', 'D', 'F'])}"
        else:  # first class
            price = 1000.00
            seat = f"{random.randint(1, 9)}{random.choice(['A', 'F'])}"
        
        print(f"Creating booking {booking_ref} for flight {flight_number}...")
        
        cursor.execute("""
            INSERT INTO bookings (
                booking_reference, passenger_name, passenger_email, flight_id,
                travel_class, seat_number, total_amount, booking_status, user_id,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            booking_ref,
            user_name,
            'vedha@example.com',
            flight_id,
            travel_class,
            seat,
            price,
            'Confirmed',
            user_id,
            datetime.datetime.now()
        ))
        
        conn.commit()
        booking_id = cursor.lastrowid
        
        print(f"""
        =======================================================
        Successfully created booking:
        Booking ID: {booking_id}
        Reference: {booking_ref}
        Passenger: {user_name}
        Flight: {flight_number}
        From: New York (JFK) to Los Angeles (LAX)
        Class: {travel_class.capitalize()}
        Seat: {seat}
        Price: ${price:.2f}
        Status: Confirmed
        =======================================================
        """)
        
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    create_complete_booking() 