from fastapi.testclient import TestClient
import sys
import traceback
from app.core.config import settings

print(f"DEBUG: settings.MONGO_URI = {settings.MONGO_URI}")

try:
    from app.main import app
    client = TestClient(app)
    
    import uuid
    sys.modules["app.models.user"] = None # Hack to prevent leftover import errors if any? No need.

    random_email = f"user_{uuid.uuid4()}@example.com"
    
    payload = {
        "email": random_email,
        "password": "password123",
        "full_name": "Random Test",
        "target_role": "Backend"
    }

    print("--- SENDING REQUEST ---")
    response = client.post("/api/v1/auth/signup", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

except Exception:
    traceback.print_exc()
