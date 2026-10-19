with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    orig_code = f.read()

with open("/home/agentuser/muse/muke_standalone.py", "r", encoding="utf-8") as f:
    standalone_code = f.read()

idx = orig_code.find("def _sesi_surel")
idx2 = orig_code.find("def merek_kartu")

if idx != -1 and idx2 != -1:
    new_code = orig_code[:idx] + "\n\n" + standalone_code + "\n\n" + orig_code[idx2:]
    with open("/home/agentuser/muse/muke_final.py", "w", encoding="utf-8") as f:
        f.write(new_code)
    print("SUCCESS: muke_final.py created successfully!")
else:
    print("ERROR:", idx, idx2)
