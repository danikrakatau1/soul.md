with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the condition in _asup_biasa so it always triggers antos_otp for mail.tm
old_cond = """    elif '@' in surel and surel.split('@')[1] in _domain_jestco():
        otp = antos_otp(surel, id_diabaikan=katempo)
    else:
        otp = input('OTP: ').strip()"""

new_cond = """    else:
        otp = antos_otp(surel, id_diabaikan=katempo)"""

if old_cond in code:
    code = code.replace(old_cond, new_cond)
    with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: _asup_biasa patched to force automatic mail.tm OTP reading!")
else:
    print("WARNING: old_cond not found exactly")
