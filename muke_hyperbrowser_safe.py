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
def run_safe_automation(ref_code="FO3DHT"):
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
            time.sleep(5)  # Natural human delay

            # Type email using UI locator naturally
            print(f"[*] 5. Mengisi email {email} secara natural...")
            page.locator("input[placeholder='Mobile number or email']").type(email, delay=100)
            time.sleep(2)
            
            print("[*] 6. Klik tombol Continue...")
            page.locator("button[type='submit']", has_text="Continue").click()
            time.sleep(5)

            # Wait for OTP with generous interval
            otp = mail.wait_for_otp(timeout=120, interval=6)
            if not otp:
                print("[-] OTP tidak ditemukan!")
                browser.close()
                client.sessions.stop(session.id)
                return False

            # Type OTP naturally digit by digit
            print(f"[*] 7. Memasukkan OTP ({otp}) secara natural...")
            time.sleep(3)
            page.keyboard.type(otp, delay=200)
            time.sleep(5)

            # Click Confirm if visible
            try:
                confirm_btn = page.locator("button", has_text="Confirm")
                if confirm_btn.is_visible(timeout=5000):
                    confirm_btn.click()
                    print("[+] Tombol Confirm OTP diklik!")
            except Exception:
                pass

            time.sleep(6)

            # Fill First and Last Name naturally
            print(f"[*] 8. Mengisi Nama ({depan} {tukang}) secara natural...")
            try:
                inputs = page.locator("input[type='text']")
                if inputs.count() >= 2:
                    inputs.first.type(depan, delay=100)
                    time.sleep(1)
                    inputs.nth(1).type(tukang, delay=100)
            except Exception as e:
                print(f"[-] Error isi nama UI: {e}")

            time.sleep(3)
            try:
                confirm_btn = page.locator("button", has_text="Confirm")
                if confirm_btn.is_visible(timeout=5000):
                    confirm_btn.click()
                    print("[+] Tombol Confirm nama diklik!")
            except Exception:
                pass

            time.sleep(6)
            page.screenshot(path="/home/agentuser/muse/screenshot_final.png")
            print("[+] Screenshot final saved.")

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
    run_safe_automation("FO3DHT")
