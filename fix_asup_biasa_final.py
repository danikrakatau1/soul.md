with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the condition in _asup_biasa so it ALWAYS uses antos_otp() instead of input('OTP: ')
old_block = """    if OTP_PANYADIA is not None:
        otp = OTP_PANYADIA(surel)
    elif '@' in surel and surel.split('@')[1] in _domain_jestco():
        otp = antos_otp(surel, id_diabaikan=katempo)
    else:
        otp = input('OTP: ').strip()"""

new_block = """    if OTP_PANYADIA is not None:
        otp = OTP_PANYADIA(surel)
    else:
        otp = antos_otp(surel, id_diabaikan=katempo)"""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: _asup_biasa forced to use antos_otp automatically!")
else:
    print("WARNING: old_block not found exactly")
