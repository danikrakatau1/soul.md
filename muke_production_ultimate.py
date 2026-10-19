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
    print("🤖 MUKE HYPERBROWSER PRODUCTION BOT (US IP TUNNEL)")
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
                page.locator("input[placeholder='Mobile number or email']").fill(email)
                time.sleep(1)
                page.locator("button[type='submit']", has_text="Continue").click()

                # 2. Wait OTP
                otp = mail.wait_for_otp(timeout=120, interval=6)
                if not otp:
                    print("[-] OTP timeout / tidak masuk.")
                    browser.close()
                    client.sessions.stop(session.id)
                    continue

                # 3. Input OTP via UI naturally
                print(f"[*] Memasukkan OTP ({otp})...")
                time.sleep(2)
                page.keyboard.type(otp, delay=150)
                time.sleep(3)

                try:
                    confirm_btn = page.locator("button", has_text="Confirm")
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click()
                except Exception:
                    pass

                time.sleep(5)

                # 4. Fill Name
                print(f"[*] Mengisi Nama: {depan} {tukang}...")
                try:
                    inputs = page.locator("input[type='text']")
                    if inputs.count() >= 2:
                        inputs.first.fill(depan)
                        time.sleep(0.5)
                        inputs.nth(1).fill(tukang)
                except Exception as e:
                    print(f"[-] Catatan isi nama: {e}")

                time.sleep(2)
                try:
                    confirm_btn = page.locator("button", has_text="Confirm")
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click()
                except Exception:
                    pass

                time.sleep(4)

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
            client.sessions.stop(session.id)
            time.sleep(3)

if __name__ == "__main__":
    run_production_bot("FO3DHT", total_accounts=1)
