"""
Muse.ai Auto Signup Bot via Hyperbrowser + Mail.tm
===================================================
- Cloud browser US (bypass region lock, skip CC verif)
- Auto generate temp email via mail.tm
- Auto baca OTP dari inbox
- Auto redeem invite code untuk 1B token

Usage:
  export HYPERBROWSER_API_KEY='hb_xxx'
  python muse_auto_signup.py
  python muse_auto_signup.py --count 3   # buat 3 akun
"""

import os, sys, time, random, string, re, json, argparse
import requests
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright

# ============================================================
# CONFIG
# ============================================================
API_KEY     = os.environ.get("HYPERBROWSER_API_KEY", "hb_cdfc571755daac8231b0c1812ec4")
INVITE_CODE = "FTITRD"   # ganti ke kode kamu sendiri
RESULT_FILE = "/home/agentuser/muse/muse_accounts.json"
MAILTM_API  = "https://box.celana-ar-store.my.id"

# ============================================================
# MAIL.TM HELPERS
# ============================================================

def mailtm_get_domain():
    r = requests.get(f"{MAILTM_API}/domains", timeout=10)
    return r.json()["hydra:member"][0]["domain"]

def mailtm_create_account():
    domain = mailtm_get_domain()
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email    = f"{username}@{domain}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    r = requests.post(f"{MAILTM_API}/accounts",
                      json={"address": email, "password": password}, timeout=10)
    if r.status_code in (200, 201):
        print(f"[+] Email dibuat: {email}")
        return email, password
    raise Exception(f"Gagal buat email: {r.text}")

def mailtm_get_token(email, password):
    r = requests.post(f"{MAILTM_API}/token",
                      json={"address": email, "password": password}, timeout=10)
    return r.json()["token"]

def mailtm_wait_otp(email, password, timeout=120):
    print(f"[*] Tunggu OTP di {email} ...")
    token = mailtm_get_token(email, password)
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{MAILTM_API}/messages", headers=headers, timeout=10)
        msgs = r.json().get("hydra:member", [])
        if msgs:
            msg_id = msgs[0]["id"]
            detail = requests.get(f"{MAILTM_API}/messages/{msg_id}", headers=headers, timeout=10).json()
            text_part = detail.get("text", "")
            html_part = detail.get("html", "")
            # html bisa berupa list atau string
            if isinstance(html_part, list):
                html_part = " ".join(html_part)
            if isinstance(text_part, list):
                text_part = " ".join(text_part)
            combined = text_part + " " + html_part
            # Cari 6-digit OTP
            codes = re.findall(r'\b(\d{6})\b', combined)
            if codes:
                print(f"[+] OTP ditemukan: {codes[0]}")
                return codes[0]
        time.sleep(5)
    raise Exception("Timeout tunggu OTP")

# ============================================================
# MAIN SIGNUP FLOW
# ============================================================

def signup_one_account(account_num=1):
    print(f"\n{'='*50}")
    print(f"[*] Signup akun #{account_num}")
    print(f"{'='*50}")

    # 1. Buat email temp
    email, mail_pass = mailtm_create_account()

    client = Hyperbrowser(api_key=API_KEY)
    print("[*] Buat cloud browser session...")
    session = client.sessions.create({
        "use_stealth": True,
        "screen": {"width": 1366, "height": 768},
    })
    print(f"[*] Session ID: {session.id}")

    result = {"email": email, "mail_pass": mail_pass, "status": "failed", "invite_redeemed": False}

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.contexts[0]
            page    = context.pages[0]

            # --- Step 1: Buka muse.ai ---
            print("[*] Buka muse.ai/join ...")
            page.goto("https://muse.ai/join", timeout=30000)
            time.sleep(3)

            # --- Step 2: Isi email ---
            print(f"[*] Isi email: {email}")
            inp = page.locator("input").first
            inp.fill(email)
            time.sleep(1)
            page.locator("button:has-text('Continue')").click()
            time.sleep(3)

            # --- Step 3: Baca & isi OTP ---
            body = page.inner_text("body")
            if "Enter your code" in body or "code we sent" in body:
                otp = mailtm_wait_otp(email, mail_pass)
                print(f"[*] Masukkan OTP: {otp}")
                otp_input = page.locator("input[inputmode='numeric'], input[type='tel'], input[autocomplete='one-time-code']").first
                otp_input.fill(otp)
                time.sleep(1)
                page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Submit')").first.click()
                time.sleep(4)
            else:
                print("[!] Tidak ada OTP step, state:", body[:200])

            # --- Step 4: Cek age verif ---
            body2 = page.inner_text("body")
            print("[*] State setelah OTP:", body2[:300])

            if "age" in body2.lower() or "born" in body2.lower() or "birthday" in body2.lower():
                print("[*] Ada age verif - coba link FB/IG atau skip...")
                # Coba klik opsi Instagram/Facebook kalau ada
                try:
                    page.locator("button:has-text('Instagram'), a:has-text('Instagram')").first.click(timeout=3000)
                    time.sleep(3)
                    print("[*] Klik Instagram verif")
                except:
                    pass
                try:
                    page.locator("button:has-text('Facebook'), a:has-text('Facebook')").first.click(timeout=3000)
                    time.sleep(3)
                    print("[*] Klik Facebook verif")
                except:
                    print("[!] Tidak ada opsi FB/IG, skip age verif")

            # --- Step 5: Cek apakah sudah masuk ---
            time.sleep(3)
            body3  = page.inner_text("body")
            url3   = page.url
            print(f"[*] Final URL: {url3}")
            print(f"[*] Final state: {body3[:300]}")

            if "muse.ai" in url3 and ("chat" in url3 or "home" in url3 or "dashboard" in url3
                                       or "What can I" in body3 or "Muse" in body3[:50]):
                print("[+] BERHASIL MASUK!")
                result["status"] = "success"

                # --- Step 6: Redeem invite code ---
                print(f"[*] Redeem invite code: {INVITE_CODE}")
                try:
                    # Buka settings
                    page.goto("https://muse.ai/settings", timeout=15000)
                    time.sleep(2)
                    # Cari redeem field
                    page.locator("input[placeholder*='code' i], input[placeholder*='invite' i]").first.fill(INVITE_CODE)
                    time.sleep(1)
                    page.locator("button:has-text('Redeem'), button:has-text('Submit'), button:has-text('Apply')").first.click()
                    time.sleep(2)
                    print("[+] Invite code diredeem!")
                    result["invite_redeemed"] = True
                    result["invite_code"] = INVITE_CODE
                except Exception as e:
                    print(f"[!] Gagal redeem invite: {e}")
            else:
                print("[!] Belum berhasil masuk / masih di halaman verif")
                result["status"] = "need_verification"
                result["last_url"] = url3

            page.screenshot(path=f"/home/agentuser/muse/muse_account_{account_num}.png")
            browser.close()

    except Exception as e:
        print(f"[!] Error: {e}")
        result["error"] = str(e)
    finally:
        client.sessions.stop(session.id)
        print("[*] Session ditutup.")

    # Simpan hasil
    try:
        existing = json.load(open(RESULT_FILE)) if os.path.exists(RESULT_FILE) else []
    except:
        existing = []
    existing.append(result)
    json.dump(existing, open(RESULT_FILE, "w"), indent=2)
    print(f"[*] Disimpan ke {RESULT_FILE}")
    return result


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Jumlah akun yang dibuat")
    args = parser.parse_args()

    print(f"[*] Muse.ai Auto Signup Bot")
    print(f"[*] Target: {args.count} akun")
    print(f"[*] Invite code: {INVITE_CODE}")

    results = []
    for i in range(1, args.count + 1):
        r = signup_one_account(i)
        results.append(r)
        if i < args.count:
            delay = random.randint(5, 10)
            print(f"[*] Tunggu {delay}s sebelum akun berikutnya...")
            time.sleep(delay)

    print("\n" + "="*50)
    print("SUMMARY:")
    for i, r in enumerate(results, 1):
        print(f"  Akun #{i}: {r['email']} -> {r['status']} | invite: {r.get('invite_redeemed', False)}")
    print("="*50)
