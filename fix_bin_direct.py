with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "BIN" in line and "re.sub" in line:
        line = '        print(warna(f"   🔍 BIN terdeteksi: {RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))\n'
    new_lines.append(line)

with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed BIN line directly!")
