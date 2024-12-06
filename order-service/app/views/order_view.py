from flask import Blueprint, request, jsonify
from app.storage import load_from_file

order_bp = Blueprint('orders', __name__)

@order_bp.route('/order-details', methods=['GET'])
def get_order_details():
    try:
        load_from_file()
        from app.storage import storage
        # Get the orderId from the query parameters
        order_id = request.args.get("orderId")
        if not order_id:
            return jsonify({"error": "orderId is required"}), 400

        # Retrieve the order from storage
        print(f"Storage: {storage}")
        order = storage.get(order_id)
        if not order:
            return jsonify({"error": f"Order with ID {order_id} not found"}), 404

        return jsonify(order), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
