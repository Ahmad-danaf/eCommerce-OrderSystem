from flask import Blueprint, request, jsonify
from app.storage import load_from_file, storage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Blueprint for orders
order_bp = Blueprint('orders', __name__)

@order_bp.route('/order-details', methods=['GET'])
def get_order_details():
    """Retrieve order details by orderId, including shipping costs."""
    try:
        load_from_file()
        order_id = request.args.get("orderId")

        if not order_id:
            return jsonify({"error": "orderId is required"}), 400

        order = storage.get(order_id)
        if not order:
            return jsonify({"error": f"Order with ID {order_id} not found"}), 404

        return jsonify(order), 200
    except Exception as e:
        logger.error(f"Error fetching order details: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

@order_bp.route('/getAllOrderIdsFromTopic', methods=['GET'])
def get_all_order_ids():
    """Retrieve all order IDs received from Kafka topic."""
    try:
        load_from_file()
        topic_name = request.args.get("topic")

        if not topic_name:
            return jsonify({"error": "Topic name is required"}), 400

        order_ids = list(storage.keys())

        return jsonify({"topic": topic_name, "orderIds": order_ids}), 200
    except Exception as e:
        logger.error(f"Error fetching order IDs from topic: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
