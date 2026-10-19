import random
import time
from temp_mail_helper import TempMail

# Daftar User-Agent acak untuk spoofing fingerprint browser (Poin 2)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def get_random_headers():
    """Menghasilkan headers dengan User-Agent acak & US Header Spoofing"""
    ua = random.choice(USER_AGENTS)
    
    # Trik Header Spoofing Lokasi US (Biar disangka user dari Amerika)
    us_locales = ["en-US,en;q=0.9", "en-US;q=0.8,en;q=0.7"]
    timezones = ["America/New_York", "America/Los_Angeles", "America/Chicago"]
    
    return {
        "User-Agent": ua,
        "Accept-Language": random.choice(us_locales),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "X-Timezone": random.choice(timezones), # Custom Header simulasi timezone US
        "Cache-Control": "no-cache"
    }

def run_automation_workflow():
    print("=" * 60)
    print("[*] Memulai Bot Auto-Farming + US Header Spoofing")
    print("=" * 60)

    # 1. Pilih User-Agent & Header US acak untuk sesi ini
    headers = get_random_headers()
    print(f"[+] Sesi menggunakan User-Agent: {headers['User-Agent'][:40]}...")
    print(f"[+] Spoofing Lokasi/Bahasa: {headers['Accept-Language']} | Timezone: {headers['X-Timezone']}")

    # 2. Generate Email Sementara Otomatis (Mail.tm)
    mail = TempMail()
    email = mail.generate_email()
    
    if not email:
        print("[-] Gagal generate email temp. Batalkan proses.")
        return

    # 3. Simulasi Pendaftaran / Request Target
    print(f"[*] Mensimulasikan pendaftaran akun dengan email: {email}")
    
    # Contoh pakai requests / curl_cffi dengan US Headers
    # response = requests.post("https://api.target.com/register", json={"email": email}, headers=headers, verify=False)

    # 4. Menunggu dan Menangkap Kode OTP Otomatis
    otp = mail.wait_for_otp(timeout=10)
    
    if otp:
        print(f"[SUCCESS] Akun berhasil diverifikasi dengan OTP: {otp} 🎉")
    else:
        print("[-] Waktu habis, OTP tidak ditemukan.")

if __name__ == "__main__":
    run_automation_workflow()
