from curl_cffi import requests as cr
import requests

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"
DASAR_MUSE = "https://muse.ai"

# Let us create a session via Hyperbrowser API to get session details or cookies if available
# Or use curl_cffi with impersonate="chrome"
s = cr.Session(impersonate="chrome")
r = s.get(DASAR_MUSE + "/")
print("Landing status:", r.status_code)

r_restart = s.post(DASAR_MUSE + "/api/auth/native/restart", json={})
print("Restart status:", r_restart.status_code, r_restart.text[:200])
