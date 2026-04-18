# Import required modules from Flask
from flask import Flask, request, jsonify

# Create Flask appication instance
app = Flask(__name__)
# List to store feedback data in memory
feedbacks = []

# Home route to check if server is running
@app.route("/")
def home():
    return "Feedback System Running" # simple sever status message

from datetime import datetime
# Add feedback(POST)
# POST API to add new feedback
@app.route("/feedback",methods = ["POST"])
def add_feedback():
    # Get JSON data sent by the client
    data = request.get_json()

    # Validation: check if required fields are present
    if not data.get("name") or not data.get("email") or not data.get("rating"):
        return jsonify({"error":"Name,email and Rating are required"}),400
    
    # Validation: rating must be between 1 and 5
    if int(data["rating"]) < 1 or int(data["rating"]) > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}),400

    # Create feedback object
    feedback = {
        "id":len(feedbacks) + 1,# auto-increment ID
        "name": data["name"], # User name
        "email": data["email"], # User email
        "rating": data["rating"], # rating value
        "message": data["message"], # feedback message 
        "time": 
datetime.now().strftime("%Y-%m-%d  %H:%M:%S") # Current timestamp
    }
    # Add feedback to list
    feedbacks.append(feedback)

    # Return saved feedback as response
    return jsonify({"message":"Feedback added","data": feedback})

# GET API to retrieve all feedbacks
# Get feedback(GET)
@app.route("/feedback",methods = ["GET"])
def get_feedback():

    # Return all stored feedbacks
    return jsonify(feedbacks)

# Run server(Flask application)
if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = True)# Enable debug mode for development