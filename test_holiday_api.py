import requests
import json

# Replace with your actual token
token = input("Enter your JWT token: ")

# Base URL
base_url = "http://127.0.0.1:8001"

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test GET holidays endpoint
print("\nTesting GET /api/holidays/")
response = requests.get(f"{base_url}/api/holidays/", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test POST to update country code
print("\nTesting POST /api/holidays/")
country_code = input("Enter country code (e.g., US, GB, DE): ")
data = {"country_code": country_code}
response = requests.post(f"{base_url}/api/holidays/", headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test GET holidays again to see updated holidays
print("\nTesting GET /api/holidays/ after update")
response = requests.get(f"{base_url}/api/holidays/", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")