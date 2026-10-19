import requests
import uuid
import urllib3
import re
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Let us test mail.tm + pure requests with session
s = requests.Session()
s.verify = False

# 1. Create mail.tm
res = s.get("https://box.celana-ar-store.my.id/domains")
domain = res.json()["hydra:member"][0]["domain"]
email = f"bot_{uuid.uuid4().hex[:8]}@{domain}"
s.post("https://box.celana-ar-store.my.id/accounts", json={"address": email, "password": "SecurePass123!"})
t_res = s.post("https://box.celana-ar-store.my.id/token", json={"address": email, "password": "SecurePass123!"})
token = t_res.json()["token"]
print("Email:", email)

# 2. Hit muse.ai via curl_cffi or requests with chrome impersonation
from curl_cffi import requests as cr
cs = cr.Session(impersonate="chrome")
r1 = cs.post("https://muse.ai/api/auth/native/restart", json={})
print("Restart:", r1.status_code, r1.text[:200])
csrf = r1.json().get("csrf_token")
print("CSRF:", csrf)

r2 = cs.post("https://muse.ai/api/auth/native/send-otp", json={"contact_point": email, "region": "US"}, headers={"x-hatch-csrf-token": csrf})
print("Send OTP:", r2.status_code, r2.text)
