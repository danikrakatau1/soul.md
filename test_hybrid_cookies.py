import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
from curl_cffi import requests as cr
import urllib3, time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print("Session created:", session.id)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.ws_endpoint)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://muse.ai/", timeout=60000)
    time.sleep(4)

    # Extract cookies from Playwright context
    pw_cookies = context.cookies()
    print("Extracted cookies count:", len(pw_cookies))

    # Create curl_cffi session with chrome impersonation
    s = cr.Session(impersonate="chrome")
    
    # Add cookies to curl_cffi
    for cookie in pw_cookies:
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    # Test API restart request via curl_cffi
    headers = {
        'Accept': '*/*',
        'Referer': 'https://muse.ai/',
        'Origin': 'https://muse.ai',
        'Content-Type': 'application/json'
    }
    r = s.post("https://muse.ai/api/auth/native/restart", json={}, headers=headers, timeout=30)
    print("Restart response via curl_cffi with cookies:", r.status_code, r.text[:300])

    browser.close()

client.sessions.stop(session.id)
