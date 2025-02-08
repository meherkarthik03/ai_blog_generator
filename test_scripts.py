import requests

url = "http://127.0.0.1:5000/generate"
data = {"topic": "The future of AI in healthcare"}

response = requests.post(url, json=data)  # Ensure JSON format
print("Response:", response.json())  # Print generated blog content
