import sys
import time
import random
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Temp Mail ---
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
def run_full_bot():
    print("="*50)
    print("🤖 Muke Full Automation Bot (Standalone)")
    print("="*50)

    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal generate email!")
        return

    depan = random.choice(NGARAN_DEPAN)
    tukang = random.choice(NGARAN_TUKANG)
    dob = f"{random.randint(1985, 2002):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    print(f"[+] Profil: {depan} {tukang} | DOB: {dob}")

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Origin": DASAR_MUSE,
        "Referer": DASAR_MUSE + "/"
    })

    try:
        print("[*] Mengakses landing page Muse...")
        s.get(DASAR_MUSE + "/", timeout=20)
        
        print("[*] Mengirim request restart flow...")
        r_restart = s.post(f"{DASAR_MUSE}/api/auth/native/restart", json={}, timeout=20)
        if r_restart.status_code != 200:
            print("[-] Gagal restart flow:", r_restart.text[:200])
            return
        
        csrf = r_restart.json().get("csrf_token")
        if not csrf:
            print("[-] CSRF token tidak ditemukan:", r_restart.text[:200])
            return
        
        print(f"[+] CSRF Token didapat: {csrf[:10]}...")
        s.headers["x-hatch-csrf-token"] = csrf

        print(f"[*] Mengirim OTP ke {email}...")
        r_otp = s.post(f"{DASAR_MUSE}/api/auth/native/send-otp", json={"contact_point": email, "region": "US"}, timeout=20)
        print(f"[+] Status Kirim OTP: {r_otp.status_code}, Resp: {r_otp.text[:150]}")

        otp = mail.wait_for_otp(timeout=120, interval=5)
        if not otp:
            print("[-] OTP tidak masuk.")
            return

        print("[*] Mengonfirmasi OTP...")
        r_confirm = s.post(f"{DASAR_MUSE}/api/auth/native/confirm-otp", json={"otp_code": otp}, timeout=20)
        print(f"[+] Confirm OTP Resp:", r_confirm.text[:150])

        print("[*] Menyelesaikan pendaftaran (Register Completion)...")
        r_reg = s.post(f"{DASAR_MUSE}/api/auth/native/register-completion", json={
            "date_of_birth": dob,
            "first_name": depan,
            "last_name": tukang,
            "tos_content_version": "ntm_create_account:default_v1_meta_account_v2+docs_v1"
        }, timeout=20)
        print(f"[+] Register Completion Resp:", r_reg.text[:200])

        with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
            f.write(f"{email}:SecurePass123! # FullBot ({depan} {tukang})\n")
        print("[SUCCESS] Akun berhasil dibuat dan disimpan ke Jestco.txt!")

    except Exception as e:
        print(f"[-] Terjadi error: {e}")

if __name__ == "__main__":
    run_full_bot()
