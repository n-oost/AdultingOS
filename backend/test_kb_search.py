"""
Quick test script for the /kb search endpoint.
Run this after starting the FastAPI server.
"""
import requests
import json
import time

# Wait a moment for server to be ready
time.sleep(1)

try:
    # Test the /kb search endpoint
    response = requests.post(
        'http://127.0.0.1:8001/assistant/chat',
        json={'message': '/kb search TD1 Ontario 2025'},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.ConnectionError:
    print("❌ Server is not running on http://127.0.0.1:8001")
    print("Start it with: cd backend && uvicorn main:app --host 127.0.0.1 --port 8001 --reload")
except Exception as e:
    print(f"❌ Error: {e}")
