import requests
import time

login = "user_9189_1792344613"
domain = "1secmail.com"
url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
res = requests.get(url, timeout=10)
print("Status:", res.status_code)
print("Response:", res.text)
