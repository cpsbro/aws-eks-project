from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Service URLs (will change in Kubernetes later)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5000")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:5001")

@app.route("/")
def home():
    return {"service": "api-gateway", "status": "running"}

# Get all users via user-service
@app.route("/users", methods=["GET"])
def users():
    response = requests.get(f"{USER_SERVICE_URL}/users")
    return jsonify(response.json())

# Get orders via order-service
@app.route("/orders", methods=["GET"])
def orders():
    response = requests.get(f"{ORDER_SERVICE_URL}/orders")
    return jsonify(response.json())

# Combined endpoint
@app.route("/dashboard/<int:user_id>", methods=["GET"])
def dashboard(user_id):
    user = requests.get(f"{USER_SERVICE_URL}/users/{user_id}").json()
    orders = requests.get(f"{ORDER_SERVICE_URL}/orders/user/{user_id}").json()

    return {
        "user": user,
        "orders": orders
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)