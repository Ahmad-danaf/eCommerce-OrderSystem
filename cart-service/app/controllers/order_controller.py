from app.models.order_model import Order, Item
from app.models.validators import validate_order
from datetime import datetime
import random
import uuid

def create_order(order_id, items_num):
    # Generate random items
    items = [
        Item(
            item_id=f"ITEM-{i+1}",
            quantity=random.randint(1, 10),
            price=round(random.uniform(10, 100), 2)
        )
        for i in range(items_num)
    ]

    # Calculate total amount
    total_amount = sum(item.quantity * item.price for item in items)

    # Create order object
    order = Order(
        order_id=order_id,
        customer_id=str(uuid.uuid4()),
        order_date=datetime.utcnow().isoformat() + "Z",
        items=items,
        total_amount=total_amount,
        currency="USD",
        status="new"
    )

    # Validate the order
    validate_order(order.to_dict())

    return order
