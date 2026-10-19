with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip_count = 0
for idx, line in enumerate(lines, 1):
    if "teangan_nagara_ti_bin" in line or "print(warna(f\"   🔍 BIN" in line:
        if "teangan_nagara_ti_bin" in line:
            new_lines.append(line)
        continue
    if "f\"   🔍 BIN" in line or "RESMI.get(otomatis" in line:
        continue
    if idx in (1676, 1677):
        new_lines.append('        clean_bin = "".join(filter(str.isdigit, str(nomer or "")))[:6]\n')
        new_lines.append('        print(warna(f"   🔍 BIN {clean_bin} terdeteksi: {RESMI.get(otomatis, otomatis)} ({otomatis})", "c"))\n')
        continue
    new_lines.append(line)

with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned BIN fstring!")
