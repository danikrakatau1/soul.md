import base64
import hashlib
import json
import os
import random
import re
import string
import sys
import time
import uuid
import urllib3
import requests
from curl_cffi import requests as cr

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Mail.tm Temp Mail Helper Standalone ---
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
        gagal('email', 'Gagal generate email dari mail.tm')
    catet('email', f'temp email (mail.tm): {surel}')
    return surel

def antos_otp(surel, timeout=BATAS_ANTOS_OTP, id_diabaikan=frozenset()):
    global _GLOBAL_MAIL_OBJ
    catet('otp', f'menunggu email OTP via mail.tm ({timeout}s) ...')
    if not _GLOBAL_MAIL_OBJ:
        gagal('otp', 'TempMail instance belum diinisialisasi')
    otp = _GLOBAL_MAIL_OBJ.wait_for_otp(timeout=timeout, interval=SELANG_ANTOS_OTP)
    if not otp:
        gagal('otp', 'OTP tidak datang dari mail.tm')
    catet('otp', 'kode OTP diterima')
    return otp

def candak_kotak(surel):
    global _GLOBAL_MAIL_OBJ
    if not _GLOBAL_MAIL_OBJ:
        return []
    msgs = _GLOBAL_MAIL_OBJ.get_messages()
    return [{'id': m.get('id'), 'body': m.get('intro', '')} for m in msgs]

def cokot_otp(daptar_pesen):
    global _GLOBAL_MAIL_OBJ
    if not _GLOBAL_MAIL_OBJ:
        return None
    return _GLOBAL_MAIL_OBJ.wait_for_otp(timeout=5, interval=1)
