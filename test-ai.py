import requests

API_KEY = "AIzaSyCoTDJBJwL1DzRWEWMPvuDBcImoeqhLCqM"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

resp = requests.get(url, timeout=10)
print(resp.status_code)
print(resp.text)

