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
print("[*] TEST: Register + Redeem + Check Checkpoint")
print("=" * 60)

email, password, mail_token = make_email()
print(f"\n[1] FRESH EMAIL: {email}")

client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print(f"[2] SESSION: {session.id}")

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

        time.sleep(10)

        otp = None
        for i in range(30):
            otp = get_otp(mail_token)
            if otp:
                break
            time.sleep(6)

        if not otp:
            print("[-] OTP gak masuk!")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        print(f"[4] OTP: {otp}")

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

        time.sleep(3)

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

        time.sleep(3)

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
            print("    Gak ada checkpoint URL!")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        # Open checkpoint
        print(f"\n[8] CHECKPOINT URL: {checkpoint_url}")
        page.goto(checkpoint_url, timeout=60000)
        time.sleep(5)

        print(f"[9] URL: {page.url}")
        print(f"[10] TITLE: {page.title()}")

        # DETAILED CHECK
        print("\n" + "=" * 60)
        print("DETAILED CHECKPOINT ANALYSIS")
        print("=" * 60)

        # Full page text
        page_text = page.evaluate("() => document.body.innerText")
        print(f"\n[A] PAGE TEXT:\n{page_text[:2000]}")

        # Check for keywords
        keywords = ["credit card", "debit card", "cc", "vcc", "payment", "billing", 
                     "card number", "cvv", "expiry", "age verification", "date of birth",
                     "birthday", "verify", "identity", "id", "upload", "camera",
                     "face", "scan", "document", "passport", "license"]
        
        print(f"\n[B] KEYWORD CHECK:")
        text_lower = page_text.lower()
        for kw in keywords:
            if kw in text_lower:
                # Find context
                idx = text_lower.find(kw)
                context = page_text[max(0, idx-30):idx+len(kw)+30]
                print(f"  ✓ '{kw}' found: ...{context}...")

        # All input fields
        inputs = page.locator("input, select, textarea").all()
        print(f"\n[C] FORM INPUTS ({len(inputs)}):")
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

        # All clickable elements
        clickables = page.locator("button, a, [role=button], input[type=submit]").all()
        print(f"\n[D] CLICKABLE ELEMENTS ({len(clickables)}):")
        for i, el in enumerate(clickables):
            try:
                text = el.inner_text(timeout=2000).strip()
                tag = el.evaluate("e => e.tagName")
                visible = el.is_visible()
                if visible and text and len(text) < 100:
                    print(f"  [{i}] <{tag}> '{text}'")
            except:
                pass

        # Images (could be CAPTCHA icons)
        images = page.locator("img").all()
        print(f"\n[E] IMAGES ({len(images)}):")
        for i, img in enumerate(images):
            try:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                visible = img.is_visible()
                if visible:
                    print(f"  [{i}] alt='{alt}' src={src[:80]}")
            except:
                pass

        # Iframes (reCAPTCHA)
        iframes = page.locator("iframe").all()
        print(f"\n[F] IFRAMES ({len(iframes)}):")
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute("src")
                print(f"  [{i}] {src}")
            except:
                pass

        # Full page screenshot
        page.screenshot(path="/home/agentuser/muse/screenshot_checkpoint_full.png", full_page=True)
        print(f"\n[G] Screenshot saved: screenshot_checkpoint_full.png")

        # Try to login with existing account (Continue with Facebook)
        print(f"\n[H] TRY: Klik 'Continue with Facebook'...")
        fb_btn = page.locator("text=Continue with Facebook").first
        if fb_btn.is_visible():
            print("  Button ditemukan! Klik...")
            fb_btn.click()
            time.sleep(5)
            print(f"  URL setelah: {page.url}")
            print(f"  Title: {page.title()}")
            
            # Check what's on this new page
            new_text = page.evaluate("() => document.body.innerText")
            print(f"  Page text: {new_text[:1000]}")
            
            # Check for CC/VCC keywords again
            new_lower = new_text.lower()
            for kw in ["credit card", "debit card", "cc", "vcc", "payment", "billing", "card"]:
                if kw in new_lower:
                    print(f"  ✓ '{kw}' found!")
            
            page.screenshot(path="/home/agentuser/muse/screenshot_after_fb_login.png")
            print("  Screenshot saved: screenshot_after_fb_login.png")
            
            # Try redeem again
            print(f"\n[I] REDEEM LAGI setelah Facebook login...")
            redeem2 = page.evaluate("""async (code) => {
                let r = await fetch('/api/hatch/invite-code/redeem', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code, supportsRedemptionStatus: true})
                });
                return {status: r.status, json: await r.json()};
            }""", REF_CODE)
            print(f"    Result: {json.dumps(redeem2, indent=2)}")
        else:
            print("  Button 'Continue with Facebook' gak ditemukan")

        browser.close()
finally:
    client.sessions.stop(session.id)
