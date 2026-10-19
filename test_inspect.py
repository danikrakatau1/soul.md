import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright

client = Hyperbrowser(api_key="hb_cdfc571755daac8231b0c1812ec4")
session = client.sessions.create()

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        page = browser.new_context().new_page()
        page.goto("https://muse.ai/", timeout=60000)
        import time; time.sleep(5)
        print("Page HTML snippet:", page.content()[:1000])
        browser.close()
finally:
    client.sessions.stop(session.id)
