import json
import os
import random
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
# ================================

DASAR_MUSE = "https://muse.ai"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"

NGARAN_DEPAN = ["Miauru", "Anya", "Sinta", "Putri", "Dian", "Nadia", "Fitri", "Intan", "Rani", "Wulan"]
NGARAN_TUKANG = ["Juanda", "Pratama", "Nugroho", "Saputra", "Kusuma", "Wijaya", "Santoso", "Hidayat"]

def catet(lengkah, pesen):
    print(f"[{lengkah}] {pesen}", flush=True)

def gagal(lengkah, pesen):
    print(f"[{lengkah}] GAGAL: {pesen}", flush=True)
    sys.exit(1)

TEMP_MAIL_BASE = "https://box.celana-ar-store.my.id"

def buat_email():
    domain = "celana-ar-store.my.id"
    username = f"bot_{uuid.uuid4().hex[:8]}"
    email = f"{username}@{domain}"
    return email

def get_otp(email):
    try:
        r = req.get(f"{TEMP_MAIL_BASE}/api/inbox?address={email}", verify=False, timeout=10)
        data = r.json()
        emails = data.get("emails", [])
        if emails:
            msg_id = emails[0]["id"]
            r2 = req.get(f"{TEMP_MAIL_BASE}/api/read?address={email}&id={msg_id}", verify=False, timeout=10)
            msg = r2.json()
            body = msg.get("body") or msg.get("text") or ""
            m = re.search(r"\b\d{6}\b", body)
            if m:
                return m.group(0)
    except Exception as e:
        print(f"  [debug] get_otp error: {e}")
    return None

def lacak_sentry():
    return f"{uuid.uuid4().hex}{uuid.uuid4().hex[:16]}-{uuid.uuid4().hex[:16]}-0"

def sesi_api():
    s = cr.Session(impersonate="chrome")
    s.headers.update({
        "User-Agent": UA,
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
    return s

def post_api(sesi, path, beban, csrf=None, cobaan=3):
    headers = {"sentry-trace": lacak_sentry(), "Content-Type": "application/json"}
    if csrf:
        headers["x-hatch-csrf-token"] = csrf
    for a in range(cobaan):
        try:
            r = sesi.post(DASAR_MUSE + path, json=beban, headers=headers, timeout=30)
            if r.status_code in (200, 201):
                return r
            err = f"HTTP {r.status_code}: {r.text[:160]}"
            print(f"  [debug] attempt {a+1}: {err}", flush=True)
            if r.status_code == 429:
                gagal("rate-limit", f"Meta rate limited ({r.text[:80]}). Tunggu 15-30 menit.")
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            print(f"  [debug] attempt {a+1}: {err}", flush=True)
        time.sleep(2 * (a + 1))
    return None

def alur_register():
    catet("mulai", "Alur register via curl_cffi (tanpa browser)")
    
    email = buat_email()
    catet("email", f"Fresh email: {email}")
    
    s = sesi_api()
    
    # Step 1: Restart
    catet("restart", "Kirim restart...")
    r = post_api(s, "/api/auth/native/restart", {})
    if not r:
        gagal("restart", "Gagal kirim restart")
    d = r.json()
    csrf = d.get("csrf_token")
    catet("csrf", f"CSRF: {csrf[:20]}...")
    
    # Step 2: Send OTP
    catet("send-otp", f"Kirim OTP ke {email}...")
    r = post_api(s, "/api/auth/native/send-otp", {"contact_point": email, "region": "US"}, csrf)
    if not r:
        gagal("send-otp", "Gagal kirim OTP")
    catet("send-otp", f"Status: {r.status_code}")
    
    # Delay 30 detik sebelum confirm-otp (anti rate-limit)
    catet("delay", "Tunggu 30 detik sebelum confirm-otp...")
    time.sleep(30)

    # Step 3: Tunggu OTP
    catet("otp", "Tunggu OTP masuk...")
    otp = None
    for i in range(30):
        otp = get_otp(email)
        if otp:
            break
        if i % 5 == 4:
            catet("otp", f"  [{i+1}/30] Nunggu...")
        time.sleep(6)
    if not otp:
        gagal("otp", "OTP gak masuk")
    catet("otp", f"OTP: {otp}")
    
    # Step 4: Confirm OTP
    catet("confirm", "Konfirmasi OTP...")
    r = post_api(s, "/api/auth/native/confirm-otp", {"otp_code": otp}, csrf)
    if not r:
        gagal("confirm", "Gagal confirm OTP")
    d = r.json()
    catet("confirm", f"Status: {r.status_code}")
    safe_confirm = {k: (v if k not in {'frl_access_token', 'access_token'} else f"{str(v)[:12]}...") for k, v in d.items()}
    catet("confirm", f"Response keys: {list(d.keys())}")
    catet("confirm", f"auth_meta_session keys: {list(d.get('auth_meta_session', {}).keys())}")

    if r.status_code != 200:
        gagal("confirm", f"Confirm gagal: {d}")

    # Set cookies dari confirm-otp response
    access_token_confirm = d.get("auth_meta_session", {}).get("frl_access_token")
    if access_token_confirm:
        s.cookies.set("frl_access_token", access_token_confirm, domain=".muse.ai")
        s.cookies.set("hatch_native_auth_state", "completion_required", domain=".muse.ai")
        catet("cookies", f"Set frl_access_token dari confirm-otp")

    # Step 5: Register Completion
    catet("register", "Register completion...")
    r = post_api(s, "/api/auth/native/register-completion", {
        "date_of_birth": DOB,
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "tos_content_version": "ntm_create_account:default_v1_meta_account_v2+docs_v1"
    }, csrf)
    if not r:
        gagal("register", "Gagal register")
    d = r.json()
    catet("register", f"Status: {r.status_code}")
    catet("register", f"Body: {r.text[:300]}")
    
    if r.status_code != 200:
        gagal("register", f"Register gagal: {d}")
    
    access_token = d.get("auth_meta_session", {}).get("frl_access_token")
    account_id = d.get("auth_meta_session", {}).get("frl_account_id")
    catet("sukses", f"Akun ID: {account_id}")
    catet("sukses", f"Access token: {access_token[:30]}...")
    
    # Save cookies
    cookies = s.cookies.get_dict()
    catet("cookies", f"Cookies: {list(cookies.keys())}")
    
    return s, email, access_token, account_id, cookies, email

def cek_status_vcc(s):
    """Cek apakah akun kena VCC atau tidak"""
    catet("vcc-cek", "Cek status VCC...")
    r = s.get(DASAR_MUSE + "/api/hatch/invite", timeout=30)
    if r.status_code == 200:
        d = r.json()
        state = d.get("invite_state")
        catet("vcc-cek", f"invite_state: {state}")
        return state
    elif r.status_code == 403:
        catet("vcc-cek", "403 - checkpoint required")
        return "checkpoint"
    else:
        catet("vcc-cek", f"HTTP {r.status_code}")
        return "unknown"

def coba_redeem(s):
    """Coba redeem referral"""
    catet("redeem", f"Coba redeem {REF_CODE}...")
    r = s.post(DASAR_MUSE + "/api/hatch/invite-code/redeem", json={"code": REF_CODE, "supportsRedemptionStatus": True}, timeout=30)
    catet("redeem", f"Status: {r.status_code}")
    if r.status_code == 200:
        catet("redeem", f"SUKSES: {r.json()}")
        return True
    else:
        catet("redeem", f"Gagal: {r.text[:200]}")
        return False

def simpan_akun(email, account_id, access_token, cookies):
    """Simpan ke file"""
    with open("/home/agentuser/muse/Jestco.txt", "a") as f:
        f.write(f"{email}:SecurePass123! # {FIRST_NAME} {LAST_NAME} | ID: {account_id} | Reff: {REF_CODE}\n")
    catet("simpan", "Akun disimpan ke Jestco.txt")

if __name__ == "__main__":
    print("=" * 60)
    print("MUKE REGISTER VIA CURL_CFFI (TANPA BROWSER)")
    print("=" * 60)
    
    # Register
    s, email, access_token, account_id, cookies, _ = alur_register()
    
    # Cek VCC status
    time.sleep(3)
    vcc_status = cek_status_vcc(s)
    
    # Coba redeem
    time.sleep(3)
    redeem_ok = coba_redeem(s)
    
    # Simpan
    if redeem_ok:
        simpan_akun(email, account_id, access_token, cookies)
    
    print("\n" + "=" * 60)
    catet("SELESAI", f"Email: {email}")
    catet("SELESAI", f"Akun ID: {account_id}")
    catet("SELESAI", f"VCC Status: {vcc_status}")
    catet("SELESAI", f"Redeem: {'SUKSES' if redeem_ok else 'GAGAL'}")
    print("=" * 60)
