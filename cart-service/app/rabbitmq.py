import pika
import json

def publish_message(exchange_name, message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()

        # Declare exchange and queue, and bind them
        channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")
        channel.queue_declare(queue="test_queue")  # Declare the test queue
        channel.queue_bind(exchange=exchange_name, queue="test_queue")  # Bind queue to exchange

        # Publish the message
        channel.basic_publish(exchange=exchange_name, routing_key="", body=json.dumps(message))
        print(f"Message published: {message}")

        connection.close()
    except Exception as e:
        print(f"Error publishing message: {e}")
        raise

