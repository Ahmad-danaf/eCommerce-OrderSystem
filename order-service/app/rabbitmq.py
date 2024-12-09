import pika
import json
from app.controllers.order_controller import process_order
import time
def start_consumer():
    while True:
        try:
            print("Connecting to RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="shared-rabbitmq"))
            channel = connection.channel()

            # Declare exchange (ensure it matches cart-service configuration)
            channel.exchange_declare(exchange="order_exchange", exchange_type="fanout", durable=True)

            # Declare a durable queue (non-temporary)
            queue_name = "order_queue"
            channel.queue_declare(queue=queue_name, durable=True)

            # Bind the queue to the exchange
            channel.queue_bind(exchange="order_exchange", queue=queue_name)
            print(f"Queue '{queue_name}' bound to exchange 'order_exchange'")

            # Define the callback
            def callback(ch, method, properties, body):
                print("Callback triggered")
                order = json.loads(body)
                print(f"Received message: {order}")
                if order.get("status") == "new":
                    process_order(order)

            # Start consuming
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print("Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()

        except Exception as e:
            print("Connection to RabbitMQ failed. Retrying in 5 seconds...")
            time.sleep(5)
            
