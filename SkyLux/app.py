from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import random
import string
import datetime
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

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
    return render_template('index.html')

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
    # For this demo, we'll generate a sample booking if the reference is valid format
    
    if len(booking_ref) != 6 or not all(c in string.ascii_uppercase + string.digits for c in booking_ref):
        return jsonify({'success': False, 'error': 'Invalid booking reference'})
    
    # Generate random booking data
    booking = {
        'booking_reference': booking_ref,
        'passenger_name': 'John Doe',
        'passenger_email': email or 'john.doe@example.com',
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
    # For this demo, we'll just render the modification page
    
    return render_template('modify_booking.html', booking_ref=booking_ref)

@app.route('/booking')
def booking():
    # Get flight details from query parameters
    flight_number = request.args.get('flight')
    travel_class = request.args.get('class')
    search_id = request.args.get('search_id')
    return_flight = request.args.get('return')
    
    if not flight_number or not travel_class or not search_id:
        return redirect(url_for('index'))
    
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
    if return_flight:
        for flight in search_data.get('return_flights', []):
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # In a real application, we would validate against the database
        # For this demo, we'll use a hardcoded admin user
        if email == 'admin@skylux.com' and password == 'admin123':
            session['user_id'] = 1
            session['user_role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        
        return render_template('login.html', error='Invalid email or password')
    
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
    
    return render_template('admin_dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # In a real application, we would store the user in the database
        # For this demo, we'll just redirect to login
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True) 