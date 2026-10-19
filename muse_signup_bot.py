"""
muse.ai Auto Signup Bot via Hyperbrowser Cloud Browser
======================================================
Cara pakai:
1. Daftar gratis di https://app.hyperbrowser.ai (login Google)
2. Ambil API key dari dashboard
3. Jalankan: python muse_signup_bot.py

Butuh:
  pip install hyperbrowser playwright
  playwright install chromium
"""

import os
import sys
import time
import random
import string
from playwright.sync_api import sync_playwright
from hyperbrowser import Hyperbrowser

# ============================================================
# KONFIGURASI - isi di sini
# ============================================================
HYPERBROWSER_API_KEY = os.environ.get("HYPERBROWSER_API_KEY", "ISI_API_KEY_DISINI")

# Email yang mau didaftarkan (bisa pakai mail.tm atau gmail baru)
EMAIL = "emailkamu@gmail.com"

# Tanggal lahir (harus 18+ tahun)
DOB_MONTH = "January"
DOB_DAY   = "15"
DOB_YEAR  = "1995"

# Invite code buat redeem 1B token
INVITE_CODE = "FTITRD"  # ganti dengan kode kamu sendiri
# ============================================================


def wait(sec=1.5):
    time.sleep(sec + random.uniform(0, 0.8))


def run_signup():
    print("[*] Mulai sesi Hyperbrowser cloud browser...")
    client = Hyperbrowser(api_key=HYPERBROWSER_API_KEY)

    session = client.sessions.create({
        "use_stealth": True,
        "screen": {"width": 1366, "height": 768},
    })

    print(f"[*] Session ID: {session.id}")
    print(f"[*] WS Endpoint: {session.ws_endpoint}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0]

            # --- Step 1: Buka halaman signup ---
            print("[*] Buka muse.ai/join ...")
            page.goto("https://muse.ai/join", timeout=30000)
            wait(3)
            print(f"[*] Title: {page.title()}")

            # Screenshot state awal
            page.screenshot(path="/home/agentuser/muse/screen_step1.png")
            print("[*] Screenshot disimpan: screen_step1.png")

            body_text = page.inner_text("body")
            print("[*] Halaman berisi:", body_text[:300])

            # --- Step 2: Isi email ---
            print("[*] Isi email...")
            try:
                # Coba cari input email
                email_input = page.locator("input[type='email'], input[placeholder*='email' i], input[name*='email' i]").first
                email_input.fill(EMAIL)
                wait(1)
                # Klik tombol lanjut / Continue
                page.locator("button:has-text('Continue'), button:has-text('Next'), button:has-text('Sign up'), button:has-text('Create')").first.click()
                wait(2)
            except Exception as e:
                print(f"[!] Error isi email: {e}")

            page.screenshot(path="/home/agentuser/muse/screen_step2.png")
            print("[*] Screenshot step2 disimpan")

            # --- Step 3: Cek apakah ada verifikasi atau sudah masuk ---
            body_text2 = page.inner_text("body")
            print("[*] State setelah email:", body_text2[:500])

            wait(2)
            print("\n[*] Selesai! Cek screenshot di folder /home/agentuser/muse/")
            print("[*] Jika berhasil masuk, redeem invite code:", INVITE_CODE)
            print("[*] Settings -> Redeem Code -> masukkan dalam 48 jam!")

            browser.close()

    finally:
        print("[*] Menutup sesi...")
        client.sessions.stop(session.id)
        print("[*] Done.")


if __name__ == "__main__":
    if HYPERBROWSER_API_KEY == "ISI_API_KEY_DISINI":
        print("="*60)
        print("ERROR: Belum isi API key!")
        print("")
        print("Cara dapat API key GRATIS:")
        print("1. Buka: https://app.hyperbrowser.ai")
        print("2. Login dengan Google")
        print("3. Pergi ke Settings/Dashboard")
        print("4. Copy API key")
        print("5. Set env variable:")
        print("   export HYPERBROWSER_API_KEY='hb-xxxxxxxx'")
        print("   python muse_signup_bot.py")
        print("="*60)
        sys.exit(1)

    run_signup()
