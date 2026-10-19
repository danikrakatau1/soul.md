import socket
import requests
import sys

def recon(domain):
    print(f"[*] Starting OSINT Recon for: {domain}")
    print("-" * 50)
    
    # 1. DNS Resolution
    try:
        ip = socket.gethostbyname(domain)
        print(f"[+] IP Address: {ip}")
    except Exception as e:
        print(f"[-] DNS Resolution failed: {e}")
        return

    # 2. HTTP Headers & Tech fingerprinting
    for proto in ["https", "http"]:
        url = f"{proto}://{domain}"
        try:
            resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            print(f"\n[+] HTTP Headers ({proto.upper()}):")
            for header, val in resp.headers.items():
                print(f"    {header}: {val}")
            break
        except Exception:
            continue

    # 3. Common Subdomain Discovery
    subdomains = ["www", "mail", "api", "admin", "staging", "dev", "shop", "login", "portal"]
    print(f"\n[*] Checking common subdomains for {domain}...")
    for sub in subdomains:
        sub_domain = f"{sub}.{domain}"
        try:
            sub_ip = socket.gethostbyname(sub_domain)
            print(f"    [FOUND] {sub_domain} -> {sub_ip}")
        except socket.gaierror:
            pass

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    recon(target)
