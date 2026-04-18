from flask import Flask, request, jsonify

app = Flask(__name__)
feedbacks = []

# Home route
@app.route("/")
def home():
    return "Feedback System Running"

# Add feedback(POST)
@app.route("/feedback",methods = ["POST"])
def add_feedback():
    data = request.get_json()

    feedback = {
        "id":len(feedbacks) + 1,
        "name": data["name"],
        "message": data["message"]
    }

    feedbacks.append(feedback)

    return jsonify({"message":"Feedback added","data": feedback})

# Get feedback(GET)
@app.route("/feedback",methods = ["GET"])
def get_feedback():
    return jsonify(feedbacks)

# Run server
if __name__ == "__main__":
    app.run(debug = True)