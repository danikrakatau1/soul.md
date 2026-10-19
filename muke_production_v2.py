import sys
import time
import random
import os
import re
import requests
import uuid
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

def cleanup_active_sessions():
    try:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        res = requests.get("https://api.hyperbrowser.ai/api/sessions?status=active", headers=headers, timeout=10)
        if res.status_code == 200:
            for s in res.json().get("sessions", []):
                sid = s.get("id")
                requests.put(f"https://api.hyperbrowser.ai/api/session/{sid}/stop", headers=headers, json={}, timeout=10)
                print(f"[HB] Membersihkan sesi tertinggal: {sid}")
    except Exception as e:
        print(f"[-] Cleanup session error: {e}")

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
    print("🤖 MUKE HYPERBROWSER ULTIMATE PRODUCTION BOT V2 (Auto-Clean)")
    print("="*60)

    for i in range(1, total_accounts + 1):
        print(f"\n--- [AKUN {i}/{total_accounts}] ---")
        cleanup_active_sessions()
        
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

                # 1. Input Email naturally
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

                # 3. Input OTP via keyboard naturally
                print(f"[*] Memasukkan OTP ({otp})...")
                time.sleep(2)
                try:
                    page.locator("input[type='text']").first.click()
                    time.sleep(0.5)
                except Exception:
                    pass
                page.keyboard.type(otp, delay=150)
                time.sleep(3)

                try:
                    confirm_btn = page.locator("button", has_text="Confirm")
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click()
                except Exception:
                    pass

                time.sleep(5)

                # 4. Handle Birthday / Name fields robustly via JS injection
                print(f"[*] Mengisi Nama ({depan} {tukang}) & Tanggal Lahir...")
                page.evaluate(f"""(data) => {{
                    const inputs = document.querySelectorAll('input[type="text"]');
                    if (inputs.length >= 2) {{
                        inputs[0].value = data.depan;
                        inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        inputs[1].value = data.tukang;
                        inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                    const selects = document.querySelectorAll('select');
                    if (selects.length >= 3) {{
                        selects[0].value = '5';
                        selects[1].value = '15';
                        selects[2].value = '1995';
                        selects[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                        selects[1].dispatchEvent(new Event('change', {{ bubbles: true }}));
                        selects[2].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}""", {"depan": depan, "tukang": tukang})

                time.sleep(3)
                
                try:
                    confirm_btn = page.locator("button", has_text="Confirm")
                    if confirm_btn.is_visible(timeout=4000):
                        confirm_btn.click()
                        print("[+] Tombol Confirm diklik!")
                except Exception:
                    pass

                time.sleep(5)

                # 5. Redeem Referral via API fetch inside browser session
                print(f"[*] Menanam kode referral: {ref_code}...")
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
