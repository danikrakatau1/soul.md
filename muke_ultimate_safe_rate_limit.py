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
def run_safe_automation_with_delays(ref_code="FO3DHT"):
    print("="*60)
    print("🤖 Muke Hyperbrowser ULTIMATE SAFE ANTI-RATE-LIMIT Bot")
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
            
            # Jeda manusiawi pertama (warming up browser session)
            print("[*] Jeda warming up sesi (5 detik)...")
            time.sleep(5)

            # Step 5: Input email secara natural menggunakan type() dengan delay
            print(f"[*] 5. Mengisi email {email} secara natural...")
            email_input = page.locator("input[placeholder='Mobile number or email']")
            email_input.click()
            time.sleep(1)
            email_input.type(email, delay=120)
            time.sleep(2)

            print("[*] 6. Klik tombol Continue...")
            page.locator("button[type='submit']", has_text="Continue").click()
            
            # Jeda ekstra setelah kirim OTP supaya server Meta tidak menganggap spam
            print("[*] Jeda menunggu server mengirim OTP (8 detik)...")
            time.sleep(8)

            # Wait for OTP
            otp = mail.wait_for_otp(timeout=150, interval=6)
            if not otp:
                print("[-] OTP tidak ditemukan!")
                browser.close()
                client.sessions.stop(session.id)
                return False

            # Step 7: Masukkan OTP dengan jeda natural per digit
            print(f"[*] 7. Memasukkan OTP ({otp}) digit demi digit secara natural...")
            time.sleep(3)
            try:
                page.locator("input[type='text']").first.click()
                time.sleep(1)
            except Exception:
                pass

            for char in otp:
                page.keyboard.press(char)
                time.sleep(random.uniform(0.2, 0.4)) # Jeda acak antar digit ala manusia
            
            time.sleep(4)

            # Klik Confirm OTP jika tombolnya ada
            try:
                confirm_btn = page.locator("button", has_text="Confirm")
                if confirm_btn.is_visible(timeout=4000):
                    confirm_btn.click()
                    print("[+] Tombol Confirm OTP diklik!")
            except Exception:
                pass

            # Jeda manusiawi sebelum lanjut ke pengisian nama
            print("[*] Jeda stabilisasi setelah konfirmasi OTP (6 detik)...")
            time.sleep(6)

            # Step 8: Isi Nama Depan dan Belakang dengan jeda natural
            print(f"[*] 8. Mengisi Nama ({depan} {tukang}) secara natural...")
            try:
                inputs = page.locator("input[type='text']")
                if inputs.count() >= 2:
                    inputs.first.click()
                    time.sleep(0.5)
                    inputs.first.type(depan, delay=100)
                    time.sleep(1)
                    inputs.nth(1).click()
                    time.sleep(0.5)
                    inputs.nth(1).type(tukang, delay=100)
            except Exception as e:
                print(f"[-] Catatan isi nama UI: {e}")

            time.sleep(3)
            try:
                confirm_btn = page.locator("button", has_text="Confirm")
                if confirm_btn.is_visible(timeout=4000):
                    confirm_btn.click()
                    print("[+] Tombol Confirm nama diklik!")
            except Exception:
                pass

            # Jeda sebelum redeem referral
            print("[*] Jeda stabilisasi akhir sebelum redeem referral (5 detik)...")
            time.sleep(5)

            # Step 9: Redeem referral via page.evaluate
            print(f"[*] 9. Menanam kode referral ({ref_code})...")
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
            print("[+] Screenshot final saved.")

            browser.close()
            
            # Save account to Jestco.txt
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
    run_safe_automation_with_delays("FO3DHT")
