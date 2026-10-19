import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import time, requests, uuid, re, json
requests.packages.urllib3.disable_warnings()

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"
REF_CODE = "FO3DHT"

# Cek semua domain yang available
print("[*] Cek domains mail.tm...")
domains = requests.get("https://box.celana-ar-store.my.id/domains", verify=False, timeout=10).json()
domain_list = [d["domain"] for d in domains["hydra:member"]]
print(f"[+] Available domains: {domain_list}")

# Pilih domain pertama
DOMAIN = domain_list[0]
print(f"[+] Using domain: {DOMAIN}")

def make_email():
    username = f"bot_{uuid.uuid4().hex[:8]}"
    email = f"{username}@{DOMAIN}"
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

print(f"\n{'='*60}")
print("PENDEKATAN LAIN: Stealth Mode + Agresive Delay")
print(f"{'='*60}")

email, password, mail_token = make_email()
print(f"\n[1] FRESH EMAIL: {email}")

# Launch dengan stealth mode
client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create(params={"use_stealth": True, "solve_captchas": True})
print(f"[2] SESSION (stealth): {session.id}")

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = context.new_page()

        # Buka muse.ai
        page.goto("https://muse.ai/", timeout=60000)
        time.sleep(5)

        # Register flow dengan delay lebih agresif
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

        # Delay 30 detik (lebih agresif)
        print("[*] Tunggu 30 detik (anti rate-limit agresif)...")
        time.sleep(30)

        # Tunggu OTP dengan retry lebih banyak
        otp = None
        for i in range(40):
            otp = get_otp(mail_token)
            if otp:
                break
            if i % 5 == 4:
                print(f"  [{i+1}/40] Nunggu OTP...")
            time.sleep(6)

        if not otp:
            print("[-] OTP gak masuk setelah 4 menit!")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        print(f"[4] OTP: {otp}")

        # Delay lagi sebelum confirm
        print("[*] Tunggu 15 detik sebelum confirm...")
        time.sleep(15)

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

        if conf.get("status") != 200 and conf.get("status") != 201:
            print(f"[-] Confirm OTP gagal! Status: {conf.get('status')}")
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
            print(f"[-] Register gagal! Status: {reg.get('status')}")
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
            print("    Gak ada checkpoint URL - mungkin langsng sukses atau error lain")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(0)

        # Open checkpoint
        print(f"\n[8] CHECKPOINT URL: {checkpoint_url}")
        page.goto(checkpoint_url, timeout=60000)
        time.sleep(5)

        print(f"[9] URL: {page.url}")
        print(f"[10] TITLE: {page.title()}")

        # DETAILED CHECK
        print(f"\n{'='*60}")
        print("DETAILED CHECKPOINT ANALYSIS")
        print(f"{'='*60}")

        page_text = page.evaluate("() => document.body.innerText")
        print(f"\n[A] PAGE TEXT:\n{page_text[:2000]}")

        keywords = ["credit card", "debit card", "cc", "vcc", "payment", "billing", 
                     "card number", "cvv", "expiry", "age verification", "date of birth",
                     "birthday", "verify", "identity", "id", "upload", "camera",
                     "face", "scan", "document", "passport", "license", "ssn",
                     "social security", "credit", "debit"]
        
        print(f"\n[B] KEYWORD CHECK:")
        text_lower = page_text.lower()
        found_any = False
        for kw in keywords:
            if kw in text_lower:
                idx = text_lower.find(kw)
                context = page_text[max(0, idx-30):idx+len(kw)+30]
                print(f"  ✓ '{kw}' found: ...{context}...")
                found_any = True
        if not found_any:
            print("  (gak ada keyword CC/VCC found)")

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

        clickables = page.locator("button, a, [role=button], input[type=submit]").all()
        print(f"\n[D] CLICKABLE ({len(clickables)}):")
        for i, el in enumerate(clickables):
            try:
                text = el.inner_text(timeout=2000).strip()
                tag = el.evaluate("e => e.tagName")
                visible = el.is_visible()
                if visible and text and len(text) < 100:
                    print(f"  [{i}] <{tag}> '{text}'")
            except:
                pass

        page.screenshot(path="/home/agentuser/muse/screenshot_stealth_checkpoint.png", full_page=True)
        print(f"\n[E] Screenshot saved")

        browser.close()
finally:
    client.sessions.stop(session.id)
