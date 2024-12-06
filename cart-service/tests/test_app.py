import requests
import pika
import json

# Flask app base URL
BASE_URL = "http://localhost:5000"  # Ensure your Flask app is running

# RabbitMQ settings
RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "test_queue"

# Helper function to consume messages from RabbitMQ
def consume_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare the queue (ensure it's consistent with the producer)
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    # Consume a single message
    method_frame, header_frame, body = channel.basic_get(queue=RABBITMQ_QUEUE, auto_ack=True)

    connection.close()
    return body


# Test cases
def test_create_order_invalid_input():
    """Test /create-order with invalid input"""
    payload = {
        "orderId": "",
        "itemsNum": 0
    }
    response = requests.post(f"{BASE_URL}/create-order", json=payload)
    assert response.status_code == 400
    assert "Invalid input" in response.json()["error"]

def test_create_order_success():
    """Test /create-order with valid input"""
    payload = {
        "orderId": "ORD-12345",
        "itemsNum": 3
    }
    response = requests.post(f"{BASE_URL}/create-order", json=payload)

    # Validate HTTP response
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Order created successfully and published to RabbitMQ"
    assert data["order"]["orderId"] == "ORD-12345"
    assert len(data["order"]["items"]) == 3

def test_rabbitmq_message_published():
    """Test if the message is published to RabbitMQ"""
    payload = {
        "orderId": "ORD-56789",
        "itemsNum": 2
    }
    requests.post(f"{BASE_URL}/create-order", json=payload)

    # Consume the message from RabbitMQ
    message = consume_message()
    assert message is not None

    # Validate the message content
    message_data = json.loads(message)
    assert message_data["orderId"] == "ORD-56789"
    assert len(message_data["items"]) == 2
    assert message_data["status"] == "new"

if __name__ == "__main__":
    test_create_order_invalid_input()
    test_create_order_success()
    test_rabbitmq_message_published()
    print("All tests passed!")
