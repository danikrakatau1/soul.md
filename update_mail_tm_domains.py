with open("/home/agentuser/muse/temp_mail_helper.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let us modify temp_mail_helper.py to support custom/random domains or allow fallback to 1secmail / guerrillamail / custom catchall if needed, 
# or let us add a few more free public temp mail API alternatives inside temp_mail_helper.py
# For example, 1secmail API: https://www.1secmail.com/api/v1/
print("Checking temp_mail_helper.py...")
