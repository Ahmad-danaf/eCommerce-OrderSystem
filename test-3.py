import unittest
import requests
import time
import math

# Base URLs for the services
CART_SERVICE_URL = "http://localhost:5000"
ORDER_SERVICE_URL = "http://localhost:5001"

class TestOrderDetailsUpdate(unittest.TestCase):
    def setUp(self):
        """
        Create a new order and save its details.
        """
        # Create a unique order id using a timestamp
        self.order_id = f"ORD-TEST-{int(time.time() * 1000)}"
        self.items_num = 3  # You can adjust the number of items if needed
        
        create_url = f"{CART_SERVICE_URL}/create-order"
        payload = {"orderId": self.order_id, "itemsNum": self.items_num}
        response = requests.post(create_url, json=payload)
        self.assertEqual(response.status_code, 201, "Order creation failed.")
        
        data = response.json()
        self.creation_order = data.get("order", {})
        # Note: the creation response may not include shippingCost yet.
        self.total_amount = self.creation_order.get("totalAmount", 0)
        # Compute expected shipping cost: 2% of totalAmount rounded to 2 decimals.
        self.expected_shipping_cost = round(self.total_amount * 0.02, 2)
        
        # Allow time for Kafka to process the new order
        time.sleep(10)
    
    def test_create_get_update_get_order_details(self):
        # STEP 1: Get order details after creation
        get_url = f"{ORDER_SERVICE_URL}/order-details"
        params = {"orderId": self.order_id}
        response = requests.get(get_url, params=params)
        self.assertEqual(response.status_code, 200, "Failed to get order details after creation.")
        order_details_initial = response.json()
        
        # Check that order details match what was created
        self.assertEqual(order_details_initial.get("orderId"), self.order_id, "OrderId does not match in initial GET.")
        self.assertEqual(order_details_initial.get("currency"), self.creation_order.get("currency"), "Currency mismatch in initial GET.")
        self.assertEqual(order_details_initial.get("customerId"), self.creation_order.get("customerId"), "CustomerId mismatch in initial GET.")
        self.assertEqual(order_details_initial.get("totalAmount"), self.total_amount, "Total amount mismatch in initial GET.")
        
        # Check that shipping cost is computed and correct
        self.assertIn("shippingCost", order_details_initial, "Shipping cost missing in initial order details.")
        self.assertEqual(order_details_initial.get("shippingCost"), self.expected_shipping_cost,
                         f"Expected shipping cost {self.expected_shipping_cost} but got {order_details_initial.get('shippingCost')}")
        
        # STEP 2: Update the order status
        update_url = f"{CART_SERVICE_URL}/update-order"
        update_payload = {"orderId": self.order_id, "status": "delivered"}
        update_response = requests.put(update_url, json=update_payload)
        self.assertEqual(update_response.status_code, 200, "Order update failed.")
        update_data = update_response.json()
        self.assertEqual(update_data.get("order", {}).get("status"), "delivered", "Order status not updated to delivered.")
        
        # Allow time for Kafka to process the update event
        time.sleep(10)
        
        # STEP 3: Get order details after update
        response_after = requests.get(get_url, params=params)
        self.assertEqual(response_after.status_code, 200, "Failed to get order details after update.")
        order_details_after = response_after.json()
        
        # Check that the order details reflect the updated status
        self.assertEqual(order_details_after.get("orderId"), self.order_id, "OrderId does not match after update.")
        self.assertEqual(order_details_after.get("status"), "delivered", "Order status not updated in GET details.")
        
        # Ensure that shipping cost remains the same (computed from totalAmount)
        self.assertIn("shippingCost", order_details_after, "Shipping cost missing in updated order details.")
        self.assertEqual(order_details_after.get("shippingCost"), self.expected_shipping_cost,
                         f"Expected shipping cost {self.expected_shipping_cost} after update but got {order_details_after.get('shippingCost')}")
        
        # Optionally: Check that other details (currency, totalAmount, etc.) remain unchanged
        self.assertEqual(order_details_after.get("currency"), self.creation_order.get("currency"), "Currency mismatch after update.")
        self.assertEqual(order_details_after.get("totalAmount"), self.total_amount, "Total amount mismatch after update.")

if __name__ == "__main__":
    unittest.main()
