import sys
import time
import os
import random
import requests
import time
import re
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

    print("[*] 2. Generate Temp Mail...")
    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal membuat temp email!")
        client.sessions.stop(session.id)
        return False
    print(f"[+] Temp Email siap: {email}")

    depan = random.choice(NGARAN_DEPAN)
    tukang = random.choice(NGARAN_TUKANG)
    dob = f"{random.randint(1985, 2002):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    print(f"[+] Profil Akun: {depan} {tukang} | DOB: {dob}")

    try:
        with sync_playwright() as p:
            print("[*] 3. Menghubungkan Playwright ke remote browser Hyperbrowser...")
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.new_context()
            page = context.new_page()

            print("[*] 4. Membuka muse.ai...")
            page.goto("https://muse.ai/", timeout=60000)
            time.sleep(3)

            # Input Email ke placeholder 'Mobile number or email'
            print(f"[*] 5. Mengisi email: {email}")
            page.locator("input[placeholder='Mobile number or email']").fill(email)
            time.sleep(1)

            # Klik tombol Continue
            print("[*] 6. Klik tombol Continue...")
            page.locator("button[type='submit']", has_text="Continue").click()

            print("[*] 7. Menunggu email OTP dari mail.tm / 1secmail...")
            otp = mail.wait_for_otp(timeout=120, interval=5)
            if not otp:
                print("[-] OTP tidak ditemukan!")
                browser.close()
                client.sessions.stop(session.id)
                return False
            
            print(f"[+] OTP Diterima: {otp}")

            # Input OTP
            print("[*] 8. Memasukkan kode OTP...")
            time.sleep(3)
            # Coba isi input OTP (biasanya muncul setelah email di-submit)
            try:
                page.locator("input[type='text'], input[placeholder*='code'], input[placeholder*='OTP']").first.fill(otp)
                time.sleep(1)
                page.keyboard.press("Enter")
            except Exception as e:
                print(f"[-] Catatan input OTP: {e}")

            time.sleep(5)
            page.screenshot(path="/home/agentuser/muse/screenshot_final.png")
            print("[+] Screenshot final disimpan ke /home/agentuser/muse/screenshot_final.png")

            browser.close()
            return True

    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        print("[*] Menghentikan sesi Hyperbrowser...")
        client.sessions.stop(session.id)

if __name__ == "__main__":
    run_full_automation()
