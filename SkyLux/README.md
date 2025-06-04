# SkyLux Airlines Management System

A comprehensive airlines management system built with Flask, MySQL, and modern web technologies.

## Features

- **User-friendly Interface**: Modern, responsive design for seamless user experience
- **Flight Search & Booking**: Advanced search functionality with flexible date options
- **Booking Management**: View, modify, and cancel bookings
- **Flight Status**: Real-time flight status updates
- **User Authentication**: Secure login and registration system
- **Admin Dashboard**: Comprehensive management tools for administrators

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python with Flask framework
- **Database**: MySQL
- **Authentication**: Werkzeug security for password hashing

## Installation

### Prerequisites

- Python 3.7+
- MySQL 5.7+ or MariaDB 10.2+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**

```bash
git clone <repository-url>
cd SkyLux
```

2. **Create and activate a virtual environment (optional but recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure the database**

Edit the database configuration in `app.py` and `database/setup.py` to match your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'skylux_airlines'
}
```

5. **Set up the database**

```bash
python database/setup.py
```

6. **Run the application**

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Admin Access

To access the admin dashboard, use the following credentials:

- **Email**: admin@skylux.com
- **Password**: admin123

## Project Structure

```
SkyLux/
├── app.py                  # Main Flask application file
├── database/
│   └── setup.py            # Database setup script
├── static/
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   └── js/
│       └── script.js       # Client-side JavaScript
├── templates/
│   ├── admin_dashboard.html # Admin dashboard template
│   ├── flight_results.html  # Flight search results page
│   ├── index.html           # Homepage
│   ├── login.html           # Login page
│   ├── modify_booking.html  # Booking modification page
│   └── register.html        # Registration page
└── README.md               # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Icons and design inspiration from various sources
- Flask community for excellent documentation and support 