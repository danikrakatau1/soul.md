with open("/home/agentuser/muse/muke_hyperbrowser_full.py", "r", encoding="utf-8") as f:
    code = f.read()

with open("/home/agentuser/muse/temp_mail_helper.py", "r", encoding="utf-8") as f:
    helper_code = f.read()

# Replace import temp_mail_helper with helper_code inline
code = code.replace("from temp_mail_helper import TempMail", helper_code)

with open("/home/agentuser/muse/muke_hyperbrowser_standalone.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Standalone Hyperbrowser script generated!")
