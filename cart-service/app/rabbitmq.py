import pika
import json

def publish_message(exchange_name, message):
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()

        # Declare the exchange as fanout (broadcast to all consumers)
        channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")

        # Publish the message to the exchange
        channel.basic_publish(exchange=exchange_name, routing_key="", body=json.dumps(message))
        print(f"Message published: {message}")

        # Close the connection
        connection.close()
    except Exception as e:
        print(f"Error publishing message: {e}")
        raise

