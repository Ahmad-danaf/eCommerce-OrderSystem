from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register blueprints
    from app.views.order_view import order_bp
    app.register_blueprint(order_bp)

    return app
