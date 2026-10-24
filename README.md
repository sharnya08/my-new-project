Event Registration Backend

Project Description

This project is a backend system for managing student registrations for the Backend Development Workshop.

Technologies Used

- Python
- Flask
- SQLite
- REST API

Features

- Register students for the event.
- View all registered participants.
- View an individual registration by ID.
- Prevent duplicate email registrations.
- Limit registrations to 50 participants.
- Validate student details.
- Store registration date and time.

How to Run

1. Install Python.

2. Install Flask using:
   
   "python -m pip install flask"

3. Run the application:
   
   "python app.py"

4. Open "http://127.0.0.1:5000" in your browser.

API Endpoints

Method| Endpoint| Purpose
POST| "/register"| Register a student
GET| "/registrations"| View all registrations
GET| "/registrations/1"| View a registration by ID

Database

SQLite stores the registration details in "registrations.db".

Author

Student Developer
