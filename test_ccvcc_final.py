import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import time, requests, uuid, re, json
requests.packages.urllib3.disable_warnings()

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"
REF_CODE = "FO3DHT"

def make_email():
    domains = requests.get("https://box.celana-ar-store.my.id/domains", verify=False, timeout=10).json()
    domain = domains["hydra:member"][0]["domain"]
    username = f"bot_{uuid.uuid4().hex[:8]}"
    email = f"{username}@{domain}"
    password = "SecurePass123!"
    requests.post("https://box.celana-ar-store.my.id/accounts", json={"address": email, "password": password}, verify=False, timeout=10)
    token = requests.post("https://box.celana-ar-store.my.id/token", json={"address": email, "password": password}, verify=False, timeout=10).json().get("token")
    return email, password, token

def get_otp(token):
    msgs = requests.get("https://box.celana-ar-store.my.id/messages", headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=10).json().get("hydra:member", [])
    if msgs:
        msg = requests.get(f"https://box.celana-ar-store.my.id/messages/{msgs[0]['id']}", headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=10).json()
        body = msg.get("text") or msg.get("intro") or ""
        m = re.search(r"\b\d{6}\b", body)
        if m:
            return m.group(0)
    return None

print("=" * 60)
print("REGISTER FRESH + REDEEM + CEK CHECKPOINT CC/VCC")
print("=" * 60)

email, password, mail_token = make_email()
print(f"\n[1] FRESH EMAIL: {email}")

client = Hyperbrowser(api_key=API_KEY)

# Cleanup existing sessions
resp = client.sessions.list()
for s in resp.sessions:
    if s.status == "active":
        client.sessions.stop(s.id)
        print(f"  Stopped existing: {s.id}")

session = client.sessions.create()
print(f"\n[2] SESSION: {session.id}")

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://muse.ai/", timeout=60000)
        time.sleep(3)

        # Register flow
        res_data = page.evaluate("""async () => {
            let r1 = await fetch('/api/auth/native/restart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
            let d1 = await r1.json();
            let csrf = d1.csrf_token;
            let r2 = await fetch('/api/auth/native/send-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-hatch-csrf-token': csrf
                },
                body: JSON.stringify({contact_point: '%s', region: 'US'})
            });
            return {status: r2.status, csrf: csrf};
        }""" % email)
        print(f"[3] SEND OTP: {res_data}")

        # Delay 30 detik
        print("[*] Tunggu 30 detik...")
        time.sleep(30)

        # Tunggu OTP
        otp = None
        for i in range(40):
            otp = get_otp(mail_token)
            if otp:
                break
            if i % 5 == 4:
                print(f"  [{i+1}/40] Nunggu OTP...")
            time.sleep(6)

        if not otp:
            print("[-] OTP gak masuk!")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        print(f"[4] OTP: {otp}")

        time.sleep(15)

        # Confirm OTP
        conf = page.evaluate("""async (data) => {
            let r = await fetch('/api/auth/native/confirm-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-hatch-csrf-token': data.csrf
                },
                body: JSON.stringify({otp_code: data.otp})
            });
            return {status: r.status, json: await r.json()};
        }""", {"csrf": res_data["csrf"], "otp": otp})
        print(f"[5] CONFIRM OTP: {conf}")

        if conf.get("status") not in [200, 201]:
            print(f"[-] Confirm gagal! Status: {conf.get('status')}")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        time.sleep(5)

        # Register completion
        reg = page.evaluate("""async (data) => {
            let r = await fetch('/api/auth/native/register-completion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-hatch-csrf-token': data.csrf
                },
                body: JSON.stringify({
                    date_of_birth: data.dob,
                    first_name: data.depan,
                    last_name: data.tukang,
                    tos_content_version: 'ntm_create_account:default_v1_meta_account_v2+docs_v1'
                })
            });
            return {status: r.status, json: await r.json()};
        }""", {"csrf": res_data["csrf"], "dob": "1995-05-15", "depan": "Sari", "tukang": "Wijaya"})
        print(f"[6] REGISTER: {reg}")

        if reg.get("status") not in [200, 201]:
            print(f"[-] Register gagal!")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        time.sleep(5)

        # Redeem
        print(f"\n[7] REDEEM REFERRAL ({REF_CODE})...")
        redeem = page.evaluate("""async (code) => {
            let r = await fetch('/api/hatch/invite-code/redeem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code, supportsRedemptionStatus: true})
            });
            return {status: r.status, json: await r.json()};
        }""", REF_CODE)
        print(f"    Result: {json.dumps(redeem, indent=2)}")

        checkpoint_url = redeem.get("json", {}).get("checkpoint_url")
        if not checkpoint_url:
            print("    Gak ada checkpoint URL")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(0)

        # BUKA CHECKPOINT
        print(f"\n[8] BUKA CHECKPOINT: {checkpoint_url}")
        page.goto(checkpoint_url, timeout=60000)
        time.sleep(5)

        print(f"[9] URL: {page.url}")
        print(f"[10] TITLE: {page.title()}")

        # DETAILED ANALYSIS
        print(f"\n{'='*60}")
        print("ANALYSIS: CC/VCC CHECK")
        print(f"{'='*60}")

        page_text = page.evaluate("() => document.body.innerText")
        print(f"\nPAGE TEXT:\n{page_text[:2000]}")

        keywords = ["credit card", "debit card", "cc", "vcc", "payment", "billing",
                     "card number", "cvv", "expiry", "age verification", "date of birth",
                     "birthday", "verify", "identity", "id", "upload", "camera",
                     "face", "scan", "document", "passport", "license"]

        print(f"\nKEYWORD CHECK:")
        text_lower = page_text.lower()
        found_any = False
        for kw in keywords:
            if kw in text_lower:
                idx = text_lower.find(kw)
                context = page_text[max(0, idx-40):idx+len(kw)+40]
                print(f"  ✓ '{kw}': ...{context}...")
                found_any = True
        if not found_any:
            print("  (gak ada keywords CC/VCC)")

        # Input fields
        inputs = page.locator("input, select, textarea").all()
        print(f"\nFORM INPUTS ({len(inputs)}):")
        for i, inp in enumerate(inputs):
            try:
                itype = inp.get_attribute("type")
                name = inp.get_attribute("name")
                placeholder = inp.get_attribute("placeholder")
                visible = inp.is_visible()
                if visible:
                    print(f"  [{i}] type={itype} name={name} placeholder={placeholder}")
            except:
                pass

        # Clickable
        clickables = page.locator("button, a, [role=button]").all()
        print(f"\nCLICKABLE ({len(clickables)}):")
        for i, el in enumerate(clickables):
            try:
                text = el.inner_text(timeout=2000).strip()
                visible = el.is_visible()
                if visible and text and len(text) < 100:
                    tag = el.evaluate("e => e.tagName")
                    print(f"  [{i}] <{tag}> '{text}'")
            except:
                pass

        page.screenshot(path="/home/agentuser/muse/screenshot_ccvcc_check.png", full_page=True)
        print(f"\nScreenshot saved: screenshot_ccvcc_check.png")

        browser.close()
finally:
    client.sessions.stop(session.id)
