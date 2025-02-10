# In-memory storage for orders
import json

# File path for persistent storage
STORAGE_FILE = "storage.json"

# In-memory storage
storage = {}

def save_to_file():
    """Save storage to a JSON file."""
    with open(STORAGE_FILE, "w") as f:
        json.dump(storage, f)

def load_from_file():
    global storage
    try:
        with open(STORAGE_FILE, "r") as f:
            file_content = f.read()
            print("Reading storage file...")
            storage = json.loads(file_content)
    except FileNotFoundError:
        storage = {}
        print("Storage file not found. Using empty storage.")
    except json.JSONDecodeError as e:
        storage = {}
        print(f"Error decoding JSON file: {e}")



