#!/usr/bin/env python3
import subprocess
import sys
import time

def run_cmd(cmd):
    print(f"[RUN] {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr and res.returncode != 0:
        print(f"[STDERR] {res.stderr}")
    return res.returncode == 0

def main():
    print("=" * 60)
    print("🌐 INSTALLING CLOUDFLARE WARP VPN ON VPS 🌐")
    print("=" * 60)

    # 1. Install prerequisites & Cloudflare GPG key
    print("[*] Menambahkan repository Cloudflare WARP...")
    run_cmd("sudo apt-get update && sudo apt-get install -y curl gpg lsb-release")
    
    # Add GPG key
    run_cmd("curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg")
    
    # Add source list
    codename = subprocess.run("lsb_release -cs", shell=True, text=True, capture_output=True).stdout.strip()
    source_line = f"deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com {codename} main"
    run_cmd(f"echo '{source_line}' | sudo tee /etc/apt/sources.list.d/cloudflare-client.list")

    # 2. Update & Install cloudflare-warp
    print("[*] Menginstal paket cloudflare-warp...")
    if not run_cmd("sudo apt-get update && sudo apt-get install -y cloudflare-warp"):
        print("[-] Gagal menginstal cloudflare-warp!")
        sys.exit(1)

    # 3. Register & Connect WARP
    print("[*] Mendaftarkan klien WARP...")
    run_cmd("warp-cli --accept-tos registration new")
    
    print("[*] Mengatur mode proxy / warp...")
    run_cmd("warp-cli --accept-tos mode proxy")
    run_cmd("warp-cli --accept-tos proxy port 40000") # Set local SOCKS5 proxy port

    print("[*] Menghubungkan ke Cloudflare WARP...")
    run_cmd("warp-cli --accept-tos connect")

    time.sleep(3)
    
    # 4. Check status
    print("[*] Mengecek status WARP:")
    run_cmd("warp-cli status")

    print("\n[SUCCESS] Cloudflare WARP berhasil diinstal & aktif! 🚀")
    print("[+] SOCKS5 proxy lokal aktif di: socks5://127.0.0.1:40000")
    print("[+] Silakan gunakan proxy ini di script bot Anda untuk bypass blokir!")

if __name__ == "__main__":
    main()
