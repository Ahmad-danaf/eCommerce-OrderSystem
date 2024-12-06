from app.rabbitmq import publish_message

order = {
    "orderId": "ORD-12345",
    "customerId": "CUST-67890",
    "orderDate": "2024-12-06T10:00:00Z",
    "items": [{"itemId": "ITEM-1", "quantity": 2, "price": 20.00}],
    "totalAmount": 40.00,
    "currency": "USD",
    "status": "new"
}
publish_message("order_exchange", order)
