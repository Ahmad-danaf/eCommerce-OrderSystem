import pytest
from app import create_app
from app.storage import save_to_file
import json
@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client

def test_order_details(client):
    """Test the /order-details endpoint."""
    # Add a mock order to the storage file
    order_id = "ORD-12345"
    order_data = {
        order_id: {
            "orderId": order_id,
            "totalAmount": 100.0,
            "shippingCost": 2.0,
            "status": "new"
        }
    }
    with open("test_storage.json", "w") as f:
        json.dump(order_data, f)

    # Make a request to the API
    response = client.get(f"/order-details?orderId={order_id}")
    assert response.status_code == 200
    assert response.json["orderId"] == order_id
    assert response.json["shippingCost"] == 2.0

def test_order_details_not_found(client):
    """Test the /order-details endpoint when orderId is not found."""
    response = client.get("/order-details?orderId=ORD-99999")
    assert response.status_code == 404
    assert "error" in response.json
