with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for idx, line in enumerate(lines, 1):
    if "re.sub" in line and "\\" in line:
        # Replace f-string with backslash or pre-compute
        line = line.replace('re.sub(r\'\\D\',', 're.sub(r\"\\D\",')
    new_lines.append(line)

with open("/home/agentuser/muse/muke.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed backslashes!")
