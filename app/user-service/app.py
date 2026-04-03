from flask import Flask, jsonify, request

app = Flask(__name__)

# Fake DB
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

@app.route("/", methods=["GET"])
def home():
    return {"service": "user-service", "status": "running"}

# Get all users
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

# Get single user
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    for user in users:
        if user["id"] == user_id:
            return jsonify(user)
    return {"error": "User not found"}, 404

# Create new user
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = {
        "id": len(users) + 1,
        "name": data.get("name")
    }
    users.append(new_user)
    return jsonify(new_user), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)