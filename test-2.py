import unittest
import requests
import time
import threading
import random

# Base URLs for the services
CART_SERVICE_URL = "http://localhost:5000"
ORDER_SERVICE_URL = "http://localhost:5001"

# A sample list of statuses to use in updates
STATUSES = ["processing", "shipped", "delivered", "cancelled"]

def update_order(order_id, status):
    """Helper function to update an order's status."""
    url = f"{CART_SERVICE_URL}/update-order"
    payload = {"orderId": order_id, "status": status}
    try:
        response = requests.put(url, json=payload)
        return response
    except Exception as e:
        print(f"Error updating order {order_id} to status {status}: {e}")
        return None

class TestAdvancedEcommerceSystem(unittest.TestCase):
    def setUp(self):
        """
        Create a new order that will be used in sequential and concurrent update tests.
        """
        self.order_id = f"ADV-ORDER-{int(time.time() * 1000)}"
        self.items_num = random.randint(2, 5)
        url = f"{CART_SERVICE_URL}/create-order"
        response = requests.post(url, json={"orderId": self.order_id, "itemsNum": self.items_num})
        self.assertEqual(response.status_code, 201, "Advanced order creation failed")
        # Wait for Kafka processing
        time.sleep(10)

    def test_sequential_updates(self):
        """
        Update the same order multiple times in sequence and then verify the final state.
        """
        statuses_to_apply = ["processing", "shipped", "delivered"]
        for status in statuses_to_apply:
            response = update_order(self.order_id, status)
            self.assertIsNotNone(response, "No response received during sequential update")
            self.assertEqual(response.status_code, 200, f"Failed to update order to {status}")
            time.sleep(3)  # Give Kafka time to process the update

        # Retrieve final order details
        details_url = f"{ORDER_SERVICE_URL}/order-details"
        response = requests.get(details_url, params={"orderId": self.order_id})
        self.assertEqual(response.status_code, 200, "Failed to retrieve final order details")
        order_data = response.json()
        self.assertEqual(order_data.get("status"), "delivered", "Final order status is not 'delivered'")
        self.assertIn("shippingCost", order_data, "Shipping cost missing in final order details")
        self.assertGreater(order_data["shippingCost"], 0, "Shipping cost should be greater than 0")

    def test_bulk_order_creation_and_topic_retrieval(self):
        """
        Create multiple orders and verify that all their IDs appear in the Kafka topic listing.
        """
        created_orders = []
        num_orders = 5
        for i in range(num_orders):
            order_id = f"BULK-ORDER-{int(time.time() * 1000)}-{i}"
            response = requests.post(f"{CART_SERVICE_URL}/create-order", 
                                     json={"orderId": order_id, "itemsNum": random.randint(1, 4)})
            self.assertEqual(response.status_code, 201, f"Order creation failed for {order_id}")
            created_orders.append(order_id)
            time.sleep(1)  # Stagger order creation

        # Wait a bit longer for Kafka to process all events
        time.sleep(10)

        # Retrieve order IDs from Kafka topic
        topic_url = f"{ORDER_SERVICE_URL}/getAllOrderIdsFromTopic"
        response = requests.get(topic_url, params={"topic": "order_events"})
        self.assertEqual(response.status_code, 200, "Failed to fetch order IDs from topic")
        data = response.json()
        self.assertIn("orderIds", data, "Response missing 'orderIds' key")
        topic_order_ids = data["orderIds"]

        for order_id in created_orders:
            self.assertIn(order_id, topic_order_ids, f"Order ID {order_id} not found in Kafka topic")

    def test_concurrent_order_updates(self):
        """
        Update the same order concurrently using multiple threads and then check that the final update is valid.
        """
        # Define a worker that updates the order with a random status
        def worker_update(order_id):
            status = random.choice(STATUSES)
            response = update_order(order_id, status)
            if response is not None:
                print(f"Updated {order_id} to {status} with status code {response.status_code}")

        # Launch multiple threads to update the same order
        threads = []
        num_threads = 5
        for _ in range(num_threads):
            thread = threading.Thread(target=worker_update, args=(self.order_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Wait for Kafka processing
        time.sleep(10)

        # Fetch final order details
        details_url = f"{ORDER_SERVICE_URL}/order-details"
        response = requests.get(details_url, params={"orderId": self.order_id})
        self.assertEqual(response.status_code, 200, "Failed to retrieve order details after concurrent updates")
        order_data = response.json()
        # Verify that the final status is one of the possible statuses
        self.assertIn(order_data.get("status"), STATUSES,
                      "Final order status is not in the expected list after concurrent updates")
        self.assertGreater(order_data.get("shippingCost", 0), 0,
                           "Shipping cost should be computed and greater than 0 after concurrent updates")

    def test_invalid_update_payloads(self):
        """
        Send invalid payloads to the update endpoint and verify proper error responses.
        """
        # Missing orderId
        response = requests.put(f"{CART_SERVICE_URL}/update-order", json={"status": "shipped"})
        self.assertIn(response.status_code, [400, 500], "Expected error status for missing orderId")
        self.assertIn("error", response.json(), "Expected error message for missing orderId")

        # Missing status
        response = requests.put(f"{CART_SERVICE_URL}/update-order", json={"orderId": self.order_id})
        self.assertIn(response.status_code, [400, 500], "Expected error status for missing status")
        self.assertIn("error", response.json(), "Expected error message for missing status")

        # Incorrect data type for status (should be a string)
        response = requests.put(f"{CART_SERVICE_URL}/update-order", json={"orderId": self.order_id, "status": 123})
        self.assertIn(response.status_code, [400, 500], "Expected error status for invalid status type")
        self.assertIn("error", response.json(), "Expected error message for invalid status type")

if __name__ == "__main__":
    unittest.main()
