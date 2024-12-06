import pika
import json
from app.controllers.order_controller import process_order

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # Declare exchange and queue
    channel.exchange_declare(exchange="order_exchange", exchange_type="fanout")
    queue_name = "order_queue"
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange="order_exchange", queue=queue_name)

    def callback(ch, method, properties, body):
        order = json.loads(body)
        if order.get("status") == "new":
            process_order(order)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
