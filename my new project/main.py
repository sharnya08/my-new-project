from flask import Flask, request, jsonify
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)

DATABASE = "registrations.db"
CAPACITY = 50


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                college TEXT DEFAULT '',
                department TEXT DEFAULT '',
                registered_at TEXT NOT NULL
            )
        """)


def registration_dict(row):
    return dict(row)


@app.get("/")
def home():
    return jsonify({
        "message": "Event Registration API is running",
        "event": "Backend Development Workshop",
        "capacity": CAPACITY,
        "endpoints": [
            "POST /register",
            "GET /registrations",
            "GET /registrations/<id>"
        ]
    })


@app.post("/register")
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send details as JSON"}), 400

    name = data.get("name")
    email = data.get("email")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Email is required"}), 400

    name = name.strip()
    email = email.strip().lower()

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Invalid email address"}), 400

    college = data.get("college", "")
    department = data.get("department", "")

    if not isinstance(college, str) or not isinstance(department, str):
        return jsonify({
            "error": "College and department must be text"
        }), 400

    with get_db() as db:
        # Reject duplicate email addresses.
        existing = db.execute(
            "SELECT id FROM registrations WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            return jsonify({
                "error": "This email is already registered"
            }), 409

        # Check event capacity.
        count = db.execute(
            "SELECT COUNT(*) FROM registrations"
        ).fetchone()[0]

        if count >= CAPACITY:
            return jsonify({"error": "Event is full"}), 409

        registered_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        try:
            cursor = db.execute("""
                INSERT INTO registrations
                (name, email, college, department, registered_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                email,
                college.strip(),
                department.strip(),
                registered_at
            ))
        except sqlite3.IntegrityError:
            return jsonify({
                "error": "This email is already registered"
            }), 409

        registration_id = cursor.lastrowid

        row = db.execute(
            "SELECT * FROM registrations WHERE id = ?",
            (registration_id,)
        ).fetchone()

        remaining = CAPACITY - count - 1

    return jsonify({
        "message": "Registration successful",
        "registration": registration_dict(row),
        "seats_remaining": remaining
    }), 201


@app.get("/registrations")
def get_registrations():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM registrations ORDER BY id"
        ).fetchall()

        count = len(rows)

    return jsonify({
        "event": "Backend Development Workshop",
        "capacity": CAPACITY,
        "registered_count": count,
        "seats_remaining": CAPACITY - count,
        "registrations": [
            registration_dict(row) for row in rows
        ]
    })


@app.get("/registrations/<int:registration_id>")
def get_registration(registration_id):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM registrations WHERE id = ?",
            (registration_id,)
        ).fetchone()

    if row is None:
        return jsonify({"error": "Registration not found"}), 404

    return jsonify({"registration": registration_dict(row)})


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)