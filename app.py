# Import required modules from Flask
from flask import Flask, render_template, request, redirect, jsonify, session

# Import SQLite for database
import sqlite3  

# Import datetime for timestamp
from datetime import datetime

# Create Flask application instance
app = Flask(__name__)

# Secret key is required for session (login system)
app.secret_key = "mysecretkey"

# -----------------------------
# ✅ DATABASE CREATE FUNCTION
# -----------------------------
def init_db():
    # Connect to SQLite database (creates file if not exists)
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Create feedback table if it does not exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  # Unique ID
        name TEXT,                             # User name
        email TEXT,                            # User email
        rating INTEGER,                        # Rating (1-5)
        message TEXT,                          # Feedback message
        time TEXT                              # Timestamp
    )
    """)

    # Save changes and close connection
    conn.commit()
    conn.close()

# Call function to initialize database
init_db()

# -----------------------------
# 🏠 HOME (User Panel)
# -----------------------------
@app.route("/")
def home():
    # Show feedback form page
    return render_template("index.html")

# -----------------------------
# 📥 ADD FEEDBACK
# -----------------------------
@app.route("/feedback", methods=["POST"])
def add_feedback():

    # Try to get JSON data (for Postman/API testing)
    data = request.get_json(silent=True)

    # If no JSON, get data from HTML form
    if not data:
        data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "rating": request.form.get("rating"),
            "message": request.form.get("message")
        }

    # Validation: required fields check
    if not data.get("name") or not data.get("email") or not data.get("rating"):
        return jsonify({"error": "Name, email and rating are required"}), 400

    # Validation: rating must be between 1 and 5
    if int(data["rating"]) < 1 or int(data["rating"]) > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Insert feedback into database
    c.execute(
        "INSERT INTO feedback (name,email,rating,message,time) VALUES (?,?,?,?,?)",
        (
            data["name"],       # User name
            data["email"],      # User email
            data["rating"],     # Rating
            data["message"],    # Feedback message
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time
        )
    )

    # Save and close database
    conn.commit()
    conn.close()

    # Redirect user back to form page
    return redirect("/")

# -----------------------------
# 🔐 LOGIN ROUTE
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    # If form submitted
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Simple static login check
        if username == "admin" and password == "1234":
            session["admin"] = True  # Store login session
            return redirect("/admin")
        else:
            return "Invalid Username or Password"

    # Show login page
    return render_template("login.html")

# -----------------------------
# 🛠 ADMIN PANEL (PROTECTED)
# -----------------------------
@app.route("/admin")
def admin():
    # Protect admin panel (only logged-in users allowed)
    if not session.get("admin"):
        return redirect("/login")

    # Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Fetch all feedbacks
    c.execute("SELECT * FROM feedback")
    feedbacks = c.fetchall()

    conn.close()

    # Send data to admin page
    return render_template("admin.html", feedbacks=feedbacks)

# -----------------------------
# 🚪 LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    # Remove admin session
    session.pop("admin", None)

    # Redirect to login page
    return redirect("/login")

# -----------------------------
# 🗑 DELETE FEEDBACK
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):
    # Allow only logged-in admin
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Delete feedback by ID
    c.execute("DELETE FROM feedback WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

# -----------------------------
# ✏️ EDIT FEEDBACK
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    # Allow only logged-in admin
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # If form submitted → update data
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")

        # Update feedback in database
        c.execute(
            "UPDATE feedback SET name=?, message=? WHERE id=?",
            (name, message, id)
        )

        conn.commit()
        conn.close()

        return redirect("/admin")

    # If GET request → fetch existing feedback
    c.execute("SELECT * FROM feedback WHERE id=?", (id,))
    feedback = c.fetchone()

    conn.close()

    # Open edit page with existing data
    return render_template("edit.html", f=feedback)

# -----------------------------
# 🚀 RUN APP
# -----------------------------
if __name__ == "__main__":
    # Run Flask app
    app.run(host="0.0.0.0", debug=True)