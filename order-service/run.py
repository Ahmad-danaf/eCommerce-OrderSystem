from threading import Thread
from app.kafka_consumer import process_order_event 
from app import create_app

# Start Flask app
app = create_app()
def start_consumer():
    """Runs Kafka consumer in a background thread."""
    consumer_thread = Thread(target=process_order_event, daemon=True)
    consumer_thread.start()

if __name__ == "__main__":
    start_consumer()
    app.run(host="0.0.0.0", port=5001, debug=True)
