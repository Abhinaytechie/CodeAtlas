import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Add the parent directory to sys.path to import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.core.config import settings

def test_connection():
    print("Testing MongoDB Connection...")
    print(f"URI configured: {settings.MONGO_URI.split('@')[-1] if '@' in settings.MONGO_URI else 'Local/Invalid'}")
    
    try:
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("Server is available.")
        
        # Now try to get the database
        db = client[settings.DB_NAME]
        print(f"Successfully connected to database: {settings.DB_NAME}")
        
        # Optional: List collection names to verify auth
        print("Collections:", db.list_collection_names())
        
    except ConnectionFailure:
        print("Server not available. Please check your network or URI.")
    except OperationFailure as e:
        print(f"Authentication failed or other operation error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_connection()
