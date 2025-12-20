from pymongo import MongoClient
from app.core.config import settings

# Hardcoded to bypass persistent environment variable conflicts
# client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[settings.DB_NAME]

def get_db():
    yield db
