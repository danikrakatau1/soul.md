with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for idx, line in enumerate(lines, 1):
    if idx in (1565, 1566):
        if idx == 1565:
            new_lines.append('        clean_bin = "".join(filter(str.isdigit, str(nomer)))[:6]\n')
            new_lines.append('        print(warna(f"   🔍 BIN {clean_bin} terdeteksi: " f"{RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))\n')
        continue
    new_lines.append(line)

with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned syntax!")
