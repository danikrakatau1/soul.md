with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    code = f.read()

# Fix backslash in f-string at line 1565-1566
old_snippet = """    if otomatis:
        print(warna(f"   🔍 BIN {re.sub(r'\\D', '', nomer)[:6]} terdeteksi: "
                  f"{RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))"""

new_snippet = """    if otomatis:
        clean_nomer = re.sub(r'\\D', '', nomer)[:6] if nomer else ''
        print(warna(f"   🔍 BIN {clean_nomer} terdeteksi: "
                  f"{RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))"""

if old_snippet in code:
    code = code.replace(old_snippet, new_snippet)
else:
    # Alternative replacement
    code = code.replace('re.sub(r\'\\D\', \'\', nomer)[:6]', 're.sub(r\"\\D\", \"\", nomer)[:6]')

with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Syntax fixed!")
