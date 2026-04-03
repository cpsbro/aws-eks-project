from flask import Flask, jsonify, request

app = Flask(__name__)

orders = [
    {"id": 1, "item": "Laptop", "user_id": 1},
    {"id": 2, "item": "Phone", "user_id": 2}
]

@app.route("/", methods=["GET"])
def home():
    return {"service": "order-service", "status": "running"}

# Get all orders
@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)

# Create order
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    new_order = {
        "id": len(orders) + 1,
        "item": data.get("item"),
        "user_id": data.get("user_id")
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# Get orders by user
@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    user_orders = [o for o in orders if o["user_id"] == user_id]
    return jsonify(user_orders)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)