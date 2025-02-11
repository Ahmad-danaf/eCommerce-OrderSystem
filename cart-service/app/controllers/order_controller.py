from app.models.order_model import Order, Item
from app.models.validators import validate_order
from datetime import datetime
import random
import uuid
from app.storage import load_from_file,save_to_file

def create_order(order_id, items_num):
    # Generate random items
    load_from_file()
    from app.storage import storage
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
    print("before saving")
    # Validate the order
    order_dict = order.to_dict()
    validate_order(order_dict)
    print("after validation")
    print("about to save..................")
    storage[order_dict["orderId"]] = order_dict
    save_to_file()
    return order_dict  

def update_order_status(order_id, new_status):
    load_from_file()
    from app.storage import storage
    order = storage.get(order_id, None)
    if not order:
        return None
    order["status"] = new_status
    order["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    storage[order_id] = order
    save_to_file()
    return order
