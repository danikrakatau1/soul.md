from curl_cffi import requests

target_url = "https://lightvela.ai"
print(f"[*] Menguji bypass Cloudflare/EdgeOne dengan curl_cffi ke {target_url}...")

try:
    # Meniru browser Chrome
    response = requests.get(target_url, impersonate="chrome110", timeout=10)
    print(f"[+] Status Code: {response.status_code}")
    print(f"[+] Panjang Konten: {len(response.text)} bytes")
    print("[+] Berhasil tembus! Header Server:", response.headers.get("server", "Tidak diketahui"))
except Exception as e:
    print("[-] Gagal:", e)
