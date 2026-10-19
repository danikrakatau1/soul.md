import requests
import time

# Proxy sources
SOURCES = {
    "proxmint": "https://raw.githubusercontent.com/proxmint/free-proxy-list/main/proxies/all.txt",
    "maximilian": "https://raw.githubusercontent.com/maximilianfeix/free-proxy-list/main/all.txt"
}

def get_proxies():
    all_proxies = set()
    for name, url in SOURCES.items():
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                proxies = resp.text.splitlines()
                all_proxies.update(proxies)
                print(f"[+] Loaded {len(proxies)} from {name}")
        except Exception as e:
            print(f"[!] Error loading {name}: {e}")
    return list(all_proxies)

def test_proxy(proxy):
    # Basic check via httpbin
    # Expecting format protocol://ip:port or ip:port
    try:
        proxies = {"http": proxy, "https": proxy}
        resp = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)
        if resp.status_code == 200:
            return True
    except:
        return False
    return False

if __name__ == "__main__":
    candidates = get_proxies()[:50]  # Check first 50 to save time
    working = []
    print(f"[*] Testing {len(candidates)} candidates...")
    for p in candidates:
        if test_proxy(p):
            working.append(p)
            print(f"[OK] {p}")
            if len(working) >= 5: break
    
    with open("working_proxies.txt", "w") as f:
        f.write("\n".join(working))
    print(f"[*] Found {len(working)} working proxies. Saved to working_proxies.txt")
