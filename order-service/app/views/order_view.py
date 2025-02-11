from flask import Blueprint, request, jsonify
from kafka import KafkaConsumer
import json
import logging
from app.storage import load_from_file, storage,save_to_file
from kafka.errors import KafkaError
import time
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
ORDER_TOPIC = "order_events"
CONSUMER_GROUP = "order-service-group"

# Define Blueprint for orders
order_bp = Blueprint("orders", __name__)

def get_kafka_order_ids(topic_name):
    """
    Retrieve all order IDs dynamically from Kafka topic instead of relying only on in-memory storage.
    """
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=KAFKA_BROKER,
            group_id="order-service-group-temp",
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None
        )

        order_ids = set()
        start_time = time.time()
        timeout = 5  # Stop polling after 5 seconds

        while time.time() - start_time < timeout:
            messages = consumer.poll(timeout_ms=1000)
            if not messages:
                break  # No messages found, stop early

            for topic_partition, records in messages.items():
                for message in records:
                    order_id = message.key
                    if order_id:
                        order_ids.add(order_id)
                    if len(order_ids) >= 100:
                        break  # Stop collecting if we have enough data

        consumer.close()
        return list(order_ids)

    except KafkaError as ke:
        logger.error(f"Kafka error while fetching order IDs: {ke}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching order IDs: {e}")
        return []


@order_bp.route("/order-details", methods=["GET"])
def get_order_details():
    """
    Retrieve order details by orderId, including shipping costs.
    If order is missing from in-memory storage (due to restart), fetch from Kafka.
    """
    try:
        load_from_file()
        order_id = request.args.get("orderId")

        if not order_id:
            return jsonify({"error": "orderId is required"}), 400

        order = storage.get(order_id)

        # If order is missing in storage, attempt to fetch from Kafka
        if not order:
            logger.warning(f"Order {order_id} not found in storage, checking Kafka...")

            consumer = KafkaConsumer(
                ORDER_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                group_id="order-service-group-temp",
                enable_auto_commit=False,
                auto_offset_reset="earliest",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None
            )

            start_time = time.time()
            timeout = 5  # Stop polling after 5 seconds

            while time.time() - start_time < timeout:
                messages = consumer.poll(timeout_ms=1000)
                if not messages:
                    break  # No messages found, stop early

                for topic_partition, records in messages.items():
                    for message in records:
                        if message.key == order_id:
                            order = message.value
                            storage[order_id] = order  # Restore order in memory
                            save_to_file()  # Persist to file
                            logger.info(f"Recovered order {order_id} from Kafka")
                            consumer.close()
                            return jsonify(order), 200

            consumer.close()

        if not order:
            return jsonify({"error": f"Order with ID {order_id} not found"}), 404

        return jsonify(order), 200

    except KafkaError as ke:
        logger.error(f"Kafka error while retrieving order {order_id}: {ke}")
        return jsonify({"error": "Failed to retrieve order from Kafka"}), 500
    except Exception as e:
        logger.error(f"Error fetching order details: {e}")
        return jsonify({"error": "An internal error occurred"}), 500



@order_bp.route("/getAllOrderIdsFromTopic", methods=["GET"])
def get_all_order_ids():
    """
    Retrieve all order IDs dynamically from Kafka, not just from in-memory storage.
    """
    try:
        topic_name = request.args.get("topic")

        if not topic_name:
            return jsonify({"error": "Topic name is required"}), 400

        order_ids = get_kafka_order_ids(topic_name)

        if order_ids is None:
            return jsonify({"error": "Failed to fetch order IDs from Kafka"}), 500

        return jsonify({"topic": topic_name, "orderIds": order_ids}), 200

    except Exception as e:
        logger.error(f"Error fetching order IDs from Kafka topic: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
