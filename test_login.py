import requests
import json

url = "http://localhost:8000/api/auth/login/"

# 测试1: 使用JSON数据
print("测试1: 使用JSON数据")
data_json = {
    "username": "testuser",
    "password": "testpass123"
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=data_json, headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

# 测试2: 使用表单数据
print("\n测试2: 使用表单数据")
data_form = {
    "username": "testuser",
    "password": "testpass123"
}
headers_form = {"Content-Type": "application/x-www-form-urlencoded"}
response2 = requests.post(url, data=data_form, headers=headers_form)
print(f"状态码: {response2.status_code}")
print(f"响应: {response2.text}")

# 测试3: 不带Content-Type头
print("\n测试3: 不带Content-Type头")
response3 = requests.post(url, data=data_form)
print(f"状态码: {response3.status_code}")
print(f"响应: {response3.text}")
