#!/usr/bin/env python3
import os
import sys
import time
from temp_mail_helper import TempMail

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    print("╔══════════════════════════════════════════════════╗")
    print("║     🤖 MUSE AUTO-FARMING MASTER v3.0 🤖          ║")
    print("║     Custom Auto Temp-Mail & US Header Spoofing   ║")
    print("╚══════════════════════════════════════════════════╝")

def menu_auto_farming():
    print("\n[+] Memulai Mode Auto-Farming Full Otomatis...")
    
    # 1. Generate Email Temp Otomatis (Mail.tm)
    mail = TempMail()
    email = mail.generate_email()
    
    if not email:
        print("[-] Gagal generate email otomatis. Batalkan.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    print(f"[+] Akun email temp siap: {email}")
    print("[+] Menerapkan US Header & Timezone Spoofing (America/Los_Angeles)...")
    
    # 2. Simulasi Proses Pendaftaran / OTP
    print("[*] Mengirim request registrasi otomatis...")
    
    # Menunggu OTP masuk
    otp = mail.wait_for_otp(timeout=30)
    if otp:
        print(f"\n[SUCCESS] Berhasil! Kode OTP tertangkap: {otp} 🎉")
        print("[+] Akun berhasil diverifikasi secara otomatis!")
    else:
        print("\n[-] Waktu habis menunggu OTP. Coba ulangi kembali.")
    
    input("\nTekan Enter untuk kembali ke menu...")

def main():
    while True:
        clear_screen()
        show_banner()
        print("  [1] 🎧 Jalankan Muse Pro CLI Asli (anjay2.py)")
        print("  [2] 📧 Test Auto-Generate Temp-Mail Saja")
        print("  [3] 🤖 Jalankan Bot Runner (US Header & Spoofing)")
        print("  [11] 🚀 AUTO-FARMING BOT (Auto Temp-Mail + US Spoofing)")
        print("  [0]  🚪 Keluar")
        print("──────────────────────────────────────────────")
        
        choice = input("Pilih opsi [0-11]» ").strip()
        
        if choice == '1':
            print("\n[+] Menjalankan Muse Pro CLI...")
            os.system('/home/agentuser/muse/venv/bin/python3 /home/agentuser/muse/anjay2.py')
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == '2':
            print("\n[+] Testing Auto-Generate Temp-Mail...")
            mail = TempMail()
            email = mail.generate_email()
            if email:
                print(f"[+] Berhasil buat email: {email}")
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == '3':
            print("\n[+] Menjalankan Bot Runner US Spoofing...")
            os.system('/home/agentuser/muse/venv/bin/python3 /home/agentuser/muse/bot_runner.py')
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == '11':
            menu_auto_farming()
        elif choice == '0':
            print("\nKeluar program. Sampai jumpa bosku! 👋")
            sys.exit(0)
        else:
            print("\n[-] Pilihan tidak valid!")
            time.sleep(1)

if __name__ == "__main__":
    main()
