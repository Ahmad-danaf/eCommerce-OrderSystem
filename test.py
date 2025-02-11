import unittest
import requests
import time
import json

# API URLs (change ports if needed)
CART_SERVICE_URL = "http://localhost:5000"
ORDER_SERVICE_URL = "http://localhost:5001"

class TestEcommerceSystem(unittest.TestCase):

    def setUp(self):
        """Runs before each test: Creates a new order to work with."""
        self.order_id = f"TEST-ORDER-{int(time.time())}"  # Unique order ID
        self.items_num = 3

        print(f"Setting up test with order_id: {self.order_id}")

        response = requests.post(
            f"{CART_SERVICE_URL}/create-order",
            json={"orderId": self.order_id, "itemsNum": self.items_num},
        )

        self.assertEqual(response.status_code, 201, "Order creation failed")
        response_data = response.json()
        self.assertIn("order", response_data, "Order response is missing 'order' key")
        self.assertEqual(response_data["order"]["orderId"], self.order_id, "Order ID mismatch")

        # Wait for Kafka to process the message
        time.sleep(10)  # Ensure Kafka consumers have received the message

    def test_create_order(self):
        """Test if order creation API returns a valid response."""
        print("Running test_create_order")

        order_id = f"TEST-ORDER-{int(time.time())}"
        response = requests.post(
            f"{CART_SERVICE_URL}/create-order",
            json={"orderId": order_id, "itemsNum": 2},
        )

        self.assertEqual(response.status_code, 201, "Order creation failed")
        response_data = response.json()
        self.assertIn("order", response_data, "Order response does not contain order details")
        self.assertEqual(response_data["order"]["orderId"], order_id, "Order ID mismatch")

        print("test_create_order succeeded")

    def test_update_order_status(self):
        """Test if order status update API works correctly."""
        print("Running test_update_order_status")

        response = requests.put(
            f"{CART_SERVICE_URL}/update-order",
            json={"orderId": self.order_id, "status": "shipped"},
        )

        self.assertEqual(response.status_code, 200, "Failed to update order")
        response_data = response.json()
        self.assertIn("order", response_data, "Update response missing 'order' key")
        self.assertEqual(response_data["order"]["status"], "shipped", "Order status did not update correctly")

        print("test_update_order_status succeeded")

    def test_get_order_details(self):
        """Test if order details API returns the correct order and shipping cost."""
        print("Running test_get_order_details")

        # Wait for Kafka to process the order update before checking details
        time.sleep(5)

        response = requests.get(
            f"{ORDER_SERVICE_URL}/order-details",
            params={"orderId": self.order_id},
        )

        self.assertEqual(response.status_code, 200, "Failed to fetch order details")
        order_data = response.json()

        self.assertIn("orderId", order_data, "Response missing orderId")
        self.assertIn("shippingCost", order_data, "Response missing shippingCost")
        self.assertEqual(order_data["orderId"], self.order_id, "Incorrect order ID")
        self.assertGreater(order_data["shippingCost"], 0, "Shipping cost should be greater than 0")

        print("test_get_order_details succeeded")

    def test_get_all_order_ids_from_topic(self):
        """Test if Kafka consumer correctly retrieves order IDs."""
        print("Running test_get_all_order_ids_from_topic")

        # Ensure Kafka has time to process the order
        max_retries = 5
        retries = 0
        order_found = False

        while retries < max_retries:
            response = requests.get(
                f"{ORDER_SERVICE_URL}/getAllOrderIdsFromTopic",
                params={"topic": "order_events"},
            )

            self.assertEqual(response.status_code, 200, "Failed to fetch order IDs from topic")
            response_data = response.json()
            self.assertIn("orderIds", response_data, "Response missing 'orderIds' key")

            if self.order_id in response_data["orderIds"]:
                order_found = True
                break  # Exit the loop if the order ID is found

            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")
            time.sleep(2)  # Wait before retrying

        self.assertTrue(order_found, "Order ID not found in topic messages after retries")

        print("test_get_all_order_ids_from_topic succeeded")

    def test_invalid_order_creation(self):
        """Test if invalid order creation returns an error."""
        print("Running test_invalid_order_creation")

        response = requests.post(
            f"{CART_SERVICE_URL}/create-order",
            json={"orderId": "", "itemsNum": -1},  # Invalid input
        )

        self.assertEqual(response.status_code, 400, "Expected 400 for invalid order creation")
        self.assertIn("error", response.json(), "Error response missing")

        print("test_invalid_order_creation succeeded")

    def test_invalid_order_update(self):
        """Test if updating a non-existing order returns an error."""
        print("Running test_invalid_order_update")

        response = requests.put(
            f"{CART_SERVICE_URL}/update-order",
            json={"orderId": "NON-EXISTENT-ORDER", "status": "shipped"},
        )

        self.assertEqual(response.status_code, 400, "Expected 400 for updating a non-existing order")
        self.assertIn("error", response.json(), "Error response missing")

        print("test_invalid_order_update succeeded")

    def test_invalid_order_details(self):
        """Test if fetching non-existing order details returns 404."""
        print("Running test_invalid_order_details")

        response = requests.get(
            f"{ORDER_SERVICE_URL}/order-details",
            params={"orderId": "NON-EXISTENT-ORDER"},
        )

        self.assertEqual(response.status_code, 404, "Expected 404 for non-existent order")
        self.assertIn("error", response.json(), "Error response missing")

        print("test_invalid_order_details succeeded")

if __name__ == "__main__":
    unittest.main()
