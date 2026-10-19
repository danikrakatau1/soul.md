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
def run_production_bot(ref_code="FO3DHT", total_accounts=1):
    print("="*60)
    print("🤖 BOT MUSER PRODUCTION V5 (ROBUST PLAYWRIGHT)")
    print("="*60)

    for i in range(1, total_accounts + 1):
        print(f"\n--- [AKUN {i}/{total_accounts}] ---")
        client = Hyperbrowser(api_key=API_KEY)
        session = client.sessions.create()
        print(f"[+] Sesi Hyperbrowser US Aktif! ID: {session.id}")

        mail = TempMail()
        email = mail.generate_email()
        if not email:
            print("[-] Gagal generate email, skip akun ini.")
            client.sessions.stop(session.id)
            continue

        depan = random.choice(NGARAN_DEPAN)
        tukang = random.choice(NGARAN_TUKANG)
        print(f"[+] Profil: {depan} {tukang} | Reff: {ref_code}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(session.ws_endpoint)
                context = browser.new_context()
                page = context.new_page()

                print("[*] Membuka muse.ai via cloud US...")
                page.goto("https://muse.ai/", timeout=60000)
                time.sleep(4)

                # 1. Input Email
                print(f"[*] Mengisi email: {email}")
                email_input = page.locator("input[placeholder='Mobile number or email']")
                email_input.click()
                time.sleep(0.5)
                email_input.type(email, delay=100)
                time.sleep(1)
                page.locator("button[type='submit']", has_text="Continue").click()

                # 2. Wait OTP
                otp = mail.wait_for_otp(timeout=120, interval=6)
                if not otp:
                    print("[-] OTP timeout / tidak masuk.")
                    browser.close()
                    client.sessions.stop(session.id)
                    continue

                # 3. Input OTP via API directly to prevent UI navigation target closed errors
                print(f"[*] Konfirmasi OTP ({otp}) via API langsung...")
                res_data = page.evaluate(f"""async () => {{
                    let r1 = await fetch('/api/auth/native/restart', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{}})
                    }});
                    let d1 = await r1.json();
                    let csrf = d1.csrf_token;
                    
                    let r2 = await fetch('/api/auth/native/confirm-otp', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'x-hatch-csrf-token': csrf
                        }},
                        body: JSON.stringify({{"otp_code": "{otp}"}})
                    }});
                    return {{status: r2.status, json: await r2.json(), csrf: csrf}};
                }}""")
                print("[+] API Confirm OTP Result:", res_data)

                time.sleep(5)

                # 4. Register Completion via API
                dob = "1995-05-15"
                print(f"[*] Register Completion ({depan} {tukang}) via API...")
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
                    return {{status: r.status, json: await r.json()}};
                }}""")
                print("[+] API Register Completion Result:", reg_res)

                time.sleep(4)

                # 5. Redeem Referral via API
                if ref_code:
                    print(f"[*] Menanam kode referral ({ref_code})...")
                    redeem_res = page.evaluate(f"""async (code) => {{
                        let r = await fetch('/api/hatch/invite-code/redeem', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{"code": code, "supportsRedemptionStatus": true}})
                        }});
                        return await r.json();
                    }}""", ref_code)
                    print("[+] Redeem Result:", redeem_res)

                page.screenshot(path=f"/home/agentuser/muse/screenshot_akun_{i}.png")
                browser.close()

                # Save to Jestco.txt
                with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
                    f.write(f"{email}:SecurePass123! # {depan} {tukang} | Reff: {ref_code}\n")
                print(f"[+] AKUN {i} SUKSES DICATAT KE Jestco.txt!")

        except Exception as e:
            print(f"[-] Error pada akun {i}: {e}")
        finally:
            print(f"[*] Menghentikan sesi Hyperbrowser {session.id}...")
            try:
                client.sessions.stop(session.id)
            except Exception:
                pass
            time.sleep(3)

if __name__ == "__main__":
    run_production_bot("FO3DHT", total_accounts=1)
