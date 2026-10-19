import sys
import time
import os
import re
from temp_mail_helper import TempMail

sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

def run_hyperbrowser_signup():
    print("[*] Membuat sesi Hyperbrowser di cloud US...")
    client = Hyperbrowser(api_key=API_KEY)
    session = client.sessions.create()
    print(f"[+] Sesi aktif! ID: {session.id}")
    print(f"[+] WS Endpoint: {session.ws_endpoint}")

    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal membuat temp email!")
        client.sessions.stop(session.id)
        return False
    
    print(f"[+] Temp Email siap: {email}")

    try:
        with sync_playwright() as p:
            print("[*] Menghubungkan Playwright ke remote browser Hyperbrowser...")
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.new_context()
            page = context.new_page()

            print("[*] Membuka muse.ai...")
            page.goto("https://muse.ai/", timeout=60000)
            time.sleep(3)

            print(f"[+] URL Saat Ini: {page.url}")
            print(f"[+] Judul Halaman: {page.title()}")

            page.screenshot(path="/home/agentuser/muse/screenshot.png")
            print("[+] Screenshot disimpan ke /home/agentuser/muse/screenshot.png")

            browser.close()
            return True

    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        client.sessions.stop(session.id)

if __name__ == "__main__":
    run_hyperbrowser_signup()
