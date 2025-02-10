from kafka import KafkaProducer
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
ORDER_TOPIC = "order_events"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)

def publish_order(order_id, order_data):
    """Publishes order data to Kafka."""
    try:
        producer.send(ORDER_TOPIC, key=order_id, value=order_data)
        producer.flush()
        logger.info(f"Order {order_id} published to Kafka")
    except Exception as e:
        logger.error(f"Error publishing order {order_id} to Kafka: {e}")
        raise
