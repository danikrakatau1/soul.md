with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace jestco email functions with TempMail integration
old_section = """def _sesi_surel():
    s = cr.Session(impersonate='chrome', proxies=PROKSI)
    s.headers.update({'User-Agent': UA})
    return s

def candak_domain_surel(cobaan=3):
    s = _sesi_surel()
    ngaran_tukang = None
    for a in range(cobaan):
        try:
            r = s.get(API_JESTCO, params={'action': 'get_public_config'}, timeout=30)
            data = r.json()
            daptar_domain = data.get('temp_email_domains') or data.get('domains') or []
            if daptar_domain:
                catet('email', f'{len(daptar_domain)} domain temp tersedia')
                return daptar_domain
            ngaran_tukang = r.text[:120]
        except Exception as e:
            ngaran_tukang = f'{type(e).__name__}: {e}'
        time.sleep(2 * (a + 1))
    gagal('email', f'get_public_config gagal {cobaan}x: {ngaran_tukang}')

def surel_sakedap_anyar():
    daptar_domain = candak_domain_surel()
    lokal = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    surel = f'{lokal}@{random.choice(daptar_domain)}'
    catet('email', f'temp email: {surel}')
    return surel

def candak_kotak(surel):
    s = _sesi_surel()
    r = s.get(API_JESTCO, params={'to': surel}, timeout=30)
    try:
        data = r.json()
    except ValueError:
        return []
    return data if isinstance(data, list) else data.get('messages', [])

def cokot_otp(daptar_pesen):
    for m in daptar_pesen:
        awak = m.get('body') or m.get('text') or ''
        subj = m.get('subject') or ''
        teks = awak + ' ' + subj
        for pola in ('Confirmation code (\\d{6})', 'Use code (\\d{6})', '\\b(\\d{6})\\b.{0,40}(log in|masuk)', 'code is (\\d{6})', 'kode (\\d{6})'):
            bulan = re.search(pola, teks, re.IGNORECASE)
            if bulan:
                return bulan.group(1)
    return None

def antos_otp(surel, timeout=BATAS_ANTOS_OTP, id_diabaikan=frozenset()):
    catet('otp', f'menunggu email OTP ({timeout}s) ...')
    tenggat = time.time() + timeout
    while time.time() < tenggat:
        pesen2 = [m for m in candak_kotak(surel) if str(m.get('id')) not in id_diabaikan]
        otp = cokot_otp(pesen2)
        if otp:
            catet('otp', 'kode OTP diterima')
            return otp
        time.sleep(SELANG_ANTOS_OTP)
    gagal('otp', 'OTP tidak datang')"""

new_section = """from temp_mail_helper import TempMail

_GLOBAL_MAIL_OBJ = None

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
"""

if old_section in code:
    code = code.replace(old_section, new_section)
    with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: muke.py successfully patched with mail.tm!")
else:
    print("WARNING: exact old_section not found, checking alternative...")
