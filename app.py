# Import required modules from Flask
from flask import Flask, render_template, request, redirect, jsonify

# Import SQLite for database
import sqlite3  

# Import datetime for timestamp
from datetime import datetime

# Create Flask application instance
app = Flask(__name__)

# -----------------------------
# ✅ DATABASE CREATE FUNCTION
# -----------------------------
def init_db():
    # Connect to database (it will create file if not exists)
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Create feedback table if it doesn't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        rating INTEGER,
        message TEXT,
        time TEXT
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
# 📥 ADD FEEDBACK (POST)
# -----------------------------
@app.route("/feedback", methods=["POST"])
def add_feedback():

    # Try to get JSON data (for Postman/API)
    data = request.get_json(silent=True)

    # If no JSON, get data from form (HTML form)
    if not data:
        data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "rating": request.form.get("rating"),
            "message": request.form.get("message")
        }

    # Validation: check required fields
    if not data.get("name") or not data.get("email") or not data.get("rating"):
        return jsonify({"error": "Name, email and rating are required"}), 400

    # Validation: rating must be between 1 and 5
    if int(data["rating"]) < 1 or int(data["rating"]) > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Insert data into database
    c.execute(
        "INSERT INTO feedback (name,email,rating,message,time) VALUES (?,?,?,?,?)",
        (
            data["name"],       # user name
            data["email"],      # user email
            data["rating"],     # rating value
            data["message"],    # feedback message
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # current time
        )
    )

    # Save and close database
    conn.commit()
    conn.close()

    # Redirect back to home page
    return redirect("/")

# -----------------------------
# 🛠 ADMIN PANEL (VIEW)
# -----------------------------
@app.route("/admin")
def admin():
    # Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Fetch all feedbacks
    c.execute("SELECT * FROM feedback")
    feedbacks = c.fetchall()

    # Close connection
    conn.close()

    # Send data to admin page
    return render_template("admin.html", feedbacks=feedbacks)

# -----------------------------
# 🗑 DELETE FEEDBACK
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):
    # Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Delete feedback by ID
    c.execute("DELETE FROM feedback WHERE id=?", (id,))

    # Save and close
    conn.commit()
    conn.close()

    # Redirect back to admin panel
    return redirect("/admin")

# -----------------------------
# ✏️ EDIT FEEDBACK
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    # Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # If form is submitted (POST request)
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")

        # Update feedback in database
        c.execute(
            "UPDATE feedback SET name=?, message=? WHERE id=?",
            (name, message, id)
        )

        # Save and close
        conn.commit()
        conn.close()

        # Redirect to admin panel
        return redirect("/admin")

    # If GET request → fetch existing data
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