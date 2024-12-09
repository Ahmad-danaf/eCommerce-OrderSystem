from threading import Thread
from app.rabbitmq import start_consumer
from app import create_app

# Start Flask app
app = create_app()
if __name__ == "__main__":
    # Start consumer in a separate thread
    consumer_thread = Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    app.run(host="0.0.0.0", port=5001, debug=True)
