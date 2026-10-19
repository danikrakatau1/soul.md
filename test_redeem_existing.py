import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import time, requests, json
requests.packages.urllib3.disable_warnings()

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"
REF_CODE = "FO3DHT"

# Email yang sudah registered dari run sebelumnya
REGISTERED_EMAILS = [
    "bot_f4015c7a@maxxspace.com",
    "bot_9bbd6a2b@maxxspace.com",
    "bot_8e8f5988@maxxspace.com",
    "bot_13eedce8@maxxspace.com",
]
PASSWORD = "SecurePass123!"

def get_token(email):
    res = requests.post("https://box.celana-ar-store.my.id/token", json={"address": email, "password": PASSWORD}, verify=False, timeout=10)
    if res.status_code == 200:
        return res.json().get("token")
    return None

def try_redeem_with_email(email, client):
    """Coba login dan redeem dengan email yang sudah registered"""
    print(f"\n{'='*60}")
    print(f"TRY: {email}")
    print(f"{'='*60}")
    
    session = client.sessions.create()
    print(f"Session: {session.id}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.new_context()
            page = context.new_page()
            
            page.goto("https://muse.ai/", timeout=60000)
            time.sleep(3)
            
            # Coba login: send OTP + confirm
            print("[*] Kirim OTP...")
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
            print(f"Send OTP: {res_data}")
            
            if res_data.get("status") not in [200, 201]:
                print("[-] Send OTP gagal!")
                browser.close()
                return None
            
            time.sleep(8)
            
            # Get OTP
            mail_token = get_token(email)
            if not mail_token:
                print("[-] Gak bisa login mail.tm!")
                browser.close()
                return None
            
            msgs = requests.get("https://box.celana-ar-store.my.id/messages", headers={"Authorization": f"Bearer {mail_token}"}, verify=False, timeout=10).json().get("hydra:member", [])
            if not msgs:
                print("[-] Gak ada email masuk!")
                browser.close()
                return None
            
            msg = requests.get(f"https://box.celana-ar-store.my.id/messages/{msgs[0]['id']}", headers={"Authorization": f"Bearer {mail_token}"}, verify=False, timeout=10).json()
            body = msg.get("text") or msg.get("intro") or ""
            import re
            m = re.search(r"\b\d{6}\b", body)
            if not m:
                print("[-] OTP gak ditemukan di email!")
                browser.close()
                return None
            
            otp = m.group(0)
            print(f"OTP: {otp}")
            
            time.sleep(3)
            
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
            print(f"Confirm OTP: {conf}")
            
            if conf.get("status") != 200 and conf.get("status") != 201:
                print("[-] Confirm OTP gagal!")
                browser.close()
                return None
            
            time.sleep(3)
            
            # Coba redeem
            print(f"\n[*] Coba redeem ({REF_CODE})...")
            redeem = page.evaluate("""async (code) => {
                let r = await fetch('/api/hatch/invite-code/redeem', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code, supportsRedemptionStatus: true})
                });
                return {status: r.status, json: await r.json()};
            }""", REF_CODE)
            print(f"Redeem: {json.dumps(redeem, indent=2)}")
            
            # Cek cookies
            cookies = context.cookies()
            csrf_cookie = None
            for c in cookies:
                if c.get("name") == "hatch_native_auth_csrf":
                    csrf_cookie = c.get("value")
                    break
            
            if csrf_cookie and redeem.get("status") == 403:
                print(f"\n[*] Coba redeem dengan CSRF dari cookies...")
                redeem2 = page.evaluate("""async (data) => {
                    let r = await fetch('/api/hatch/invite-code/redeem', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'x-hatch-csrf-token': data.csrf
                        },
                        body: JSON.stringify({code: data.code, supportsRedemptionStatus: true})
                    });
                    return {status: r.status, json: await r.json()};
                }""", {"csrf": csrf_cookie, "code": REF_CODE})
                print(f"Redeem (dengan CSRF): {json.dumps(redeem2, indent=2)}")
                redeem = redeem2
            
            checkpoint_url = redeem.get("json", {}).get("checkpoint_url")
            if checkpoint_url:
                print(f"\n[*] Buka checkpoint: {checkpoint_url}")
                page.goto(checkpoint_url, timeout=60000)
                time.sleep(5)
                print(f"URL: {page.url}")
                print(f"Title: {page.title()}")
                
                # Cek page text
                page_text = page.evaluate("() => document.body.innerText")
                print(f"Page text:\n{page_text[:1000]}")
                
                # Cek keywords CC/VCC
                keywords = ["credit card", "debit card", "cc", "vcc", "payment", "billing", "card number"]
                text_lower = page_text.lower()
                found = [kw for kw in keywords if kw in text_lower]
                if found:
                    print(f"[!] Keywords found: {found}")
                else:
                    print(f"[✓] Gak ada keywords CC/VCC")
                
                # Cek input fields
                inputs = page.locator("input, select, textarea").all()
                print(f"Input fields: {len(inputs)}")
                for inp in inputs:
                    try:
                        itype = inp.get_attribute("type")
                        name = inp.get_attribute("name")
                        if inp.is_visible():
                            print(f"  type={itype} name={name}")
                    except:
                        pass
                
                page.screenshot(path=f"/home/agentuser/muse/screenshot_redeem_{email[:10]}.png")
                print(f"Screenshot saved: screenshot_redeem_{email[:10]}.png")
            
            browser.close()
            return redeem
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        client.sessions.stop(session.id)

# Main
client = Hyperbrowser(api_key=API_KEY)

results = {}
for email in REGISTERED_EMAILS:
    result = try_redeem_with_email(email, client)
    results[email] = result
    time.sleep(5)  # Delay antar percobaan

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
for email, result in results.items():
    if result:
        status = result.get("status")
        print(f"{email}: status={status}")
        if status == 200:
            print(f"  ✅ SUKSES!")
        elif status == 403:
            print(f"  ❌ Forbidden (checkpoint)")
        elif status == 401:
            print(f"  ❌ Auth required")
    else:
        print(f"{email}: gak ada result")
