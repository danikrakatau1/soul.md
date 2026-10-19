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

        # Ambil cookies dan CSRF token
        cookies = context.cookies()
        print(f"\n[*] Cookies ({len(cookies)}):")
        csrf_cookie = None
        for c in cookies:
            print(f"  {c['name']}: {c['value'][:60]}...")
            if c['name'] == 'hatch_native_auth_csrf':
                csrf_cookie = c['value']

        # Coba redeem dengan CSRF dari cookies
        if csrf_cookie:
            print(f"\n[*] Redeem dengan CSRF dari cookies...")
            redeem = page.evaluate("""async (data) => {
                let r = await fetch('/api/hatch/invite-code/redeem', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': data.csrf
                    },
                    body: JSON.stringify({code: data.code, supportsRedemptionStatus: true})
                });
                return {status: r.status, headers: Object.fromEntries(r.headers.entries()), json: await r.json()};
            }""", {"csrf": csrf_cookie, "code": REF_CODE})
            print(f"[+] Redeem (dengan CSRF): {redeem}")
        else:
            print("[-] CSRF cookie gak ditemukan!")

        # Coba redeem tanpa CSRF
        print(f"\n[*] Redeem tanpa CSRF...")
        redeem2 = page.evaluate("""async (code) => {
            let r = await fetch('/api/hatch/invite-code/redeem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code, supportsRedemptionStatus: true})
            });
            return {status: r.status, json: await r.json()};
        }""", REF_CODE)
        print(f"[+] Redeem (tanpa CSRF): {redeem2}")

        # Coba GET redeem endpoint
        print(f"\n[*] Cek redeem endpoint (GET)...")
        check = page.evaluate("""async () => {
            let r = await fetch('/api/hatch/invite-code/redeem', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'}
            });
            return {status: r.status, json: await r.json().catch(() => 'not json')};
        }""")
        print(f"[+] GET redeem: {check}")

        # Cek API lain yang mungkin related
        print(f"\n[*] Cek API invite-code lain...")
        endpoints = [
            '/api/hatch/invite-code/validate',
            '/api/hatch/invite-code/status',
            '/api/hatch/invite-code/info',
        ]
        for ep in endpoints:
            try:
                res = page.evaluate("""async (ep) => {
                    let r = await fetch(ep, {method: 'GET'});
                    return {status: r.status, json: await r.json().catch(() => 'not json')};
                }""", ep)
                print(f"  {ep}: {res}")
            except Exception as e:
                print(f"  {ep}: error {e}")

        browser.close()
finally:
    client.sessions.stop(session.id)
