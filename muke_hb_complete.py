import sys
import time
import random
import os
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Dual Engine Temp Mail ---
class TempMail:
    def __init__(self):
        self.base_url = "https://box.celana-ar-store.my.id"
        self.email = None
        self.domain = "celana-ar-store.my.id"

    def generate_email(self):
        import random, string
        local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.email = f"{local}@{self.domain}"
        print(f"[email] Temp Email Custom Dibuat: {self.email}")
        return self.email

    def wait_for_otp(self, timeout=150, interval=5):
        print(f"[otp] Menunggu email masuk ke {self.email} (Maks {timeout} detik)...")
        start_time = time.time()
        seen_ids = set()
        while time.time() - start_time < timeout:
            try:
                res = preq.get(f"{self.base_url}/api/inbox", params={"address": self.email}, timeout=10)
                if res.status_code == 200:
                    emails = res.json().get("emails", [])
                    for mail in emails:
                        msg_id = mail.get("id")
                        if msg_id not in seen_ids:
                            seen_ids.add(msg_id)
                            m_res = preq.get(f"{self.base_url}/api/read", params={"address": self.email, "id": msg_id}, timeout=10)
                            if m_res.status_code == 200:
                                data = m_res.json()
                                body = data.get("body", "")
                                subject = data.get("subject", "")
                                combined = f"{subject} {body}"
                                otp_match = re.search(r'\b(\d{6})\b', combined)
                                if otp_match:
                                    otp = otp_match.group(1)
                                    print(f"[otp] Kode OTP Diterima: {otp}")
                                    return otp
            except Exception as e:
                pass
            time.sleep(interval)
        return None
def run_hb_complete(ref_code="FO3DHT"):
    print("="*50)
    print("🤖 Muke Hyperbrowser Complete Automation")
    print("="*50)

    print("[HB] Membuat sesi Hyperbrowser cloud US...")
    client = Hyperbrowser(api_key=API_KEY)
    session = client.sessions.create()
    print(f"[HB] Sesi aktif! ID: {session.id}")

    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal generate email")
        client.sessions.stop(session.id)
        return False

    depan = random.choice(NGARAN_DEPAN)
    tukang = random.choice(NGARAN_TUKANG)
    dob = f"{random.randint(1985, 2002):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    print(f"[profile] {depan} {tukang} | DOB: {dob}")

    try:
        with sync_playwright() as p:
            print("[*] Menghubungkan Playwright ke browser cloud US...")
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            page = browser.new_context().new_page()

            print("[*] Membuka muse.ai...")
            page.goto("https://muse.ai/", timeout=60000)
            time.sleep(3)

            print(f"[*] Mengirim restart flow via browser JS context...")
            restart_resp = page.evaluate("""async () => {
                let r = await fetch('/api/auth/native/restart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                return await r.json();
            }""")
            csrf = restart_resp.get("csrf_token")
            if not csrf:
                print("[-] Gagal dapat CSRF token:", restart_resp)
                browser.close()
                client.sessions.stop(session.id)
                return False
            print(f"[+] CSRF Token didapat: {csrf[:10]}...")

            # Send OTP via browser JS context
            print(f"[*] Mengirim OTP ke {email}...")
            otp_resp = page.evaluate(f"""async () => {{
                let r = await fetch('/api/auth/native/send-otp', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': '{csrf}'
                    }},
                    body: JSON.stringify({{"contact_point": "{email}", "region": "US"}})
                }});
                return r.status;
            }}""")
            print(f"[+] Status Kirim OTP: {otp_resp}")

            # Wait for OTP
            otp = mail.wait_for_otp(timeout=120, interval=5)
            if not otp:
                print("[-] OTP tidak datang")
                browser.close()
                client.sessions.stop(session.id)
                return False

            # Confirm OTP
            print("[*] Mengonfirmasi OTP...")
            conf_resp = page.evaluate(f"""async () => {{
                let r = await fetch('/api/auth/native/confirm-otp', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': '{csrf}'
                    }},
                    body: JSON.stringify({{"otp_code": "{otp}"}})
                }});
                return await r.json();
            }}""")
            print(f"[+] Confirm OTP Resp:", conf_resp)

            # Register Completion
            print("[*] Menyelesaikan pendaftaran (Register Completion)...")
            reg_resp = page.evaluate(f"""async () => {{
                let r = await fetch('/api/auth/native/register-completion', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': '{csrf}'
                    }},
                    body: JSON.stringify({{
                        "date_of_birth": "{dob}",
                        "first_name": "{depan}",
                        "last_name": "{tukang}",
                        "tos_content_version": "ntm_create_account:default_v1_meta_account_v2+docs_v1"
                    }})
                }});
                return await r.json();
            }}""")
            print(f"[+] Register Completion Resp:", reg_resp)

            # Redeem Reff if success
            if ref_code and "auth_meta_session" in reg_resp:
                print(f"[*] Menebus kode referral: {ref_code}...")
                redeem_resp = page.evaluate(f"""async () => {{
                    let r = await fetch('/api/hatch/invite-code/redeem', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{"code": "{ref_code}", "supportsRedemptionStatus": true}})
                    }});
                    return await r.json();
                }}""")
                print(f"[+] Redeem Resp:", redeem_resp)

            with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:SecurePass123! # HB Complete ({depan} {tukang})\n")
            print("[SUCCESS] Akun berhasil dibuat dan disimpan ke Jestco.txt!")

            browser.close()
            return True

    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        print("[HB] Menghentikan sesi Hyperbrowser...")
        client.sessions.stop(session.id)

if __name__ == "__main__":
    run_hb_complete("FO3DHT")
