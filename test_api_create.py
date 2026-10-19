import requests
API_KEY = "hb_cdfc571755daac8231b0c1812ec4"
headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
res = requests.post("https://api.hyperbrowser.ai/api/session", headers=headers, json={}, timeout=10)
print(res.status_code, res.text[:300])
