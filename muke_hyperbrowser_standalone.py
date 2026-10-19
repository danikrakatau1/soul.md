import sys
import time
import random
import os
import re
import requests
import uuid
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
def run_full_automation(ref_code="FO3DHT"):
    print("[*] 1. Membuat sesi Hyperbrowser di cloud US...")
    client = Hyperbrowser(api_key=API_KEY)
    session = client.sessions.create()
    print(f"[+] Sesi aktif! ID: {session.id}")

    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal generate email!")
        client.sessions.stop(session.id)
        return False

    depan = random.choice(NGARAN_DEPAN)
    tukang = random.choice(NGARAN_TUKANG)
    print(f"[+] Profil Akun: {depan} {tukang} | Reff: {ref_code}")

    try:
        with sync_playwright() as p:
            print("[*] 3. Menghubungkan Playwright ke remote browser Hyperbrowser...")
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.new_context()
            page = context.new_page()

            print("[*] 4. Membuka muse.ai...")
            page.goto("https://muse.ai/", timeout=60000)
            time.sleep(3)

            # API Restart & Send OTP
            print("[*] 5. Mengirim request restart & send-otp via API...")
            res_data = page.evaluate(f"""async () => {{
                let r1 = await fetch('/api/auth/native/restart', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{}})
                }});
                let d1 = await r1.json();
                let csrf = d1.csrf_token;
                
                let r2 = await fetch('/api/auth/native/send-otp', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': csrf
                    }},
                    body: JSON.stringify({{"contact_point": "{email}", "region": "US"}})
                }});
                return {{status: r2.status, csrf: csrf}};
            }}""")
            print("[+] Send-OTP API Result:", res_data)

            # Wait for OTP
            otp = mail.wait_for_otp(timeout=120, interval=5)
            if not otp:
                print("[-] OTP tidak ditemukan!")
                browser.close()
                client.sessions.stop(session.id)
                return False

            # Confirm OTP via API
            print(f"[*] 6. Konfirmasi OTP ({otp}) via API...")
            conf_res = page.evaluate(f"""async () => {{
                let r = await fetch('/api/auth/native/confirm-otp', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': '{res_data["csrf"]}'
                    }},
                    body: JSON.stringify({{"otp_code": "{otp}"}})
                }});
                return await r.json();
            }}""")
            print("[+] Confirm OTP API Resp:", conf_res)

            # Register Completion via API
            dob = "1995-05-15"
            print(f"[*] 7. Register Completion ({depan} {tukang}) via API...")
            reg_res = page.evaluate(f"""async () => {{
                let r = await fetch('/api/auth/native/register-completion', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': '{res_data["csrf"]}'
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
            print("[+] Register Completion API Resp:", reg_res)

            # Redeem Referral via API
            if ref_code and "auth_meta_session" in reg_res:
                print(f"[*] 8. Redeem referral ({ref_code})...")
                redeem_res = page.evaluate(f"""async () => {{
                    let r = await fetch('/api/hatch/invite-code/redeem', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{"code": "{ref_code}", "supportsRedemptionStatus": true}})
                    }});
                    return await r.json();
                }}""")
                print("[+] Redeem API Resp:", redeem_res)

            time.sleep(3)
            page.screenshot(path="/home/agentuser/muse/screenshot_final.png")
            print("[+] Screenshot saved.")

            browser.close()
            
            with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:SecurePass123! # {depan} {tukang} | Reff: {ref_code}\n")
            print("[+] Akun sukses & referral tertanam dicatat ke Jestco.txt!")
            return True

    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        print("[*] Menghentikan sesi Hyperbrowser...")
        client.sessions.stop(session.id)

if __name__ == "__main__":
    run_full_automation("FO3DHT")
