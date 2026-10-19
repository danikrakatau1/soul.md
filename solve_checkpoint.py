import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import time, requests, uuid, re
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

print("[*] Buat fresh email...")
email, password, mail_token = make_email()
print(f"[+] Email: {email}")

client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print(f"[+] Session: {session.id}")

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://muse.ai/", timeout=60000)
        time.sleep(3)

        # Restart + Send OTP
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
        print(f"[+] Send OTP: {res_data}")

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

        print(f"[+] OTP: {otp}")

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
        print(f"[+] Confirm OTP: {conf}")

        time.sleep(3)

        # Register Completion
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
        print(f"[+] Register: {reg}")

        time.sleep(3)

        # Coba redeem -> tangkap checkpoint URL
        print("\n[*] Coba redeem untuk trigger checkpoint...")
        redeem = page.evaluate("""async (code) => {
            let r = await fetch('/api/hatch/invite-code/redeem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code, supportsRedemptionStatus: true})
            });
            return {status: r.status, json: await r.json()};
        }""", REF_CODE)
        print(f"[+] Redeem: {redeem}")

        # Extract checkpoint URL
        checkpoint_url = redeem.get("json", {}).get("checkpoint_url")
        if not checkpoint_url:
            print("[-] Gak ada checkpoint_url di response")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        print(f"\n[*] Buka checkpoint URL: {checkpoint_url}")
        page.goto(checkpoint_url, timeout=60000)
        time.sleep(5)

        print(f"[+] URL sekarang: {page.url}")
        print(f"[+] Title: {page.title()}")

        # Cek halaman checkpoint
        print(f"\n[*] Cek halaman checkpoint:")
        
        # Cari semua elements
        all_text = page.evaluate("() => document.body.innerText")
        print(f"Page text:\n{all_text[:1500]}")
        
        # Cari buttons
        buttons = page.locator("button").all()
        print(f"\n[*] Buttons ({len(buttons)}):")
        for i, btn in enumerate(buttons):
            try:
                text = btn.inner_text(timeout=2000).strip()
                visible = btn.is_visible()
                if visible and text:
                    print(f"  [{i}] Button: '{text}'")
            except:
                pass

        # Cari links
        links = page.locator("a").all()
        print(f"\n[*] Links ({len(links)}):")
        for i, link in enumerate(links):
            try:
                text = link.inner_text(timeout=2000).strip()
                href = link.get_attribute("href")
                visible = link.is_visible()
                if visible and text:
                    print(f"  [{i}] Link: '{text}' -> {href}")
            except:
                pass

        # Cari images (CAPTCHA)
        images = page.locator("img").all()
        print(f"\n[*] Images ({len(images)}):")
        for i, img in enumerate(images):
            try:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                visible = img.is_visible()
                if visible:
                    print(f"  [{i}] Img: src={src[:80]}... alt={alt}")
            except:
                pass

        # Cari iframes (reCAPTCHA)
        iframes = page.locator("iframe").all()
        print(f"\n[*] Iframes ({len(iframes)}):")
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute("src")
                print(f"  [{i}] Iframe: {src}")
            except:
                pass

        # Cek apakah ada form input
        inputs = page.locator("input").all()
        print(f"\n[*] Inputs ({len(inputs)}):")
        for i, inp in enumerate(inputs):
            try:
                itype = inp.get_attribute("type")
                name = inp.get_attribute("name")
                visible = inp.is_visible()
                if visible:
                    print(f"  [{i}] Input: type={itype} name={name}")
            except:
                pass

        page.screenshot(path="/home/agentuser/muse/screenshot_checkpoint.png", full_page=True)
        print("\n[+] Screenshot checkpoint saved: /home/agentuser/muse/screenshot_checkpoint.png")

        # Coba klik "Continue" atau "Next" jika ada
        continue_btn = page.locator("button:has-text('Continue'), button:has-text('Next'), button:has-text('Submit'), button:has-text('Verify')").first
        if continue_btn.is_visible():
            print(f"\n[+] Tombol '{continue_btn.inner_text()}' ditemukan! Klik...")
            continue_btn.click()
            time.sleep(5)
            print(f"[+] URL setelah klik: {page.url}")
            page.screenshot(path="/home/agentuser/muse/screenshot_after_checkpoint.png")
            print("[+] Screenshot after checkpoint saved")

            # Coba redeem lagi
            print("\n[*] Coba redeem lagi setelah checkpoint...")
            redeem2 = page.evaluate("""async (code) => {
                let r = await fetch('/api/hatch/invite-code/redeem', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code, supportsRedemptionStatus: true})
                });
                return {status: r.status, json: await r.json()};
            }""", REF_CODE)
            print(f"[+] Redeem attempt 2: {redeem2}")
        else:
            print("\n[-] Tombol Continue/Next gak ditemukan")

        browser.close()
finally:
    client.sessions.stop(session.id)
