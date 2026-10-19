import sys
import time
import random
import re
import requests
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
def hb_fetch(url):
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    try:
        res = requests.post("https://api.hyperbrowser.ai/api/web/fetch", headers=headers, json={"url": url}, timeout=30)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

if __name__ == "__main__":
    print("=== Muke Hyperbrowser Pure REST Bot ===")
    mail = TempMail()
    email = mail.generate_email()
    print(f"[+] Temp Email Generated: {email}")
    
    data = hb_fetch("https://muse.ai/")
    if data:
        print("[+] Sukses fetch muse.ai via Hyperbrowser Cloud API!")
        print(data.get("data", {}).get("metadata", {}).get("title", "OK"))
