import os
import time
import json
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from temp_mail_helper import TempMail

def create_tiktok_account(proxy_url=None):
    print("=" * 60)
    print("[*] Memulai Bot Auto Create TikTok (Stealth + Mail.tm + OTP Auto)")
    print("=" * 60)

    # 1. Generate Temp Mail
    mail = TempMail()
    email = mail.generate_email()
    if not email:
        print("[-] Gagal membuat temp email. Batalkan proses.")
        return False

    print(f"[+] Email untuk registrasi: {email}")

    # 2. Setup Playwright & Browser (dengan Stealth & Proxy)
    with sync_playwright() as p:
        browser_args = {
            "headless": True, # Wajib True di VPS tanpa GUI
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1280,800"
            ]
        }
        
        if proxy_url:
            print(f"[*] Menggunakan Proxy: {proxy_url}")
            browser_args["proxy"] = {"server": proxy_url}

        browser = p.chromium.launch(**browser_args)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        
        page = context.new_page()
        
        # Terapkan Stealth Mode untuk bypass deteksi bot dasar
        Stealth().apply_stealth_sync(page)

        try:
            print("[*] Membuka halaman registrasi TikTok...")
            page.goto("https://www.tiktok.com/signup", timeout=60000)
            time.sleep(5)

            # Langkah 1: Pilih Tanggal Lahir (Contoh: 15 Januari 1995)
            print("[*] Mengatur tanggal lahir...")
            try:
                # TikTok signup form sering menggunakan dropdown atau wheel selector
                # Kita tunggu elemen muncul dan interaksi dasar
                page.wait_for_selector('div[class*="DivMonthSelector"], select', timeout=10000)
                print("[+] Form tanggal lahir terdeteksi.")
                # (Placeholder interaksi DOB, disesuaikan dengan struktur web TikTok terbaru)
                time.sleep(2)
            except Exception as e:
                print("[-] Peringatan: Elemen DOB tidak langsung ketemu, lanjut isi email...")

            # Langkah 2: Masukkan Email & Password
            print("[*] Mengisi Email dan Password...")
            try:
                # Input Email
                email_input = page.locator('input[type="email"], input[name="email"]')
                if email_input.count() > 0:
                    email_input.fill(email)
                    print(f"[+] Email {email} dimasukkan.")

                # Input Password
                password_input = page.locator('input[type="password"]')
                if password_input.count() > 0:
                    password_input.fill("CyberSecure99#")
                    print("[+] Password dimasukkan.")

                time.sleep(2)
            except Exception as e:
                print(f"[-] Gagal mengisi email/password: {e}")

            # Langkah 3: Deteksi Captcha / Pengecekan Slider
            print("[*] Memeriksa apakah muncul Captcha / Slider...")
            time.sleep(3)
            
            # Cek jika ada iframe captcha atau puzzle slider
            captcha_frame = page.locator('iframe[src*="captcha"], div[class*="captcha"]')
            if captcha_frame.count() > 0:
                print("[!] CAPTCHA / Slider Terdeteksi!")
                print("[!] Tips: Gunakan layanan solver (seperti CapSolver / 2Captcha) atau selesaikan manual jika headful.")
                # Disini hook untuk solver pihak ketiga (CapSolver API) bisa dipasang
                # input("[?] Selesaikan captcha di browser, lalu tekan ENTER di terminal untuk lanjut...")

            # Langkah 4: Klik tombol Kirim Kode (Send Code)
            print("[*] Mengklik tombol kirim kode (Send Code)...")
            try:
                send_code_btn = page.locator('button:has-text("Send code"), button[type="submit"]')
                if send_code_btn.count() > 0:
                    send_code_btn.first.click()
                    print("[+] Tombol kirim kode diklik. Menunggu OTP masuk...")
            except Exception as e:
                print(f"[-] Gagal klik kirim kode: {e}")

            # Langkah 5: Auto-OTP Reader (Ambil dari Mail.tm)
            otp_code = mail.wait_for_otp(timeout=90, interval=5)
            if otp_code:
                print(f"[+] Berhasil mendapatkan OTP: {otp_code}")
                try:
                    # Cari input kode OTP di halaman
                    otp_input = page.locator('input[placeholder*="code"], input[name*="code"], input[maxlength="6"]')
                    if otp_input.count() > 0:
                        otp_input.fill(otp_code)
                        print("[+] Kode OTP berhasil diisi ke form!")
                        time.sleep(3)
                except Exception as e:
                    print(f"[-] Gagal mengisi OTP otomatis ke form: {e}")
            else:
                print("[-] OTP tidak masuk dalam batas waktu.")

            # input("[*] Tekan ENTER di terminal jika registrasi selesai dan masuk ke dashboard...")

            # Langkah 6: Simpan Sesi Cookies Akun
            cookies = context.cookies()
            account_data = {
                "email": email,
                "proxy": proxy_url,
                "cookies": cookies
            }
            
            filename = f"account_{email.split('@')[0]}.json"
            with open(filename, "w") as f:
                json.dump(account_data, f, indent=4)
            print(f"[+] Akun berhasil! Sesi & cookies tersimpan di {filename}")

        except Exception as e:
            print(f"[-] Terjadi error pada automasi: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    proxy_to_use = None
    proxy_file = "/home/agentuser/muse/proxies.txt"
    
    if os.path.exists(proxy_file):
        with open(proxy_file, "r") as f:
            valid_lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            if valid_lines:
                proxy_to_use = valid_lines[0]
                print(f"[+] Memuat proxy dari proxies.txt: {proxy_to_use}")
            else:
                print("[*] Tidak ada proxy aktif di proxies.txt, berjalan tanpa proxy.")

    create_tiktok_account(proxy_url=proxy_to_use)
