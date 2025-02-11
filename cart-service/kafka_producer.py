from kafka import KafkaProducer
import json
import logging
import time
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
ORDER_TOPIC = "order_events"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),  # Ensures JSON encoding
    key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k  # Ensures proper key encoding
)

def publish_order(order_id, order_data, retries=5, delay=2):
    """
    Publishes order data to Kafka with retries.
    Retries up to `retries` times if Kafka is unavailable.
    """
    if not isinstance(order_data, dict):
        raise ValueError("order_data must be a dictionary")

    for attempt in range(retries):
        try:
            producer.send(ORDER_TOPIC, key=order_id.encode("utf-8"), value=order_data)
            producer.flush()  # Ensure the message is sent
            logger.info(f"Order {order_id} published to Kafka successfully")
            return  # Exit successfully
        except KafkaError as e:
            logger.error(f"Kafka publish failed for order {order_id}, attempt {attempt + 1}: {e}")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff

    logger.error(f"Failed to publish order {order_id} after {retries} attempts.")
    raise RuntimeError(f"Kafka publish failed after {retries} attempts for order {order_id}")
