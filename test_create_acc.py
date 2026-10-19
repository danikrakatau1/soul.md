import requests
import uuid
base_url = "https://box.celana-ar-store.my.id"
username = f"bot_{uuid.uuid4().hex[:8]}"
email = f"{username}@maxxspace.com"
res = requests.post(f"{base_url}/accounts", json={"address": email, "password": "SecurePass123!"}, verify=False)
print(res.status_code, res.text)
