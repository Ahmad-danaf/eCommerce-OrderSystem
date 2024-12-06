from app.storage import load_from_file,save_to_file

def process_order(order):
    try:
        load_from_file()
        from app.storage import storage
        # Calculate shipping cost (2% of totalAmount)
        total_amount = order.get("totalAmount", 0)
        shipping_cost = round(total_amount * 0.02, 2)

        # Add shipping cost to the order details
        order["shippingCost"] = shipping_cost

        # Log and store the order
        print(f"Processed Order: {order}")
        storage[order["orderId"]] = order
        save_to_file()
    except Exception as e:
        print(f"Error processing order: {e}")
        raise
