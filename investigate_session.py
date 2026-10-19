import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import time, requests, uuid, re
requests.packages.urllib3.disable_warnings()

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

# 1. Generate fresh email via mail.tm
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
        
        # Buka muse.ai
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
        
        # Tunggu OTP
        otp = None
        for i in range(20):
            otp = get_otp(mail_token)
            if otp:
                break
            time.sleep(5)
        
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
        
        # CEK COOKIES setelah confirm OTP
        cookies = context.cookies()
        print(f"\n[*] Cookies setelah confirm OTP: {len(cookies)}")
        for c in cookies:
            print(f"  {c['name']}: {c['value'][:60]}...")
        
        # CEK localStorage
        local_storage = page.evaluate("() => JSON.stringify(localStorage)")
        print(f"\n[*] localStorage: {local_storage[:500]}")
        
        # Navigate ke /access
        print("\n[*] Navigate ke /access...")
        page.goto("https://muse.ai/access", timeout=60000)
        time.sleep(5)
        print(f"[+] URL sekarang: {page.url}")
        
        # Cek tombol Get Started
        get_started = page.locator("text=Get Started").first
        if get_started.is_visible():
            print("[+] Tombol Get Started ditemukan! Klik...")
            get_started.click()
            time.sleep(5)
            print(f"[+] URL setelah Get Started: {page.url}")
            
            if "verification" in page.url.lower() or "verifikasi" in page.url.lower():
                print("[!] KENA VERIFIKASI!")
            else:
                print("[+] LOLOS!")
        else:
            print("[-] Get Started gak ditemukan")
            print(f"Page text: {page.inner_text()[:500]}")
        
        page.screenshot(path="/home/agentuser/muse/screenshot_investigate.png")
        print("\n[+] Screenshot saved: /home/agentuser/muse/screenshot_investigate.png")
        
        browser.close()
finally:
    client.sessions.stop(session.id)
