from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

try:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "testclient@test.com", "password": "password123"}
    )
    print("STATUS_CODE:", response.status_code)
    print("JSON_RESPONSE:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
