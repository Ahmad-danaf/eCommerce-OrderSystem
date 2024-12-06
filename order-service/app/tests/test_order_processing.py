from app.controllers.order_controller import process_order
from app.storage import load_from_file, save_to_file, storage

def test_process_order():
    """Test processing an order and saving it persistently."""
    # Create a mock order
    order = {
        "orderId": "ORD-99999",
        "totalAmount": 500.0,
        "status": "new"
    }

    # Process the order
    process_order(order)

    # Assert the order is stored in memory
    assert "ORD-99999" in storage
    assert storage["ORD-99999"]["shippingCost"] == 10.0

    # Assert the order is saved to the file
    save_to_file()
    load_from_file()
    assert "ORD-99999" in storage
    assert storage["ORD-99999"]["shippingCost"] == 10.0
