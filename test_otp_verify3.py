import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import urllib3, uuid, requests, re, time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()

domain = requests.get("https://box.celana-ar-store.my.id/domains", verify=False).json()["hydra:member"][0]["domain"]
email = f"bot_{uuid.uuid4().hex[:8]}@{domain}"
requests.post("https://box.celana-ar-store.my.id/accounts", json={"address": email, "password": "SecurePass123!"}, verify=False)
t_res = requests.post("https://box.celana-ar-store.my.id/token", json={"address": email, "password": "SecurePass123!"}, verify=False)
token = t_res.json()["token"]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.ws_endpoint)
    page = browser.new_context().new_page()
    page.goto("https://muse.ai/", timeout=60000)
    time.sleep(3)

    r1 = page.evaluate("async () => { let r = await fetch('/api/auth/native/restart', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({})}); return await r.json(); }")
    csrf = r1.get("csrf_token")

    # Use UI typing for send-otp or fetch
    page.locator("input[placeholder='Mobile number or email']").fill(email)
    time.sleep(1)
    page.locator("button[type='submit']", has_text="Continue").click()

    # Wait for OTP
    otp = None
    for _ in range(30):
        m_res = requests.get("https://box.celana-ar-store.my.id/messages", headers={"Authorization": f"Bearer {token}"}, verify=False)
        msgs = m_res.json().get("hydra:member", [])
        if msgs:
            msg_id = msgs[0]["id"]
            body = requests.get(f"https://box.celana-ar-store.my.id/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"}, verify=False).json().get("text", "")
            match = re.search(r'Confirmation code\s*(\d{6})', body)
            if match:
                otp = match.group(1)
                break
        time.sleep(3)
    print("UI Flow OTP found:", otp)

    if otp:
        time.sleep(2)
        page.keyboard.type(otp, delay=150)
        time.sleep(5)
        page.screenshot(path="/home/agentuser/muse/screenshot_final.png")

    browser.close()

client.sessions.stop(session.id)
