// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Header background change on scroll
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
        header.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.boxShadow = 'none';
    }
});

// Fade in animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('departure').setAttribute('min', today);
    document.getElementById('return').setAttribute('min', today);

    // Booking form submission
    document.getElementById('bookingForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const bookingData = {};
        formData.forEach((value, key) => {
            bookingData[key] = value;
        });
        
        // Show loading state
        const submitBtn = this.querySelector('.search-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Searching Flights...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/search-flights', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookingData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Redirect to flight results page
                window.location.href = `/flight-results?search_id=${result.search_id}`;
            } else {
                alert('Error searching flights: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to search flights. Please try again.');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
});

// Flight status check
async function checkFlightStatus() {
    const flightNumber = document.getElementById('flightStatus').value;
    const resultDiv = document.getElementById('statusResult');
    
    if (flightNumber) {
        try {
            const response = await fetch(`/api/flight-status/${flightNumber}`);
            const result = await response.json();
            
            if (result.success) {
                const flight = result.flight;
                const departureTime = new Date(flight.departure_time).toLocaleString();
                const arrivalTime = new Date(flight.arrival_time).toLocaleString();
                
                resultDiv.innerHTML = `
                    <strong>Flight ${flight.flight_number}</strong><br>
                    Route: ${flight.departure_city} → ${flight.arrival_city}<br>
                    Departure: ${departureTime}<br>
                    Arrival: ${arrivalTime}<br>
                    Status: <span style="color: #4299e1; font-weight: bold;">${flight.status}</span><br>
                    Gate: ${flight.gate || 'TBA'} | Terminal: ${flight.terminal || 'TBA'}
                `;
                resultDiv.style.display = 'block';
            } else {
                resultDiv.innerHTML = `<span style="color: #f56565;">Flight not found</span>`;
                resultDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to check flight status');
        }
    } else {
        alert('Please enter a flight number');
    }
}

// Manage booking
async function manageBooking() {
    const bookingRef = document.getElementById('bookingRef').value;
    const email = document.getElementById('email').value;
    const resultDiv = document.getElementById('bookingResult');
    
    if (bookingRef && email) {
        try {
            const response = await fetch(`/api/booking/${bookingRef}?email=${encodeURIComponent(email)}`);
            const result = await response.json();
            
            if (result.success) {
                const booking = result.booking;
                const departureTime = new Date(booking.departure_time).toLocaleString();
                
                resultDiv.innerHTML = `
                    <strong>Booking Found!</strong><br>
                    Reference: ${booking.booking_reference}<br>
                    Route: ${booking.departure_city} → ${booking.arrival_city}<br>
                    Date: ${departureTime}<br>
                    Status: <span style="color: ${booking.booking_status === 'Confirmed' ? '#48bb78' : '#f56565'}">${booking.booking_status}</span><br>
                    Amount: ${booking.total_amount}<br>
                    Gate: ${booking.gate || 'TBA'} | Terminal: ${booking.terminal || 'TBA'}
                `;
                resultDiv.style.display = 'block';
            } else {
                resultDiv.innerHTML = `<span style="color: #f56565;">${result.error || 'Booking not found'}</span>`;
                resultDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to retrieve booking');
        }
    } else {
        alert('Please enter both booking reference and email');
    }
}

// Cancel flight
async function cancelFlight() {
    const cancelRef = document.getElementById('cancelRef').value;
    const cancelEmail = document.getElementById('cancelEmail').value;
    const resultDiv = document.getElementById('cancelResult');
    
    if (cancelRef && cancelEmail) {
        try {
            // First verify the booking exists
            const bookingResponse = await fetch(`/api/booking/${cancelRef}?email=${encodeURIComponent(cancelEmail)}`);
            const bookingResult = await bookingResponse.json();
            
            if (bookingResult.success) {
                const booking = bookingResult.booking;
                
                resultDiv.innerHTML = `
                    <strong>Booking Options</strong><br>
                    Reference: ${booking.booking_reference}<br>
                    Route: ${booking.departure_city} → ${booking.arrival_city}<br>
                    Date: ${new Date(booking.departure_time).toLocaleString()}<br>
                    <button style="margin: 5px; padding: 8px 16px; background: #48bb78; color: white; border: none; border-radius: 5px; cursor: pointer;" onclick="modifyBooking('${booking.booking_reference}')">Modify Booking</button>
                    <button style="margin: 5px; padding: 8px 16px; background: #f56565; color: white; border: none; border-radius: 5px; cursor: pointer;" onclick="confirmCancellation('${booking.booking_reference}')">Cancel Flight</button>
                `;
                resultDiv.style.display = 'block';
            } else {
                resultDiv.innerHTML = `<span style="color: #f56565;">${bookingResult.error || 'Booking not found'}</span>`;
                resultDiv.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to retrieve booking');
        }
    } else {
        alert('Please enter both booking reference and email');
    }
}

function modifyBooking(bookingRef) {
    window.location.href = `/modify-booking/${bookingRef}`;
}

function confirmCancellation(bookingRef) {
    if (confirm('Are you sure you want to cancel this booking? This action cannot be undone.')) {
        cancelBooking(bookingRef);
    }
}

async function cancelBooking(bookingRef) {
    try {
        const response = await fetch(`/api/booking/${bookingRef}/cancel`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Booking cancelled successfully. If eligible, a refund will be processed within 7-10 business days.');
            document.getElementById('cancelResult').innerHTML = `
                <span style="color: #48bb78;">Booking cancelled successfully!</span><br>
                Reference: ${bookingRef}<br>
                Cancellation ID: ${result.cancellation_id}
            `;
        } else {
            alert('Failed to cancel booking: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to cancel booking. Please try again or contact customer service.');
    }
} 