from kafka import KafkaConsumer
import json
import logging
from app.storage import save_to_file, load_from_file, storage
from app.controllers.order_controller import serialize_order
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
ORDER_TOPIC = "order_events"

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    ORDER_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    enable_auto_commit=True
)

def process_order_event():
    """Consumes order events from Kafka and processes them."""
    try:
        load_from_file()  # Load existing orders from storage
        
        for message in consumer:
            order_data = message.value
            order_id = order_data.get("orderId")

            if not order_id:
                logger.warning("Received order without orderId, skipping...")
                continue

            if order_data.get("status") == "new":
                # Calculate shipping cost (2% of totalAmount)
                total_amount = order_data.get("totalAmount", 0)
                shipping_cost = round(total_amount * 0.02, 2)

                # Add shipping cost to the order details
                order_data["shippingCost"] = shipping_cost
                # Ensure order_data is JSON-serializable before storing
                clean_order = serialize_order(order_data)

                # Store the order in-memory (or persist to DB later)
                storage[order_id] = clean_order
                save_to_file()
                logger.info(f"Processed and stored order {order_id} with shipping cost {shipping_cost}")
            else:
                logger.info(f"Skipping order {order_id} with status {order_data['status']}")

    except Exception as e:
        logger.error(f"Error processing Kafka messages: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting Kafka consumer...")
    process_order_event()
