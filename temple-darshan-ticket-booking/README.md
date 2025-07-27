# Temple Ticket Booking Platform

## Project Overview
Temple Ticket Booking is a web application designed to simplify the process of discovering, booking, and donating to temples. The platform allows users to:
- Browse a curated list of temples with detailed information and images
- Book tickets for temple visits, choosing ticket types and visit dates
- Manage their bookings and view booking history
- Make donations to support temples, with options for anonymous giving
- Register, log in, and access personalized features
- Contact the platform for support or inquiries

The project aims to make spiritual journeys accessible and convenient, while supporting the maintenance and heritage of sacred places.

## Key Features
- User authentication (registration, login, logout)
- Temple listing and detail pages
- Ticket booking with availability checks
- Booking management for users
- Donation system with recent donation stats
- Admin interface for managing temples and bookings
- Responsive design for desktop and mobile

## Getting Started

### 1. Clone the repository
```
git clone <your-repo-url>
cd templebooking_project
```

### 2. Create and activate a virtual environment
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Apply migrations
```
python manage.py migrate
```

### 5. Run the development server
```
python manage.py runserver
```

### 6. Access the application
Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 7. (Optional) Create a superuser for admin access
```
python manage.py createsuperuser
```

## Project Structure
- `temple_app/` – Main Django app with models, views, forms, templates, and static files
- `media/` – Uploaded images for temples
- `static/` – Static files (CSS, JS, images)
- `db.sqlite3` – Default SQLite database (auto-created)

## Requirements
All dependencies are listed in `requirements.txt`. Main packages include:
- Django
- Pillow (for image handling)

## Notes
- Static and media files are served locally in development. For production, configure proper static/media hosting.
- Replace email addresses in settings and contact forms with your own.

---

For any issues or contributions, please open an issue or pull request on the repository.
