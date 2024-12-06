import threading
from app.rabbitmq import start_consumer
from app import create_app

# Start Flask app
app = create_app()

if __name__ == "__main__":
    # Run RabbitMQ consumer in a separate thread
    threading.Thread(target=start_consumer).start()

    # Start Flask API
    app.run(debug=True, port=5001)
