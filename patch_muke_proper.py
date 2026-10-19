with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    orig = f.read()

# 1. Add HB session functions at top
hb_code = """
import requests as preq
HB_API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

def make_hb_session():
    headers = {"x-api-key": HB_API_KEY, "Content-Type": "application/json"}
    try:
        res = preq.post("https://api.hyperbrowser.ai/api/session", headers=headers, json={}, timeout=30)
        if res.status_code == 200:
            data = res.json()
            print(f"[HB] Sesi Hyperbrowser US Aktif! ID: {data.get('id')}")
            return data.get("id")
    except Exception as e:
        print(f"[HB] Gagal buat sesi: {e}")
    return None

def stop_hb_session(session_id):
    if not session_id:
        return
    headers = {"x-api-key": HB_API_KEY, "Content-Type": "application/json"}
    try:
        preq.put(f"https://api.hyperbrowser.ai/api/session/{session_id}/stop", headers=headers, timeout=30)
        print("[HB] Sesi Hyperbrowser dihentikan.")
    except Exception:
        pass
"""

# 2. Replace TempMail functions
idx = orig.find("def surel_sakedap_anyar")
idx2 = orig.find("def merek_kartu")

mailtm_code = """
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
def surel_sakedap_anyar():
    global _GLOBAL_MAIL_OBJ
    _GLOBAL_MAIL_OBJ = TempMail()
    surel = _GLOBAL_MAIL_OBJ.generate_email()
    if not surel:
        print("[-] Gagal generate email")
        sys.exit(1)
    return surel

def antos_otp(surel, timeout=150, id_diabaikan=frozenset()):
    global _GLOBAL_MAIL_OBJ
    if not _GLOBAL_MAIL_OBJ:
        print("[-] TempMail belum diinisialisasi")
        sys.exit(1)
    otp = _GLOBAL_MAIL_OBJ.wait_for_otp(timeout=timeout, interval=5)
    if not otp:
        print("[-] OTP tidak datang")
        sys.exit(1)
    return otp

def candak_kotak(surel):
    return []

def cokot_otp(daptar_pesen):
    return None
"""

if idx != -1 and idx2 != -1:
    new_orig = hb_code + "\n" + orig[:idx] + "\n" + mailtm_code + "\n" + orig[idx2:]
    
    # Fix backslash in f-string for BIN detection by escaping properly
    new_orig = new_orig.replace("re.sub(r'\\D', '', nomer)", "re.sub(r'\\\\D', '', nomer)")

    # Trigger make_hb_session inside mimitian_alur
    new_orig = new_orig.replace("def mimitian_alur():", "def mimitian_alur():\n    hb_id = make_hb_session()", 1)

    with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
        f.write(new_orig)
    print("SUCCESS: Proper patched muke.py generated!")
else:
    print("ERROR indices:", idx, idx2)
