import requests
import json

url = "http://localhost:8000/api/students/"
data = {
    "student_id": "S001",
    "user": 3,
    "enrollment_date": "2023-09-01",
    "status": "active"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

# 也尝试使用data参数
response2 = requests.post(url, data=json.dumps(data), headers=headers)
print(f"\n使用data参数:")
print(f"状态码: {response2.status_code}")
print(f"响应: {response2.text}")
