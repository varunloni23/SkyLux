from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import random
import string
import datetime
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Import database connection function
from database.db_connect import connect_mysql

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Varunloni@12',  # Change this to your MySQL password if needed
    'database': 'skylux_airlines'
}

# Helper function to get database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Generate a random booking reference
def generate_booking_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Generate a random flight number
def generate_flight_number():
    return 'SL' + ''.join(random.choices(string.digits, k=3))

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    # Generate some popular routes for direct booking
    popular_routes = [
        {
            'from': 'New York',
            'to': 'London',
            'departure_date': (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d'),
            'flights': generate_sample_flights('New York', 'London', (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d'))
        },
        {
            'from': 'London',
            'to': 'Paris',
            'departure_date': (datetime.datetime.now() + datetime.timedelta(days=5)).strftime('%Y-%m-%d'),
            'flights': generate_sample_flights('London', 'Paris', (datetime.datetime.now() + datetime.timedelta(days=5)).strftime('%Y-%m-%d'))
        },
        {
            'from': 'Tokyo',
            'to': 'Singapore',
            'departure_date': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
            'flights': generate_sample_flights('Tokyo', 'Singapore', (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
        }
    ]
    
    # Store the flight data in the session
    session['popular_routes'] = popular_routes
    
    return render_template('index.html', popular_routes=popular_routes)

@app.route('/api/search-flights', methods=['POST'])
def search_flights():
    data = request.json
    
    # Validate required fields
    required_fields = ['from', 'to', 'departure', 'passengers', 'class']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'})
    
    # In a real application, we would search the database for flights
    # For this demo, we'll generate some sample flights
    
    # Generate a search ID to retrieve results later
    search_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    # Store search parameters in session
    session[f'search_{search_id}'] = {
        'from': data['from'],
        'to': data['to'],
        'departure': data['departure'],
        'return': data.get('return'),
        'passengers': data['passengers'],
        'class': data['class'],
        'outbound_flights': generate_sample_flights(data['from'], data['to'], data['departure']),
        'return_flights': generate_sample_flights(data['to'], data['from'], data.get('return')) if data.get('return') else []
    }
    
    return jsonify({
        'success': True,
        'search_id': search_id
    })

def generate_sample_flights(origin, destination, date_str):
    if not date_str:
        return []
    
    flights = []
    airlines = ['SkyLux', 'AirBlue', 'SunWings', 'StarJet']
    statuses = ['On Time', 'Delayed', 'Boarding', 'Scheduled']
    
    # Parse the date string
    flight_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Generate 3-5 random flights
    num_flights = random.randint(3, 5)
    
    for _ in range(num_flights):
        # Random departure time between 6 AM and 10 PM
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        
        # Flight duration between 1 and 5 hours
        duration_hours = random.randint(1, 5)
        duration_minutes = random.choice([0, 15, 30, 45])
        
        # Calculate departure and arrival times
        departure_time = datetime.datetime.combine(
            flight_date, 
            datetime.time(departure_hour, departure_minute)
        )
        
        arrival_time = departure_time + datetime.timedelta(
            hours=duration_hours, 
            minutes=duration_minutes
        )
        
        # Generate price (more expensive for business and first class)
        base_price = random.randint(150, 500)
        
        flight = {
            'flight_number': generate_flight_number(),
            'airline': random.choice(airlines),
            'departure_city': origin,
            'arrival_city': destination,
            'departure_time': departure_time.isoformat(),
            'arrival_time': arrival_time.isoformat(),
            'duration': f"{duration_hours}h {duration_minutes}m",
            'price': {
                'economy': base_price,
                'business': base_price * 2.5,
                'first': base_price * 4
            },
            'available_seats': random.randint(5, 50),
            'status': random.choice(statuses),
            'aircraft': f"Airbus A{random.choice(['320', '330', '350', '380'])}",
            'gate': f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 20)}",
            'terminal': str(random.randint(1, 5))
        }
        
        flights.append(flight)
    
    # Sort by departure time
    flights.sort(key=lambda x: x['departure_time'])
    
    return flights

@app.route('/flight-results')
def flight_results():
    search_id = request.args.get('search_id')
    
    if not search_id or f'search_{search_id}' not in session:
        return redirect(url_for('index'))
    
    search_data = session[f'search_{search_id}']
    
    return render_template(
        'flight_results.html',
        search_data=search_data,
        search_id=search_id
    )

@app.route('/api/flight-status/<flight_number>')
def flight_status(flight_number):
    # In a real application, we would query the database for the flight
    # For this demo, we'll generate a sample flight if the flight number starts with SL
    
    if not flight_number.startswith('SL'):
        return jsonify({'success': False, 'error': 'Flight not found'})
    
    # Generate random flight data
    flight = {
        'flight_number': flight_number,
        'departure_city': random.choice(['New York', 'London', 'Tokyo', 'Dubai', 'Paris']),
        'arrival_city': random.choice(['Los Angeles', 'Singapore', 'Sydney', 'Rome', 'Berlin']),
        'departure_time': (datetime.datetime.now() + datetime.timedelta(hours=random.randint(1, 24))).isoformat(),
        'arrival_time': (datetime.datetime.now() + datetime.timedelta(hours=random.randint(3, 30))).isoformat(),
        'status': random.choice(['On Time', 'Delayed', 'Boarding', 'Departed', 'Arrived']),
        'gate': f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 20)}",
        'terminal': str(random.randint(1, 5))
    }
    
    return jsonify({
        'success': True,
        'flight': flight
    })

@app.route('/api/booking/<booking_ref>')
def get_booking(booking_ref):
    email = request.args.get('email')
    
    # In a real application, we would query the database for the booking
    # For this demo, we'll use session data if available
    
    if len(booking_ref) != 6 or not all(c in string.ascii_uppercase + string.digits for c in booking_ref):
        return jsonify({'success': False, 'error': 'Invalid booking reference'})
    
    # Use user's name from session if available
    user_name = session.get('user_name', 'John Doe')
    
    # Generate random booking data
    booking = {
        'booking_reference': booking_ref,
        'passenger_name': user_name,
        'passenger_email': email or 'user@example.com',
        'departure_city': random.choice(['New York', 'London', 'Tokyo', 'Dubai', 'Paris']),
        'arrival_city': random.choice(['Los Angeles', 'Singapore', 'Sydney', 'Rome', 'Berlin']),
        'departure_time': (datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30))).isoformat(),
        'booking_status': random.choice(['Confirmed', 'Pending', 'Cancelled']),
        'total_amount': f"${random.randint(200, 1500)}.00",
        'gate': f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 20)}",
        'terminal': str(random.randint(1, 5))
    }
    
    # If email is provided, check if it matches
    if email and email.lower() != booking['passenger_email'].lower():
        return jsonify({'success': False, 'error': 'Email does not match booking records'})
    
    return jsonify({
        'success': True,
        'booking': booking
    })

@app.route('/api/booking/<booking_ref>/cancel', methods=['POST'])
def cancel_booking(booking_ref):
    # In a real application, we would update the booking status in the database
    # For this demo, we'll just return a success response
    
    if len(booking_ref) != 6 or not all(c in string.ascii_uppercase + string.digits for c in booking_ref):
        return jsonify({'success': False, 'error': 'Invalid booking reference'})
    
    # Generate a cancellation ID
    cancellation_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    return jsonify({
        'success': True,
        'message': 'Booking cancelled successfully',
        'cancellation_id': cancellation_id
    })

@app.route('/modify-booking/<booking_ref>')
def modify_booking(booking_ref):
    # In a real application, we would fetch the booking details from the database
    # For this demo, we'll use the user's session data if available
    
    # Get user details from session
    user_name = session.get('user_name', 'John Doe')  # Default to John Doe if not logged in
    user_email = None
    
    # If we're logged in, try to get the user's email from the database
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT email FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if user:
                    user_email = user['email']
            except Exception as e:
                print(f"Error fetching user email: {e}")
            finally:
                cursor.close()
                conn.close()
    
    return render_template('modify_booking.html', 
                          booking_ref=booking_ref, 
                          user_name=user_name,
                          user_email=user_email)

@app.route('/booking')
def booking():
    # Get flight details from query parameters
    flight_number = request.args.get('flight')
    travel_class = request.args.get('class')
    search_id = request.args.get('search_id')
    return_flight = request.args.get('return')
    
    if not flight_number or not travel_class:
        return redirect(url_for('index'))
    
    # Handle direct bookings from homepage
    if search_id == 'direct':
        # Find the flight in the popular routes
        selected_flight = None
        popular_routes = session.get('popular_routes', [])
        
        for route in popular_routes:
            for flight in route['flights']:
                if flight['flight_number'] == flight_number:
                    selected_flight = flight
                    
                    # Create a search data structure similar to regular searches
                    search_data = {
                        'from': route['from'],
                        'to': route['to'],
                        'departure': route['departure_date'],
                        'return': None,
                        'passengers': '1',
                        'class': travel_class,
                        'outbound_flights': [selected_flight],
                        'return_flights': []
                    }
                    
                    # Store in session
                    direct_search_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                    session[f'search_{direct_search_id}'] = search_data
                    
                    # Update search_id for the template
                    search_id = direct_search_id
                    break
            
            if selected_flight:
                break
                
        if not selected_flight:
            return redirect(url_for('index'))
    else:
        # Regular search flow
        # Get search data from session
        search_data = session.get(f'search_{search_id}')
        if not search_data:
            return redirect(url_for('index'))
        
        # Find the selected flight in the search results
        selected_flight = None
        for flight in search_data['outbound_flights']:
            if flight['flight_number'] == flight_number:
                selected_flight = flight
                break
    
    # Find return flight if provided
    selected_return_flight = None
    if return_flight and search_data.get('return_flights'):
        for flight in search_data['return_flights']:
            if flight['flight_number'] == return_flight:
                selected_return_flight = flight
                break
    
    # In a real application, we would store the booking in the database
    # For this demo, we'll just generate a booking reference
    booking_ref = generate_booking_reference()
    
    return render_template(
        'booking.html',
        booking_ref=booking_ref,
        flight=selected_flight,
        return_flight=selected_return_flight,
        travel_class=travel_class,
        search_data=search_data
    )

@app.route('/complete-booking', methods=['POST'])
def complete_booking():
    # Get form data
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    phone = request.form.get('phone')
    dob = request.form.get('dob')
    nationality = request.form.get('nationality')
    
    # Get flight data
    flight_number = request.form.get('flight_number')
    travel_class = request.form.get('travel_class')
    total_amount = float(request.form.get('total_amount'))
    booking_ref = request.form.get('booking_ref')
    
    # If user is logged in, use their name
    if 'user_name' in session:
        passenger_name = session['user_name']
    else:
        passenger_name = f"{first_name} {last_name}"
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # First, get the flight ID from the flight number
            cursor.execute("SELECT id FROM flights WHERE flight_number = %s", (flight_number,))
            flight_result = cursor.fetchone()
            
            if not flight_result:
                # If flight doesn't exist, create a temporary one for demo
                cursor.execute("""
                    INSERT INTO flights (flight_number, origin_airport_id, destination_airport_id, aircraft_id, 
                                        departure_time, arrival_time, economy_price, business_price, first_class_price, status)
                    VALUES (%s, 1, 2, 1, NOW(), DATE_ADD(NOW(), INTERVAL 5 HOUR), 200, 500, 1000, 'Scheduled')
                """, (flight_number,))
                conn.commit()
                flight_id = cursor.lastrowid
            else:
                flight_id = flight_result[0]
            
            # Generate a random seat based on class
            if travel_class == 'economy':
                seat_prefix = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
                seat_row = random.randint(20, 40)
            elif travel_class == 'business':
                seat_prefix = random.choice(['A', 'D', 'F'])
                seat_row = random.randint(10, 19)
            else:  # first class
                seat_prefix = random.choice(['A', 'F'])
                seat_row = random.randint(1, 9)
            
            seat_number = f"{seat_row}{seat_prefix}"
            
            # Insert booking
            cursor.execute("""
                INSERT INTO bookings (booking_reference, passenger_name, passenger_email, flight_id, 
                                     travel_class, seat_number, total_amount, booking_status, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                booking_ref, 
                passenger_name, 
                email, 
                flight_id, 
                travel_class, 
                seat_number, 
                total_amount, 
                'Confirmed',
                session.get('user_id')
            ))
            
            conn.commit()
            
            # Create booking details for the confirmation page
            booking = {
                'booking_reference': booking_ref,
                'passenger_name': passenger_name,
                'email': email,
                'phone': phone,
                'flight_number': flight_number,
                'travel_class': travel_class,
                'seat_number': seat_number,
                'total_amount': total_amount,
                'departure_city': 'Sample City',
                'arrival_city': 'Destination City',
                'departure_time': datetime.datetime.now() + datetime.timedelta(days=7),
                'arrival_time': datetime.datetime.now() + datetime.timedelta(days=7, hours=2),
                'aircraft': 'Airbus A320',
                'departure_code': 'SMP',
                'arrival_code': 'DST',
                'booking_status': 'Confirmed'
            }
            
            # Store in session for future reference
            session['booking_details'] = booking
            
            print(f"Rendering booking confirmation page for booking: {booking_ref}")
            
            # Directly render the confirmation page instead of redirecting
            return render_template('booking_confirmation.html', booking=booking)
            
        except Exception as e:
            print(f"Error saving booking: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    # If something went wrong, redirect to the homepage
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Get user from database
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    # Set session variables
                    session['user_id'] = user['id']
                    session['user_role'] = user['role']
                    session['user_name'] = user['name']
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('index'))
                
                return render_template('login.html', error='Invalid email or password')
                
            except Exception as e:
                print(f"Error during login: {e}")
            finally:
                cursor.close()
                conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get counts for dashboard stats
            cursor.execute("SELECT COUNT(*) as total FROM bookings")
            total_bookings = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM flights WHERE status != 'Cancelled'")
            active_flights = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            cursor.execute("SELECT SUM(total_amount) as total FROM bookings")
            result = cursor.fetchone()
            total_revenue = result['total'] if result['total'] else 0
            
            # Get recent bookings with error handling
            try:
                cursor.execute("""
                    SELECT b.id, b.booking_reference, b.passenger_name, f.flight_number, 
                           a1.city as departure_city, a2.city as arrival_city, 
                           f.departure_time, b.total_amount, b.booking_status
                    FROM bookings b
                    JOIN flights f ON b.flight_id = f.id
                    JOIN airports a1 ON f.origin_airport_id = a1.id
                    JOIN airports a2 ON f.destination_airport_id = a2.id
                    ORDER BY b.created_at DESC
                    LIMIT 5
                """)
                recent_bookings = cursor.fetchall()
                print(f"Found {len(recent_bookings)} recent bookings")
                
                # Debug: print all bookings
                for booking in recent_bookings:
                    print(f"Booking: {booking['booking_reference']} - {booking['passenger_name']}")
                
            except Exception as e:
                print(f"Error fetching recent bookings: {e}")
                # Fallback query if there's an issue with the JOIN
                cursor.execute("""
                    SELECT id, booking_reference, passenger_name, flight_id, 
                           travel_class, total_amount, booking_status, created_at
                    FROM bookings
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                recent_bookings = cursor.fetchall()
                
                # If we have bookings but with incomplete flight data
                for booking in recent_bookings:
                    # Add missing fields to avoid template errors
                    if 'flight_number' not in booking:
                        booking['flight_number'] = 'Unknown'
                    if 'departure_city' not in booking:
                        booking['departure_city'] = 'Unknown'
                    if 'arrival_city' not in booking:
                        booking['arrival_city'] = 'Unknown'
                    if 'departure_time' not in booking:
                        booking['departure_time'] = datetime.datetime.now()
            
            # Get today's flights
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT f.id, f.flight_number, a1.city as departure_city, a2.city as arrival_city,
                       f.departure_time, f.arrival_time, ac.model as aircraft, f.status
                FROM flights f
                JOIN airports a1 ON f.origin_airport_id = a1.id
                JOIN airports a2 ON f.destination_airport_id = a2.id
                JOIN aircraft ac ON f.aircraft_id = ac.id
                WHERE DATE(f.departure_time) = %s
                ORDER BY f.departure_time
                LIMIT 5
            """, (today,))
            todays_flights = cursor.fetchall()
            
            return render_template(
                'admin_dashboard.html', 
                total_bookings=total_bookings,
                active_flights=active_flights,
                total_users=total_users,
                total_revenue=total_revenue,
                recent_bookings=recent_bookings,
                todays_flights=todays_flights
            )
        except Exception as e:
            print(f"Error fetching admin dashboard data: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin_dashboard.html')

@app.route('/admin/flights')
@login_required
def admin_flights():
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    # Get filter parameters
    status = request.args.get('status', 'all')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Build query based on filters
            query = """
                SELECT f.id, f.flight_number, a1.city as departure_city, a2.city as arrival_city,
                       f.departure_time, f.arrival_time, ac.model as aircraft, 
                       f.economy_price, f.business_price, f.first_class_price, f.status,
                       f.gate, f.terminal
                FROM flights f
                JOIN airports a1 ON f.origin_airport_id = a1.id
                JOIN airports a2 ON f.destination_airport_id = a2.id
                JOIN aircraft ac ON f.aircraft_id = ac.id
            """
            
            params = []
            if status != 'all':
                query += " WHERE f.status = %s"
                params.append(status)
            
            query += " ORDER BY f.departure_time"
            
            cursor.execute(query, params)
            flights = cursor.fetchall()
            
            # Get all aircraft for the add/edit form
            cursor.execute("SELECT id, model FROM aircraft ORDER BY model")
            aircraft = cursor.fetchall()
            
            # Get all airports for the add/edit form
            cursor.execute("SELECT id, code, city, name FROM airports ORDER BY city")
            airports = cursor.fetchall()
            
            return render_template(
                'admin_flights.html',
                flights=flights,
                aircraft=aircraft,
                airports=airports,
                selected_status=status
            )
        except Exception as e:
            print(f"Error fetching flights: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin_flights.html', flights=[], aircraft=[], airports=[])

@app.route('/admin/flights/add', methods=['GET', 'POST'])
@login_required
def add_flight():
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Extract form data
        flight_number = request.form.get('flight_number') or generate_flight_number()
        origin_airport_id = request.form.get('origin_airport_id')
        destination_airport_id = request.form.get('destination_airport_id')
        aircraft_id = request.form.get('aircraft_id')
        departure_date = request.form.get('departure_date')
        departure_time = request.form.get('departure_time')
        arrival_date = request.form.get('arrival_date')
        arrival_time = request.form.get('arrival_time')
        economy_price = request.form.get('economy_price')
        business_price = request.form.get('business_price')
        first_class_price = request.form.get('first_class_price')
        status = request.form.get('status')
        gate = request.form.get('gate')
        terminal = request.form.get('terminal')
        
        # Combine date and time
        departure_datetime = f"{departure_date} {departure_time}:00"
        arrival_datetime = f"{arrival_date} {arrival_time}:00"
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Insert new flight
                cursor.execute("""
                    INSERT INTO flights (
                        flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                        departure_time, arrival_time, economy_price, business_price, first_class_price,
                        status, gate, terminal
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                    departure_datetime, arrival_datetime, economy_price, business_price, first_class_price,
                    status, gate, terminal
                ))
                
                conn.commit()
                return redirect(url_for('admin_flights'))
            except Exception as e:
                print(f"Error adding flight: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
    
    # GET request handling is done in admin_flights route
    return redirect(url_for('admin_flights'))

@app.route('/admin/flights/edit/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def edit_flight(flight_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Extract form data
        flight_number = request.form.get('flight_number')
        origin_airport_id = request.form.get('origin_airport_id')
        destination_airport_id = request.form.get('destination_airport_id')
        aircraft_id = request.form.get('aircraft_id')
        departure_date = request.form.get('departure_date')
        departure_time = request.form.get('departure_time')
        arrival_date = request.form.get('arrival_date')
        arrival_time = request.form.get('arrival_time')
        economy_price = request.form.get('economy_price')
        business_price = request.form.get('business_price')
        first_class_price = request.form.get('first_class_price')
        status = request.form.get('status')
        gate = request.form.get('gate')
        terminal = request.form.get('terminal')
        
        # Combine date and time
        departure_datetime = f"{departure_date} {departure_time}:00"
        arrival_datetime = f"{arrival_date} {arrival_time}:00"
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Update flight
                cursor.execute("""
                    UPDATE flights SET
                        flight_number = %s,
                        origin_airport_id = %s,
                        destination_airport_id = %s,
                        aircraft_id = %s,
                        departure_time = %s,
                        arrival_time = %s,
                        economy_price = %s,
                        business_price = %s,
                        first_class_price = %s,
                        status = %s,
                        gate = %s,
                        terminal = %s
                    WHERE id = %s
                """, (
                    flight_number, origin_airport_id, destination_airport_id, aircraft_id,
                    departure_datetime, arrival_datetime, economy_price, business_price, first_class_price,
                    status, gate, terminal, flight_id
                ))
                
                conn.commit()
                return redirect(url_for('admin_flights'))
            except Exception as e:
                print(f"Error updating flight: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
    
    # GET request - fetch the flight details
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get flight details
            cursor.execute("""
                SELECT * FROM flights WHERE id = %s
            """, (flight_id,))
            flight = cursor.fetchone()
            
            # Get all aircraft
            cursor.execute("SELECT id, model FROM aircraft ORDER BY model")
            aircraft = cursor.fetchall()
            
            # Get all airports
            cursor.execute("SELECT id, code, city, name FROM airports ORDER BY city")
            airports = cursor.fetchall()
            
            return render_template(
                'admin_edit_flight.html',
                flight=flight,
                aircraft=aircraft,
                airports=airports
            )
        except Exception as e:
            print(f"Error fetching flight details: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin_flights'))

@app.route('/admin/flights/delete/<int:flight_id>', methods=['POST'])
@login_required
def delete_flight(flight_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Check if there are any bookings for this flight
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE flight_id = %s", (flight_id,))
            booking_count = cursor.fetchone()[0]
            
            if booking_count > 0:
                # If there are bookings, just update the status to cancelled
                cursor.execute("UPDATE flights SET status = 'Cancelled' WHERE id = %s", (flight_id,))
            else:
                # If no bookings, we can delete the flight
                cursor.execute("DELETE FROM flights WHERE id = %s", (flight_id,))
            
            conn.commit()
        except Exception as e:
            print(f"Error deleting flight: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin_flights'))

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    # Get filter parameters
    status = request.args.get('status', 'all')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First check if there are any bookings at all
            cursor.execute("SELECT COUNT(*) as count FROM bookings")
            booking_count = cursor.fetchone()['count']
            
            if booking_count == 0:
                print("No bookings found in the database")
                return render_template('admin_bookings.html', bookings=[], selected_status=status)
            
            # Build query based on filters
            try:
                query = """
                    SELECT b.id, b.booking_reference, b.passenger_name, b.passenger_email,
                           f.flight_number, a1.city as departure_city, a2.city as arrival_city,
                           f.departure_time, b.travel_class, b.seat_number, b.booking_status,
                           b.total_amount, b.created_at
                    FROM bookings b
                    JOIN flights f ON b.flight_id = f.id
                    JOIN airports a1 ON f.origin_airport_id = a1.id
                    JOIN airports a2 ON f.destination_airport_id = a2.id
                """
                
                params = []
                if status != 'all':
                    query += " WHERE b.booking_status = %s"
                    params.append(status)
                
                query += " ORDER BY b.created_at DESC"
                
                cursor.execute(query, params)
                bookings = cursor.fetchall()
                
                print(f"Found {len(bookings)} bookings with status filter: {status}")
                
            except Exception as e:
                print(f"Error in JOIN query: {e}")
                # Fallback to simpler query if there's an issue with JOINs
                query = """
                    SELECT id, booking_reference, passenger_name, passenger_email,
                           flight_id, travel_class, seat_number, booking_status,
                           total_amount, created_at
                    FROM bookings
                """
                
                if status != 'all':
                    query += " WHERE booking_status = %s"
                    params = [status]
                else:
                    params = []
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                bookings = cursor.fetchall()
                
                # Add missing fields for template compatibility
                for booking in bookings:
                    booking['flight_number'] = 'Unknown'
                    booking['departure_city'] = 'Unknown'
                    booking['arrival_city'] = 'Unknown'
                    booking['departure_time'] = datetime.datetime.now()
            
            return render_template(
                'admin_bookings.html',
                bookings=bookings,
                selected_status=status
            )
        except Exception as e:
            print(f"Error fetching bookings: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin_bookings.html', bookings=[], selected_status=status)

@app.route('/admin/bookings/<int:booking_id>')
@login_required
def view_booking(booking_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # First, get the basic booking info
            cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
            booking = cursor.fetchone()
            
            if not booking:
                print(f"No booking found with ID {booking_id}")
                return redirect(url_for('admin_bookings'))
            
            try:
                # Try to get additional flight information
                cursor.execute("""
                    SELECT f.flight_number, a1.city as departure_city, a2.city as arrival_city,
                           f.departure_time, f.arrival_time, f.status as flight_status,
                           ac.model as aircraft, f.gate, f.terminal
                    FROM flights f
                    JOIN airports a1 ON f.origin_airport_id = a1.id
                    JOIN airports a2 ON f.destination_airport_id = a2.id
                    JOIN aircraft ac ON f.aircraft_id = ac.id
                    WHERE f.id = %s
                """, (booking['flight_id'],))
                
                flight_info = cursor.fetchone()
                
                if flight_info:
                    # Merge flight info into booking
                    for key, value in flight_info.items():
                        booking[key] = value
                else:
                    print(f"No flight found with ID {booking['flight_id']}")
                    # Add fallback values
                    booking['flight_number'] = 'Unknown'
                    booking['departure_city'] = 'Unknown'
                    booking['arrival_city'] = 'Unknown'
                    booking['departure_time'] = datetime.datetime.now()
                    booking['arrival_time'] = datetime.datetime.now()
                    booking['flight_status'] = 'Unknown'
                    booking['aircraft'] = 'Unknown'
                    booking['gate'] = 'Unknown'
                    booking['terminal'] = 'Unknown'
            except Exception as e:
                print(f"Error fetching flight details: {e}")
                # Add fallback values
                booking['flight_number'] = 'Unknown'
                booking['departure_city'] = 'Unknown'
                booking['arrival_city'] = 'Unknown'
                booking['departure_time'] = datetime.datetime.now()
                booking['arrival_time'] = datetime.datetime.now()
                booking['flight_status'] = 'Unknown'
                booking['aircraft'] = 'Unknown'
                booking['gate'] = 'Unknown'
                booking['terminal'] = 'Unknown'
            
            # Get cancellation details if any
            if booking['booking_status'] == 'Cancelled':
                try:
                    cursor.execute("""
                        SELECT * FROM cancellations WHERE booking_id = %s
                    """, (booking_id,))
                    cancellation = cursor.fetchone()
                except Exception as e:
                    print(f"Error fetching cancellation details: {e}")
                    cancellation = None
            else:
                cancellation = None
            
            print(f"Successfully retrieved booking: {booking['booking_reference']} for {booking['passenger_name']}")
            
            return render_template(
                'admin_view_booking.html',
                booking=booking,
                cancellation=cancellation
            )
        except Exception as e:
            print(f"Error fetching booking details: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin_bookings'))

@app.route('/admin/bookings/update-status/<int:booking_id>', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    if session.get('user_role') != 'admin':
        return redirect(url_for('index'))
    
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'Confirmed', 'Cancelled']:
        return redirect(url_for('view_booking', booking_id=booking_id))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Update booking status
            cursor.execute("""
                UPDATE bookings SET booking_status = %s WHERE id = %s
            """, (new_status, booking_id))
            
            # If cancelled, create a cancellation record
            if new_status == 'Cancelled':
                # Get booking amount
                cursor.execute("SELECT total_amount FROM bookings WHERE id = %s", (booking_id,))
                total_amount = cursor.fetchone()[0]
                
                # Generate cancellation ID and calculate refund (e.g., 75% of booking amount)
                cancellation_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                refund_amount = float(total_amount) * 0.75
                reason = "Cancelled by administrator"
                
                cursor.execute("""
                    INSERT INTO cancellations (booking_id, cancellation_id, refund_amount, reason)
                    VALUES (%s, %s, %s, %s)
                """, (booking_id, cancellation_id, refund_amount, reason))
            
            conn.commit()
        except Exception as e:
            print(f"Error updating booking status: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('view_booking', booking_id=booking_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not name or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Check if user already exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    return render_template('register.html', error='Email already registered')
                
                # Insert new user
                cursor.execute("""
                    INSERT INTO users (name, email, password, role)
                    VALUES (%s, %s, %s, %s)
                """, (name, email, hashed_password, 'user'))
                
                conn.commit()
                
                # Get the user ID for session
                cursor.execute("SELECT LAST_INSERT_ID()")
                user_id = cursor.fetchone()[0]
                
                # Set session variables
                session['user_id'] = user_id
                session['user_role'] = 'user'
                session['user_name'] = name
                
                return redirect(url_for('index'))
                
            except Exception as e:
                print(f"Error during registration: {e}")
                conn.rollback()
                return render_template('register.html', error='Registration failed. Please try again.')
            finally:
                cursor.close()
                conn.close()
    
    return render_template('register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Get user from database
                cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    # Set session variables
                    session['user_id'] = user['id']
                    session['user_role'] = user['role']
                    session['user_name'] = user['name']
                    
                    return redirect(url_for('admin_dashboard'))
                
                return render_template('admin_login.html', error='Invalid admin credentials')
                
            except Exception as e:
                print(f"Error during admin login: {e}")
            finally:
                cursor.close()
                conn.close()
    
    return render_template('admin_login.html')

@app.route('/booking-confirmation/<booking_ref>')
def booking_confirmation(booking_ref):
    """
    Display booking confirmation details after a successful booking.
    """
    print(f"Booking confirmation page requested for booking: {booking_ref}")
    
    # Try to get booking details from session first (more reliable for new bookings)
    booking = session.get('booking_details')
    if booking:
        print(f"Using session data for booking: {booking_ref}")
        # Add some default values for display
        booking['departure_city'] = 'Sample City'
        booking['arrival_city'] = 'Destination City'
        booking['departure_time'] = datetime.datetime.now() + datetime.timedelta(days=7)
        booking['arrival_time'] = datetime.datetime.now() + datetime.timedelta(days=7, hours=2)
        booking['aircraft'] = 'Airbus A320'
        booking['departure_code'] = 'SMP'
        booking['arrival_code'] = 'DST'
        booking['booking_status'] = 'Confirmed'
        
        return render_template(
            'booking_confirmation.html',
            booking=booking
        )
    
    # If not in session, try to get from database
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get booking details
            cursor.execute("""
                SELECT b.*, f.flight_number, f.departure_time, f.arrival_time, 
                       a1.city as departure_city, a1.code as departure_code,
                       a2.city as arrival_city, a2.code as arrival_code,
                       ac.model as aircraft
                FROM bookings b
                JOIN flights f ON b.flight_id = f.id
                JOIN airports a1 ON f.origin_airport_id = a1.id
                JOIN airports a2 ON f.destination_airport_id = a2.id
                JOIN aircraft ac ON f.aircraft_id = ac.id
                WHERE b.booking_reference = %s
            """, (booking_ref,))
            
            booking = cursor.fetchone()
            
            if booking:
                print(f"Found booking in database: {booking_ref}")
                return render_template(
                    'booking_confirmation.html',
                    booking=booking
                )
            else:
                print(f"Booking not found in database: {booking_ref}")
                
        except Exception as e:
            print(f"Error fetching booking details: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # If all else fails, redirect to homepage with an error message
    return redirect(url_for('index'))

@app.route('/direct-booking-confirmation', methods=['POST'])
def direct_booking_confirmation():
    """
    Process booking and immediately display confirmation without redirects
    """
    # Get form data
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    phone = request.form.get('phone')
    dob = request.form.get('dob')
    nationality = request.form.get('nationality')
    
    # Get flight data
    flight_number = request.form.get('flight_number')
    travel_class = request.form.get('travel_class')
    total_amount = float(request.form.get('total_amount'))
    booking_ref = request.form.get('booking_ref')
    
    # If user is logged in, use their name
    if 'user_name' in session:
        passenger_name = session['user_name']
    else:
        passenger_name = f"{first_name} {last_name}"
    
    # Generate a random seat based on class
    if travel_class == 'economy':
        seat_prefix = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
        seat_row = random.randint(20, 40)
    elif travel_class == 'business':
        seat_prefix = random.choice(['A', 'D', 'F'])
        seat_row = random.randint(10, 19)
    else:  # first class
        seat_prefix = random.choice(['A', 'F'])
        seat_row = random.randint(1, 9)
    
    seat_number = f"{seat_row}{seat_prefix}"
    
    # Create booking details for the confirmation page
    booking = {
        'booking_reference': booking_ref,
        'passenger_name': passenger_name,
        'email': email,
        'phone': phone,
        'flight_number': flight_number,
        'travel_class': travel_class,
        'seat_number': seat_number,
        'total_amount': total_amount,
        'departure_city': 'Sample City',
        'arrival_city': 'Destination City',
        'departure_time': datetime.datetime.now() + datetime.timedelta(days=7),
        'arrival_time': datetime.datetime.now() + datetime.timedelta(days=7, hours=2),
        'aircraft': 'Airbus A320',
        'departure_code': 'SMP',
        'arrival_code': 'DST',
        'booking_status': 'Confirmed'
    }
    
    # Store in session for future reference
    session['booking_details'] = booking
    
    # Try to save to database in background without waiting for result
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # First, get the flight ID from the flight number
            cursor.execute("SELECT id FROM flights WHERE flight_number = %s", (flight_number,))
            flight_result = cursor.fetchone()
            
            if not flight_result:
                # If flight doesn't exist, create a temporary one for demo
                cursor.execute("""
                    INSERT INTO flights (flight_number, origin_airport_id, destination_airport_id, aircraft_id, 
                                        departure_time, arrival_time, economy_price, business_price, first_class_price, status)
                    VALUES (%s, 1, 2, 1, NOW(), DATE_ADD(NOW(), INTERVAL 5 HOUR), 200, 500, 1000, 'Scheduled')
                """, (flight_number,))
                conn.commit()
                flight_id = cursor.lastrowid
            else:
                flight_id = flight_result[0]
            
            # Insert booking
            cursor.execute("""
                INSERT INTO bookings (booking_reference, passenger_name, passenger_email, flight_id, 
                                     travel_class, seat_number, total_amount, booking_status, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                booking_ref, 
                passenger_name, 
                email, 
                flight_id, 
                travel_class, 
                seat_number, 
                total_amount, 
                'Confirmed',
                session.get('user_id')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error saving booking: {e}")
        # Continue anyway - we'll show the confirmation page
    
    # Directly render the confirmation page
    return render_template('booking_confirmation.html', booking=booking)

if __name__ == '__main__':
    app.run(debug=True) 