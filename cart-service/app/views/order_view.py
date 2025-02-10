from flask import Blueprint, request, jsonify
from app.controllers.order_controller import create_order, update_order_status
import logging
from kafka_producer import publish_order
from datetime import datetime
import json
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

order_bp = Blueprint('orders', __name__)

@order_bp.route('/create-order', methods=['POST'])
def create_order_view():
    try:
        logger.info("Creating order")
        # Get request data
        data = request.json
        order_id = data.get('orderId')
        items_num = data.get('itemsNum')

        # Validate input
        if not order_id or not isinstance(items_num, int) or items_num <= 0:
            return jsonify({"error": "Invalid input. Provide a valid orderId and itemsNum > 0"}), 400
        logger.info("Order validated")
        # Create order
        order = create_order(order_id, items_num)
        
        # Publish order to Kafka
        publish_order(order_id, order)


        return jsonify({"message": "Order created successfully", "order": order}), 201
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({"error": "no way"}), 500
    
    
@order_bp.route("/update-order", methods=["PUT"])
def update_order():
    try:
        data = request.json
        order_id = data.get("orderId")
        new_status = data.get("status")

        if not order_id or not new_status:
            return jsonify({"error": "orderId and status are required"}), 400
        # Check if status is a valid string
        if not isinstance(new_status, str):
            return jsonify({"error": "Invalid status. Status must be a string"}), 400
        
        # Update order status
        update_event = update_order_status(order_id, new_status)

        # Publish update to Kafka
        publish_order(order_id, update_event)

        return jsonify({"message": "Order updated successfully", "order": update_event}), 200
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        return jsonify({"error": str(e)}), 500
