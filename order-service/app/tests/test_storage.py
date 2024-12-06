import os

import json
import pytest
from app.storage import load_from_file, save_to_file, storage

# Define a test storage file path
TEST_STORAGE_FILE = "test_storage.json"

# Override the storage file path in the module
os.environ["STORAGE_FILE"] = TEST_STORAGE_FILE

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for tests."""
    # Ensure a clean state before each test
    if os.path.exists(TEST_STORAGE_FILE):
        os.remove(TEST_STORAGE_FILE)
    yield
    # Cleanup after each test
    if os.path.exists(TEST_STORAGE_FILE):
        os.remove(TEST_STORAGE_FILE)

def test_load_from_file():
    """Test loading from a JSON file."""
    # Write test data to the file
    test_data = {"ORD-12345": {"orderId": "ORD-12345", "customerId": "123"}}
    with open(TEST_STORAGE_FILE, "w") as f:
        json.dump(test_data, f)

    # Call the function
    load_from_file()

    # Assert the storage is loaded correctly
    assert "ORD-12345" in storage
    assert storage["ORD-12345"]["customerId"] == "123"

def test_save_to_file():
    """Test saving to a JSON file."""
    # Update storage
    storage["ORD-67890"] = {"orderId": "ORD-67890", "customerId": "456"}

    # Call the function
    save_to_file()

    # Assert the file contains the correct data
    with open(TEST_STORAGE_FILE, "r") as f:
        data = json.load(f)
    assert "ORD-67890" in data
    assert data["ORD-67890"]["customerId"] == "456"
