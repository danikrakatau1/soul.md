import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Let us see what headers are needed for restart or if Hyperbrowser proxy/session cookies are needed
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Origin": "https://muse.ai",
    "Referer": "https://muse.ai/"
})
r = s.post("https://muse.ai/api/auth/native/restart", json={})
print(r.status_code, r.text)
