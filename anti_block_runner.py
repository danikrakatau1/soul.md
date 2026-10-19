#!/usr/bin/env python3
import sys
import os
import random
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, '/home/agentuser/muse')
import joe_source

def human_jitter(min_sec=3.0, max_sec=6.0):
    delay = random.uniform(min_sec, max_sec)
    print(f"[*] Menunggu jeda natural (human-like): {delay:.2f} detik...")
    time.sleep(delay)

def run_anti_block_flow():
    print("=" * 60)
    print("🛡️  TOR + CLOUDFLARE WARP AUTO-FARMING (100% GRATIS) 🛡️")
    print("=" * 60)

    # 1. Pilih Referral Code
    ref_input = input("Masukkan Referral Code [Default: 4Y14U7]: ").strip()
    ref_code = ref_input if ref_input else '4Y14U7'
    joe_source.CFG['ref_code'] = ref_code
    print(f"[+] Referral Code diset: {ref_code}")

    # 2. Gunakan Tor SOCKS5 Proxy Lokal (127.0.0.1:9050) - 100% Gratis & Anonym
    tor_proxy = 'socks5://127.0.0.1:9050'
    joe_source.PROXIES = {'http': tor_proxy, 'https': tor_proxy}
    joe_source.CFG['proxy_enabled'] = True
    joe_source.CFG['proxy'] = tor_proxy
    print(f"[+] Menggunakan Tor Anonymity Proxy: {tor_proxy}")

    # 3. Generate Email Sementara Otomatis via Jestco
    print("[*] Menyiapkan email sementara bersih...")
    try:
        email = joe_source.new_temp_email()
        print(f"[+] Berhasil generate email otomatis: {email}")
    except Exception as e:
        print(f"[-] Gagal generate email: {e}")
        return

    human_jitter(2.0, 4.0)

    # 4. Jalankan Pendaftaran & Redeem Reff
    print(f"[*] Menjalankan registrasi & redeem reff melalui Tor Network...")
    try:
        joe_source.flow_register_cli(email)
        print(f"[SUCCESS] Flow register & redeem reff selesai untuk {email}! 🎉")
    except Exception as e:
        print(f"[-] Terhenti pada flow: {e}")

if __name__ == "__main__":
    run_anti_block_flow()
