import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Create user
print("=" * 50)
print("TEST 1: Create User")
print("=" * 50)
response = requests.post(f"{BASE_URL}/api/user/create?username=test_user_1")
print(f"Status: {response.status_code}")
user = response.json()
print(f"Response: {json.dumps(user, indent=2)}")
user_id = user.get("id")

# Test 2: Send chat message
if user_id:
    print("\n" + "=" * 50)
    print(f"TEST 2: Send Chat Message (User ID: {user_id})")
    print("=" * 50)
    
    response = requests.post(
        f"{BASE_URL}/chat?user_id={user_id}",
        json={
            "message": "Hello! What is 2+2?",
            "forced_role": None
        }
    )
    print(f"Status: {response.status_code}")
    if response.ok:
        print("Response (streaming):")
        for line in response.iter_lines():
            if line:
                print(f"  {line.decode()}")
    else:
        print(f"Error: {response.text}")

# Test 3: Get chat history
if user_id:
    print("\n" + "=" * 50)
    print(f"TEST 3: Get Chat History (User ID: {user_id})")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/chat/history/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
