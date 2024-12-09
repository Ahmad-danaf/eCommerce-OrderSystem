import pika
import json

def publish_message(exchange_name, message):
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="shared-rabbitmq"))
        channel = connection.channel()

        # Declare the exchange (ensure it's durable and matches order-service configuration)
        channel.exchange_declare(exchange=exchange_name, exchange_type="fanout", durable=True)

        # Publish the message
        channel.basic_publish(exchange=exchange_name, routing_key="", body=json.dumps(message))
        print(f"Message published: {message}")

        connection.close()

    except Exception as e:
        print(f"Error publishing message: {e}")
        raise
