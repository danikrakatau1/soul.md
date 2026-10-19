import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import urllib3, uuid, requests, re, time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print("Session created:", session.id)

domain = requests.get("https://box.celana-ar-store.my.id/domains", verify=False).json()["hydra:member"][0]["domain"]
email = f"bot_{uuid.uuid4().hex[:8]}@{domain}"
requests.post("https://box.celana-ar-store.my.id/accounts", json={"address": email, "password": "SecurePass123!"}, verify=False)
t_res = requests.post("https://box.celana-ar-store.my.id/token", json={"address": email, "password": "SecurePass123!"}, verify=False)
token = t_res.json()["token"]
print("Email created:", email)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.ws_endpoint)
    page = browser.context.new_page() if hasattr(browser, 'context') else browser.new_context().new_page()
    page.goto("https://muse.ai/", timeout=60000)
    time.sleep(3)

    r1 = page.evaluate("async () => { let r = await fetch('/api/auth/native/restart', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({})}); return await r.json(); }")
    csrf = r1.get("csrf_token")

    r2 = page.evaluate("async (data) => { let r = await fetch('/api/auth/native/send-otp', {method:'POST', headers:{'Content-Type':'application/json', 'x-hatch-csrf-token':data.csrf}, body:JSON.stringify({'contact_point':data.email, 'region':'US'})}); return {status: r.status, text: await r.text()}; }", {"csrf": csrf, "email": email})
    print("Send OTP:", r2)

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
    print("OTP retrieved via API:", otp)

    if otp:
        time.sleep(2)
        conf = page.evaluate("async (data) => { let r = await fetch('/api/auth/native/confirm-otp', {method:'POST', headers:{'Content-Type':'application/json', 'x-hatch-csrf-token':data.csrf}, body:JSON.stringify({'otp_code':data.otp})}); return {status: r.status, json: await r.json()}; }", {"csrf": csrf, "otp": otp})
        print("API Confirm OTP:", conf)

        reg = page.evaluate("async (data) => { let r = await fetch('/api/auth/native/register-completion', {method:'POST', headers:{'Content-Type':'application/json', 'x-hatch-csrf-token':data.csrf}, body:JSON.stringify({'date_of_birth':'1995-05-15', 'first_name':'Miauru', 'last_name':'Juanda', 'tos_content_version':'ntm_create_account:default_v1_meta_account_v2+docs_v1'})}); return {status: r.status, json: await r.json()}; }", {"csrf": csrf})
        print("API Register Completion:", reg)

        redeem = page.evaluate("async () => { let r = await fetch('/api/hatch/invite-code/redeem', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({'code':'FO3DHT', 'supportsRedemptionStatus':true})}); return await r.json(); }")
        print("API Redeem:", redeem)

        time.sleep(3)
        page.reload()
        time.sleep(3)
        page.screenshot(path="/home/agentuser/muse/screenshot_final.png")
        print("Screenshot saved.")

    browser.close()

client.sessions.stop(session.id)
