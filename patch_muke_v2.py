with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Let us find lines around candak_domain_surel
new_lines = []
skip = False
for line in lines:
    if "def candak_domain_surel" in line:
        new_lines.append("from temp_mail_helper import TempMail\n")
        new_lines.append("_GLOBAL_MAIL_OBJ = None\n\n")
        new_lines.append("def surel_sakedap_anyar():\n")
        new_lines.append("    global _GLOBAL_MAIL_OBJ\n")
        new_lines.append("    _GLOBAL_MAIL_OBJ = TempMail()\n")
        new_lines.append("    surel = _GLOBAL_MAIL_OBJ.generate_email()\n")
        new_lines.append("    if not surel:\n")
        new_lines.append("        gagal('email', 'Gagal generate email dari mail.tm')\n")
        new_lines.append("    catet('email', f'temp email (mail.tm): {surel}')\n")
        new_lines.append("    return surel\n\n")
        new_lines.append("def antos_otp(surel, timeout=BATAS_ANTOS_OTP, id_diabaikan=frozenset()):\n")
        new_lines.append("    global _GLOBAL_MAIL_OBJ\n")
        new_lines.append("    catet('otp', f'menunggu email OTP via mail.tm ({timeout}s) ...')\n")
        new_lines.append("    if not _GLOBAL_MAIL_OBJ:\n")
        new_lines.append("        gagal('otp', 'TempMail instance belum diinisialisasi')\n")
        new_lines.append("    otp = _GLOBAL_MAIL_OBJ.wait_for_otp(timeout=timeout, interval=SELANG_ANTOS_OTP)\n")
        new_lines.append("    if not otp:\n")
        new_lines.append("        gagal('otp', 'OTP tidak datang dari mail.tm')\n")
        new_lines.append("    catet('otp', 'kode OTP diterima')\n")
        new_lines.append("    return otp\n\n")
        skip = True
    elif skip and "def merek_kartu" in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("SUCCESS v2: muke.py patched successfully!")
