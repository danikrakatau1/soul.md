import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright

client = Hyperbrowser(api_key="hb_cdfc571755daac8231b0c1812ec4")
session = client.sessions.create()

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://ip-api.com/json/", timeout=30000)
        print("IP Info:", page.locator("body").inner_text())
        browser.close()
finally:
    client.sessions.stop(session.id)
