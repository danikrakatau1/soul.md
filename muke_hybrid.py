import json
import re
import sys
import time
import uuid
import requests as req
from curl_cffi import requests as cr

# ============ CONFIG ============
REF_CODE = "FO3DHT"
DOB = "1995-05-15"
FIRST_NAME = "Sari"
LAST_NAME = "Wijaya"
DASAR_MUSE = "https://muse.ai"
TEMP_MAIL_BASE = "https://box.celana-ar-store.my.id"
# ================================

def catet(step, msg):
    print(f"[{step}] {msg}", flush=True)

def gagal(step, msg):
    print(f"[{step}] GAGAL: {msg}", flush=True)
    sys.exit(1)

def buat_email():
    username = f"bot_{uuid.uuid4().hex[:8]}"
    email = f"{username}@celana-ar-store.my.id"
    return email

def get_otp(email):
    try:
        r = req.get(f"{TEMP_MAIL_BASE}/api/inbox?address={email}", verify=False, timeout=10)
        emails = r.json().get("emails", [])
        if emails:
            msg_id = emails[0]["id"]
            r2 = req.get(f"{TEMP_MAIL_BASE}/api/read?address={email}&id={msg_id}", verify=False, timeout=10)
            body = r2.json().get("body") or r2.json().get("text") or ""
            m = re.search(r"\b\d{6}\b", body)
            if m:
                return m.group(0)
    except Exception as e:
        print(f"  [debug] get_otp error: {e}")
    return None

# ============ PHASE 1: REGISTER VIA HYPERBROWSER ============

def register_via_hyperbrowser(email):
    catet("register", "Phase 1: Register via Hyperbrowser")

    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
    from hyperbrowser import Hyperbrowser
    from playwright.sync_api import sync_playwright

    API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

    client = Hyperbrowser(api_key=API_KEY)
    session = client.sessions.create()
    catet("hyperbrowser", f"Session: {session.id}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.new_context()
            page = context.new_page()

            page.goto(DASAR_MUSE + "/", timeout=60000)
            time.sleep(3)

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
            catet("send-otp", f"Status: {res_data.get('status')}")
            if res_data.get("status") not in [200, 201]:
                gagal("send-otp", f"Gagal: {res_data}")

            catet("delay", "Tunggu 30 detik...")
            time.sleep(30)

            catet("otp", "Tunggu OTP masuk...")
            otp = None
            for i in range(40):
                otp = get_otp(email)
                if otp:
                    break
                if i % 5 == 4:
                    catet("otp", f"  [{i+1}/40] Nunggu...")
                time.sleep(6)
            if not otp:
                gagal("otp", "OTP gak masuk")
            catet("otp", f"OTP: {otp}")

            catet("confirm", "Konfirmasi OTP...")
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
            catet("confirm", f"Status: {conf.get('status')}")

            if conf.get("status") != 200:
                gagal("confirm", f"Confirm gagal: {conf}")

            confirm_json = conf.get("json", {})
            auth_meta = confirm_json.get("auth_meta_session", {})
            access_token = auth_meta.get("frl_access_token")
            account_id = auth_meta.get("frl_account_id")

            if not access_token:
                gagal("confirm", f"Tidak ada access token: {list(confirm_json.keys())}")

            catet("confirm", f"Account ID: {account_id}")
            catet("confirm", f"Access token: {access_token[:20]}...")

            catet("register", "Register completion...")
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
            }""", {"csrf": res_data["csrf"], "dob": DOB, "depan": FIRST_NAME, "last_name": LAST_NAME})
            catet("register", f"Status: {reg.get('status')}")

            if reg.get("status") != 200:
                gagal("register", f"Register gagal: {reg}")

            reg_json = reg.get("json", {})
            catet("register", f"Redirect to: {reg_json.get('redirect_to')}")

            cookies = context.cookies()
            cookie_dict = {}
            for c in cookies:
                cookie_dict[c["name"]] = c["value"]
            catet("cookies", f"Extracted {len(cookie_dict)} cookies")

            browser.close()

            return {
                "access_token": access_token,
                "account_id": account_id,
                "cookies": cookie_dict,
                "email": email
            }
    finally:
        client.sessions.stop(session.id)

# ============ PHASE 2: REDEEM VIA CURL_CFFI ============

def redeem_via_curl_cffi(register_data):
    catet("redeem", "Phase 2: Redeem via curl_cffi")

    s = cr.Session(impersonate="chrome")
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": DASAR_MUSE,
        "Referer": DASAR_MUSE + "/",
        "x-hatch-caa-reg-entry-point": "login_home",
        "x-hatch-waterfall-id": str(uuid.uuid4()),
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    })

    for name, value in register_data["cookies"].items():
        s.cookies.set(name, value, domain=".muse.ai")
    catet("cookies", f"Set {len(register_data['cookies'])} cookies from Hyperbrowser")

    catet("redeem", f"Coba redeem {REF_CODE}...")
    r = s.post(
        DASAR_MUSE + "/api/hatch/invite-code/redeem",
        json={"code": REF_CODE, "supportsRedemptionStatus": True},
        timeout=30
    )
    catet("redeem", f"Status: {r.status_code}")
    catet("redeem", f"Response: {r.text[:300]}")

    if r.status_code == 200:
        return {"status": "success", "response": r.json()}
    elif r.status_code == 403:
        return {"status": "checkpoint", "response": r.json()}
    else:
        return {"status": "unknown", "response": r.json()}

# ============ MAIN ============

if __name__ == "__main__":
    print("=" * 60)
    print("MUKE HYBRID: Hyperbrowser Register + curl_cffi Redeem")
    print("=" * 60)

    email = buat_email()
    catet("email", f"Fresh email: {email}")

    register_data = register_via_hyperbrowser(email)

    time.sleep(3)
    redeem_result = redeem_via_curl_cffi(register_data)

    print("\n" + "=" * 60)
    catet("SELESAI", f"Email: {register_data['email']}")
    catet("SELESAI", f"Account ID: {register_data['account_id']}")
    catet("SELESAI", f"Redeem status: {redeem_result['status']}")
    if redeem_result['status'] == 'checkpoint':
        checkpoint_url = redeem_result.get('response', {}).get('checkpoint_url')
        if checkpoint_url:
            catet("SELESAI", f"Checkpoint URL: {checkpoint_url}")
    print("=" * 60)
