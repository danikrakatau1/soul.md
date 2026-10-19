import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"
client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print("Created session:", session.id)

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        page = browser.new_context().new_page()
        
        # Navigate to muse.ai and execute the API call directly in browser context!
        page.goto("https://muse.ai/", timeout=60000)
        import time; time.sleep(3)
        
        # Execute fetch/post via page.evaluate to leverage the browser session cookies and US IP natively!
        resp = page.evaluate("""async () => {
            let r1 = await fetch('/api/auth/native/restart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
            let data1 = await r1.json();
            return data1;
        }""")
        print("Browser JS fetch result (restart):", resp)
        
        browser.close()
finally:
    client.sessions.stop(session.id)
