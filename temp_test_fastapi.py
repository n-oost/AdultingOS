import requests
import json

# --- Configuration ---
DJANGO_BASE_URL = "http://127.0.0.1:8000/api"
FASTAPI_BASE_URL = "http://127.0.0.1:8001"
LOGIN_CREDENTIALS = {
    "username": "testuser",
    "password": "testpass123"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response):
    """Print formatted response details"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except json.JSONDecodeError:
        print(f"Response Text: {response.text}")

# --- Step 1: Authenticate with Django to get a token ---
print_section("Step 1: Authenticate with Django")
token = None
try:
    login_response = requests.post(f"{DJANGO_BASE_URL}/auth/login/", json=LOGIN_CREDENTIALS)
    print_response(login_response)

    if login_response.status_code == 200:
        token = login_response.json().get('token')
        print(f"\n✅ Successfully retrieved token: {token}")
    else:
        print("\n❌ Failed to authenticate with Django. Please ensure the Django server is running and migrations are applied.")
        exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection to Django server failed: {e}")
    print("Please ensure the Django server is running on http://127.0.0.1:8000.")
    exit(1)


# --- Step 2: Call FastAPI /chat endpoint with the token ---
print_section("Step 2: Call FastAPI /chat endpoint")

if not token:
    print("\n❌ No token available. Exiting.")
    exit(1)

# FastAPI's OAuth2PasswordBearer expects "Bearer <token>"
chat_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
# The endpoint expects a body with a "message" field
chat_data = {
    "message": "Hello, this is a test message."
}

try:
    chat_response = requests.post(f"{FASTAPI_BASE_URL}/chat", headers=chat_headers, json=chat_data)
    print_response(chat_response)

    if chat_response.status_code == 200:
        print("\n✅ Successfully called FastAPI /chat endpoint.")
        print("The response body should contain the user's profile from Django.")
    else:
        print("\n❌ Failed to call FastAPI /chat endpoint.")

except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection to FastAPI server failed: {e}")
    print("Please ensure the FastAPI server is running on http://127.0.0.1:8001.")
    exit(1)
