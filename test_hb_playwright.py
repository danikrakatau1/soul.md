import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

print("[*] Memulai Hyperbrowser session...")
client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print(f"[+] Sesi aktif! ID: {session.id}")
print(f"[+] WS Endpoint: {session.ws_endpoint}")

try:
    with sync_playwright() as p:
        print("[*] Menghubungkan Playwright ke remote browser Hyperbrowser...")
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context()
        page = context.new_page()
        
        print("[*] Membuka muse.ai landing page...")
        page.goto("https://muse.ai/", timeout=60000)
        print(f"[+] Judul Halaman: {page.title()}")
        
        # Cek IP di browser cloud
        page.goto("http://ip-api.com/json/", timeout=30000)
        content = page.content()
        print(f"[+] Info IP Cloud Browser: {content[:200]}")
        
        browser.close()
finally:
    print("[*] Menghentikan sesi Hyperbrowser...")
    client.sessions.stop(session.id)
    print("[+] Selesai!")
