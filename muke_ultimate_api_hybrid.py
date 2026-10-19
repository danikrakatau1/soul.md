import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

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
def run_hybrid_automation(ref_code="FO3DHT"):
    print("="*60)
    print("🤖 Muke Hyperbrowser HYBRID API + UI Bot")
    print("="*60)

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
            time.sleep(5)

            # Step 5: Restart & Send OTP via API inside browser
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

            print("[*] Tunggu 10 detik sebelum confirm-otp (anti rate-limit)...")
            time.sleep(10)

            # Wait for OTP
            otp = mail.wait_for_otp(timeout=150, interval=6)
            if not otp:
                print("[-] OTP tidak ditemukan!")
                if 'browser' in locals() and browser is not None:
                    browser.close()
                client.sessions.stop(session.id)
                return False

            # Step 6: Confirm OTP via API FIRST before doing anything on UI
            print(f"[*] 6. Konfirmasi OTP ({otp}) langsung via API...")
            conf_res = page.evaluate(f"""async (data) => {{
                let r = await fetch('/api/auth/native/confirm-otp', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': data.csrf
                    }},
                    body: JSON.stringify({{"otp_code": data.otp}})
                }});
                return {{status: r.status, json: await r.json()}};
            }}""", {"csrf": res_data["csrf"], "otp": otp})
            print("[+] Confirm OTP API Resp:", conf_res)

            if conf_res.get("status") != 200 and conf_res.get("status") != 201:
                print(f"[-] Confirm OTP gagal (status {conf_res.get('status')})! Menghentikan...")
                if 'browser' in locals() and browser is not None:
                    browser.close()
                client.sessions.stop(session.id)
                return False

            time.sleep(4)

            # Step 7: Register Completion via API
            dob = "1995-05-15"
            print(f"[*] 7. Register Completion ({depan} {tukang}) via API...")
            reg_res = page.evaluate(f"""async (data) => {{
                let r = await fetch('/api/auth/native/register-completion', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'x-hatch-csrf-token': data.csrf
                    }},
                    body: JSON.stringify({{
                        "date_of_birth": data.dob,
                        "first_name": data.depan,
                        "last_name": data.tukang,
                        "tos_content_version": "ntm_create_account:default_v1_meta_account_v2+docs_v1"
                    }})
                }});
                return {{status: r.status, json: await r.json()}};
            }}""", {"csrf": res_data["csrf"], "dob": dob, "depan": depan, "tukang": tukang})
            print("[+] Register Completion API Resp:", reg_res)

            if reg_res.get("status") not in [200, 201]:
                print(f"[-] Register gagal (status {reg_res.get('status')})! Menghentikan...")
                if 'browser' in locals() and browser is not None:
                    browser.close()
                client.sessions.stop(session.id)
                return False

            time.sleep(3)

            # Step 8: Navigate to /access and click Get Started
            print("[*] 8. Navigasi ke /access...")
            page.goto("https://muse.ai/access", timeout=60000)
            time.sleep(3)

            print("[*] Mencari tombol 'Get Started'...")
            get_started = page.locator("text=Get Started").first
            if get_started.is_visible():
                print("[+] Tombol 'Get Started' ditemukan! Klik...")
                get_started.click()
                time.sleep(5)

                current_url = page.url
                print(f"[+] URL setelah Get Started: {current_url}")

                if "verification" in current_url.lower() or "verifikasi" in current_url.lower():
                    print("[!] KENA CC/VCC (Verif Umur)! Redirect ke halaman verifikasi.")
                    page.screenshot(path="/home/agentuser/muse/screenshot_verification.png")
                    print("[+] Screenshot verifikasi saved.")
                    print(f"[!] Cek manual: https://muse.ai/access/verification")
                    if 'browser' in locals() and browser is not None:
                        browser.close()
                    client.sessions.stop(session.id)
                    return False
                else:
                    print("[+] LOLOS CC/VCC! Lanjut ke redeem...")
                    page.screenshot(path="/home/agentuser/muse/screenshot_after_getstarted.png")
            else:
                print("[-] Tombol 'Get Started' tidak ditemukan!")
                print(f"[!] URL sekarang: {page.url}")
                page.screenshot(path="/home/agentuser/muse/screenshot_no_getstarted.png")
                print(f"[!] Cek manual: https://muse.ai/access/verification")

            time.sleep(3)

            # Step 9: Redeem Referral via API
            if ref_code:
                print(f"[*] 8. Menanam kode referral ({ref_code})...")
                redeem_res = page.evaluate(f"""async (code) => {{
                    let r = await fetch('/api/hatch/invite-code/redeem', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{"code": code, "supportsRedemptionStatus": true}})
                    }});
                    return await r.json();
                }}""", ref_code)
                print("[+] Redeem API Resp:", redeem_res)

            time.sleep(3)
            page.screenshot(path="/home/agentuser/muse/screenshot_final.png")
            print("[+] Screenshot final saved.")

            if 'browser' in locals() and browser is not None:
                browser.close()

            # Only save to Jestco.txt if all steps succeeded
            with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:SecurePass123! # {depan} {tukang} | Reff: {ref_code}\n")
            print("[+] Sukses! Akun dicatat ke Jestco.txt")
            return True

    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        print("[*] Menghentikan sesi Hyperbrowser...")
        client.sessions.stop(session.id)

if __name__ == "__main__":
    run_hybrid_automation("FO3DHT")
