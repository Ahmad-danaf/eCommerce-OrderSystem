import logging
from datetime import datetime

logger = logging.getLogger(__name__)

VALID_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD']
VALID_STATUSES = ['pending', 'confirmed', 'cancelled', 'shipped', 'delivered','new', 'in progress']

def validate_order_data(order_data):
    if not order_data.get('orderId'):
        raise ValueError("Order ID is required")
    if not order_data.get('customerId'):
        raise ValueError("Customer ID is required")
    if not order_data.get('orderDate'):
        raise ValueError("Order date is required and must follow ISO 8601 format")
    if not isinstance(order_data.get('items'), list) or len(order_data['items']) == 0:
        raise ValueError("Order must have at least one item")
    if order_data.get('totalAmount') <= 0:
        raise ValueError("Total amount must be greater than 0")

def validate_item(item):
    if not item.get('itemId'):
        raise ValueError("Item ID is required")
    if not isinstance(item.get('quantity'), int) or item['quantity'] <= 0:
        raise ValueError("Quantity must be a positive integer")
    if not isinstance(item.get('price'), (float, int)) or item['price'] <= 0:
        raise ValueError("Price must be a positive number")

def validate_currency(currency):
    if currency not in VALID_CURRENCIES:
        raise ValueError(f"Invalid currency: {currency}. Valid options are {', '.join(VALID_CURRENCIES)}")

def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Valid statuses are {', '.join(VALID_STATUSES)}")

def validate_iso8601(date_string):
    try:
        datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Invalid ISO 8601 date format: {date_string}")

def validate_order(order):
    try:
        validate_order_data(order)
        validate_currency(order['currency'])
        validate_status(order['status'])
        for item in order['items']:
            validate_item(item)
    except ValueError as e:
        logger.error(f"Validation failed: {e}")
        raise
