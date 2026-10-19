import sys
import time
import random
import os
import re
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. Dual-Engine Temp Mail (1secmail / Mail.tm) ---
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
def create_hb_session():
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    res = requests.post("https://api.hyperbrowser.ai/api/session", headers=headers, json={}, timeout=30)
    data = res.json()
    return data.get("wsEndpoint"), data.get("id")

def stop_hb_session(session_id):
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    requests.put(f"https://api.hyperbrowser.ai/api/session/{session_id}/stop", headers=headers, timeout=30)

def run_ultimate_automation(ref_code="FO3DHT"):
    print("="*50)
    print("🤖 Muke Ultimate Automation (Hyperbrowser + Playwright)")
    print("="*50)

    print("[*] 1. Membuat sesi Hyperbrowser cloud US...")
    ws_endpoint, session_id = create_hb_session()
    if not ws_endpoint:
        print("[-] Gagal membuat sesi Hyperbrowser!")
        return False
    print(f"[+] Sesi aktif! ID: {session_id}")

    print("[*] 2. Generate Temp Mail...")
    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal membuat temp email!")
        stop_hb_session(session_id)
        return False

    depan = random.choice(NGARAN_DEPAN)
    tukang = random.choice(NGARAN_TUKANG)
    dob = f"{random.randint(1985, 2002):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    print(f"[+] Profil Akun: {depan} {tukang} | DOB: {dob}")

    try:
        with sync_playwright() as p:
            print("[*] 3. Menghubungkan Playwright ke cloud browser Hyperbrowser...")
            browser = p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.new_context()
            page = context.new_page()

            print("[*] 4. Membuka muse.ai...")
            page.goto("https://muse.ai/", timeout=60000)
            time.sleep(3)

            print(f"[*] 5. Mengisi email: {email}")
            page.locator("input[placeholder='Mobile number or email']").fill(email)
            time.sleep(1)

            print("[*] 6. Klik tombol Continue...")
            page.locator("button[type='submit']", has_text="Continue").click()

            print("[*] 7. Menunggu email OTP masuk...")
            otp = mail.wait_for_otp(timeout=120, interval=5)
            if not otp:
                print("[-] OTP tidak ditemukan!")
                browser.close()
                stop_hb_session(session_id)
                return False
            
            print(f"[+] Kode OTP Diterima: {otp}")

            time.sleep(3)
            try:
                otp_input = page.locator("input[type='text'], input[placeholder*='code'], input[placeholder*='OTP']").first
                if otp_input.is_visible():
                    otp_input.fill(otp)
                    page.keyboard.press("Enter")
                    print("[+] OTP berhasil dimasukkan ke halaman!")
            except Exception as e:
                print(f"[-] Info input OTP UI: {e}")

            time.sleep(5)
            page.screenshot(path="/home/agentuser/muse/success_register.png")
            print("[+] Sesi automation selesai & screenshot disimpan!")

            with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:SecurePass123! # Berhasil Ultimate ({depan} {tukang})\n")

            browser.close()
            return True

    except Exception as e:
        print(f"[-] Error automation: {e}")
        return False
    finally:
        print("[*] Menghentikan sesi Hyperbrowser...")
        stop_hb_session(session_id)

if __name__ == "__main__":
    run_ultimate_automation("FO3DHT")
