from datetime import datetime

class Item:
    def __init__(self, item_id, quantity, price):
        self.item_id = item_id
        self.quantity = quantity
        self.price = price

    def to_dict(self):
        return {
            "itemId": self.item_id,
            "quantity": self.quantity,
            "price": self.price,
        }
        
    def __str__(self):
        return f"Item ID: {self.item_id}, Quantity: {self.quantity}, Price: {self.price}"

class Order:
    def __init__(self, order_id, customer_id, order_date, items, total_amount, currency, status):
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.items = items
        self.total_amount = total_amount
        self.currency = currency
        self.status = status

    def to_dict(self):
        return {
            "orderId": self.order_id,
            "customerId": self.customer_id,
            "orderDate": self.order_date,
            "items": [item.to_dict() for item in self.items],
            "totalAmount": self.total_amount,
            "currency": self.currency,
            "status": self.status,
        }
    
    def __str__(self):
        return f"Order ID: {self.order_id}, Customer ID: {self.customer_id}, Order Date: {self.order_date}, Items: {self.items}, Total Amount: {self.total_amount}, Currency: {self.currency}, Status: {self.status}"