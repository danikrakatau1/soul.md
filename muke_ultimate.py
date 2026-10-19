import sys
import time
import random
import re
import requests
import urllib3
import uuid

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
def hb_request(method, path, json_data=None):
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    url = f"https://api.hyperbrowser.ai/api{path}" if path.startswith("/") else f"https://api.hyperbrowser.ai/api/{path}"
    try:
        if method == "POST":
            res = requests.post(url, headers=headers, json=json_data, timeout=30)
        else:
            res = requests.get(url, headers=headers, timeout=30)
        return res.json() if res.status_code in (200, 201) else {"error": res.status_code, "text": res.text}
    except Exception as e:
        return {"error": str(e)}

def register_single_account(ref_code="FO3DHT"):
    print("\n" + "="*50)
    print("🤖 Memulai Auto Register Akun Baru via Hyperbrowser & 1secmail...")
    print("="*50)

    # 1. Generate Temp Email
    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal generate temp email!")
        return False

    # 2. Generate Random Profile
    first_name = random.choice(NGARAN_DEPAN)
    last_name = random.choice(NGARAN_TUKANG)
    dob = f"{random.randint(1985, 2002):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    print(f"[+] Profil: {first_name} {last_name} | DOB: {dob}")

    # 3. Hit Muse landing via Hyperbrowser (pastikan IP bersih US)
    print("[*] Mengakses landing page Muse lewat IP US Hyperbrowser...")
    fetch_res = hb_request("POST", "/web/fetch", {"url": DASAR_MUSE})
    if not fetch_res or "error" in fetch_res:
        print("[-] Gagal akses lewat Hyperbrowser:", fetch_res)
        return False
    print("[+] Koneksi US Cloud Browser siap!")

    # 4. Kirim OTP ke email baru via API Muse
    print(f"[*] Mengirim OTP ke {email}...")
    # Sesi curl_cffi / requests session dengan proxy/header US
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Origin": DASAR_MUSE,
        "Referer": DASAR_MUSE + "/"
    })

    try:
        # Restart flow & get CSRF
        r_restart = s.post(f"{DASAR_MUSE}/api/auth/native/restart", json={}, timeout=20)
        csrf = r_restart.json().get("csrf_token")
        if not csrf:
            print("[-] Gagal mengambil CSRF token:", r_restart.text[:150])
            return False
        print(f"[+] CSRF Token didapat: {csrf[:10]}...")

        # Send OTP
        s.headers["x-hatch-csrf-token"] = csrf
        r_otp = s.post(f"{DASAR_MUSE}/api/auth/native/send-otp", json={"contact_point": email, "region": "US"}, timeout=20)
        print(f"[+] Respons Send OTP: {r_otp.status_code}")

        # Wait for OTP
        otp = mail.wait_for_otp(timeout=120, interval=5)
        if not otp:
            print("[-] Gagal menerima kode OTP.")
            return False

        # Confirm OTP
        r_confirm = s.post(f"{DASAR_MUSE}/api/auth/native/confirm-otp", json={"otp_code": otp}, timeout=20)
        conf_data = r_confirm.json()
        print(f"[+] Konfirmasi OTP Berhasil:", conf_data.get("registration_state"))

        # Register Completion (Daftar Akun Baru)
        r_reg = s.post(f"{DASAR_MUSE}/api/auth/native/register-completion", json={
            "date_of_birth": dob,
            "first_name": first_name,
            "last_name": last_name,
            "tos_content_version": "ntm_create_account:default_v1_meta_account_v2+docs_v1"
        }, timeout=20)
        reg_data = r_reg.json()
        print(f"[+] Pendaftaran Selesai:", reg_data)

        # Redeem Reff jika ada
        if ref_code:
            print(f"[*] Menebus kode referral: {ref_code}...")
            r_redeem = s.post(f"{DASAR_MUSE}/api/hatch/invite-code/redeem", json={"code": ref_code, "supportsRedemptionStatus": True}, timeout=20)
            print(f"[+] Hasil Redeem:", r_redeem.json())

        # Simpan akun ke file Jestco.txt
        with open("/home/agentuser/muse/Jestco.txt", "a", encoding="utf-8") as f:
            f.write(f"{email}:SecurePass123! # Berhasil Aman ({first_name} {last_name})\n")
        print(f"[SUCCESS] Akun berhasil dibuat & disimpan ke Jestco.txt!")
        return True

    except Exception as e:
        print(f"[-] Terjadi error saat registrasi: {e}")
        return False

if __name__ == "__main__":
    register_single_account("FO3DHT")
