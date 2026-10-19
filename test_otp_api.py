import requests
import time
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Let us check mail.tm messages for the latest code
base_url = "https://box.celana-ar-store.my.id"
# Let us get domains first
res = requests.get(f"{base_url}/domains", verify=False)
print("Domains:", res.status_code, res.json())
