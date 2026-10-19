with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    code = f.read()

# Fix the backslash inside f-string by precomputing the cleaned bin string
old_target = """    otomatis = teangan_nagara_ti_bin(nomer) if nomer else None
    if otomatis:
        print(warna(f"   🔍 BIN {re.sub(r'\\D', '', nomer)[:6]} terdeteksi: "
                  f"{RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))"""

new_target = """    otomatis = teangan_nagara_ti_bin(nomer) if nomer else None
    if otomatis:
        clean_bin = "".join(filter(str.isdigit, str(nomer or '')))[:6]
        print(warna(f"   🔍 BIN {clean_bin} terdeteksi: "
                  f"{RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))"""

if old_target in code:
    code = code.replace(old_target, new_target)
    with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Fixed backslash f-string!")
else:
    print("WARNING: old_target not found")
