from flask import Blueprint, request, jsonify
from app.controllers.order_controller import create_order
from app.rabbitmq import publish_message
import logging
logging.basicConfig(level=logging.DEBUG)

order_bp = Blueprint('orders', __name__)

@order_bp.route('/create-order', methods=['POST'])
def create_order_view():
    try:
        # Get request data
        data = request.json
        order_id = data.get('orderId')
        items_num = data.get('itemsNum')

        # Validate input
        if not order_id or not isinstance(items_num, int) or items_num <= 0:
            return jsonify({"error": "Invalid input. Provide a valid orderId and itemsNum > 0"}), 400

        # Create order
        order = create_order(order_id, items_num)

        # Publish the order to RabbitMQ
        publish_message('order_exchange', order.to_dict())

        return jsonify({
            "message": "Order created successfully and published to RabbitMQ",
            "order": order.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error("Internal Server Error: %s", e)
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500
