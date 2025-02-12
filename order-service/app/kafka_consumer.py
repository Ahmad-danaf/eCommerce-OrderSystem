from kafka import KafkaConsumer
import json
import logging
import time
from kafka.errors import (
    KafkaTimeoutError,
    NoBrokersAvailable,
    CommitFailedError,
    KafkaConfigurationError,
    NotLeaderForPartitionError,
    OffsetOutOfRangeError,
    RequestTimedOutError
)
from app.storage import save_to_file, load_from_file, storage
from app.controllers.order_controller import serialize_order

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"
ORDER_TOPIC = "order_events"
CONSUMER_GROUP = "order-service-group"

# Initialize Kafka Consumer
def create_consumer():
    """Creates a Kafka consumer with proper error handling."""
    try:
        consumer = KafkaConsumer(
            ORDER_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            group_id=CONSUMER_GROUP,
            enable_auto_commit=False,  # Manual offset commit
            auto_offset_reset="earliest",  # Start from earliest if offset is invalid
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None
        )
        return consumer
    except KafkaConfigurationError as e:
        logger.error(f"Kafka configuration error: {e}")
        raise SystemExit("Fatal error: Incorrect Kafka configuration.")  # Exit process
    except Exception as e:
        logger.error(f"Unexpected error creating Kafka consumer: {e}")
        raise

def process_order_event():
    """Consumes order events from Kafka and processes them reliably."""
    consumer = create_consumer()
    load_from_file()

    while True:
        try:
            messages = consumer.poll(timeout_ms=1000)  # Poll messages in batches
            if not messages:
                continue

            for topic_partition, records in messages.items():
                for message in records:
                    try:
                        order_data = message.value
                        order_id = message.key  # Order ID is the key

                        if not order_id:
                            logger.warning("Received order without orderId, skipping...")
                            continue

                        logger.info(f"Processing order {order_id}: {order_data}")

                        # Process every event (new or update)
                        total_amount = order_data.get("totalAmount", 0)
                        # Calculate shipping cost only if needed (e.g., for new orders)
                        if order_data.get("status") == "new":
                            shipping_cost = round(total_amount * 0.02, 2)
                            order_data["shippingCost"] = shipping_cost
                        else:
                            existing_shipping_cost = order_data.get("shippingCost", None)
                            if existing_shipping_cost is not None:
                               order_data["shippingCost"] = existing_shipping_cost
                            else:
                                shipping_cost = round(total_amount * 0.02, 2)
                                order_data["shippingCost"] = shipping_cost
                            
                            
                        clean_order = serialize_order(order_data)
                        storage[order_id] = clean_order
                        save_to_file()
                        logger.info(f"Updated order {order_id} in storage.")

                        try:
                            consumer.commit()
                        except CommitFailedError as ce:
                            logger.error(f"Commit failed for order {order_id}: {ce}")
                            continue

                    except Exception as e:
                        logger.error(f"Error processing order {order_id}: {e}")
                        continue

        except (KafkaTimeoutError, RequestTimedOutError) as kte:
            logger.error(f"Kafka timeout error: {kte}")
            time.sleep(5)
        except NoBrokersAvailable as nb:
            logger.error(f"Kafka broker is unavailable: {nb}")
            time.sleep(10)
        except NotLeaderForPartitionError as npe:
            logger.error(f"Partition leader changed: {npe}, refreshing metadata")
            consumer.close()
            time.sleep(5)
            consumer = create_consumer()
        except OffsetOutOfRangeError as ooe:
            logger.error(f"Offset out of range: {ooe}, resetting offset")
            consumer.seek_to_beginning()
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}")
            time.sleep(5)

if __name__ == "__main__":
    logger.info("Starting Kafka consumer...")
    process_order_event()
