from curl_cffi import requests as cr

s = cr.Session(impersonate="chrome")
r = s.get("https://muse.ai/")
print("Landing:", r.status_code)
r2 = s.post("https://muse.ai/api/auth/native/restart", json={})
print("Restart:", r2.status_code, r2.text)
