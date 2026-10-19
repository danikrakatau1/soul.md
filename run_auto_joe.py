#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, '/home/agentuser/muse')
import joe_source

def main():
    print("==================================================")
    print("🤖 AUTO-FARMING JOE'S ENGINE: MANUAL & AUTO MODE 🤖")
    print("==================================================")
    
    # Pilih Referral Code
    ref_input = input("Masukkan Referral Code [Default: 4Y14U7]: ").strip()
    ref_code = ref_input if ref_input else '4Y14U7'
    joe_source.CFG['ref_code'] = ref_code
    print(f"[+] Referral Code diset: {ref_code}")

    print("\nPilih Mode Pendaftaran:")
    print("  [1] 🤖 Auto Mode (Temp-mail otomatis + Auto OTP)")
    print("  [2] 👤 Manual Mode (Input Email Sendiri + Ketik OTP Manual)")
    
    mode = input("Pilih mode [1/2, default 1]: ").strip()
    if not mode:
        mode = '1'

    if mode == '2':
        email = input("Masukkan email Anda (contoh: email@gmail.com): ").strip()
        if not email:
            print("[-] Email tidak boleh kosong!")
            return
        print(f"[*] Menjalankan registrasi dengan email manual: {email}")
        try:
            joe_source.flow_register_cli(email)
            print(f"[SUCCESS] Flow selesai untuk {email}!")
        except Exception as e:
            print(f"[-] Terhenti pada flow: {e}")
    else:
        try:
            email = joe_source.new_temp_email()
            print(f"[+] Berhasil generate email otomatis: {email}")
        except Exception as e:
            print(f"[-] Gagal generate email: {e}")
            return

        print(f"[*] Menjalankan registrasi & redeem reff untuk: {email}")
        try:
            joe_source.flow_register_cli(email)
            print(f"[SUCCESS] Flow register & redeem reff selesai untuk {email}!")
        except Exception as e:
            print(f"[-] Terhenti pada flow: {e}")

if __name__ == "__main__":
    main()
