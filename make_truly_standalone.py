with open("/home/agentuser/muse/muke_hyperbrowser_full.py", "r", encoding="utf-8") as f:
    code = f.read()

with open("/home/agentuser/muse/temp_mail_helper.py", "r", encoding="utf-8") as f:
    helper = f.read()

# Replace import
code = code.replace("from temp_mail_helper import TempMail", helper)

with open("/home/agentuser/muse/muke_hyperbrowser_full.py", "w", encoding="utf-8") as f:
    f.write(code)

print("muke_hyperbrowser_full.py is now truly standalone!")
