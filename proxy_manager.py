import requests
import concurrent.futures
import threading

# Configuration
INPUT_SOURCES = {
    "proxmint": "https://raw.githubusercontent.com/proxmint/free-proxy-list/main/proxies/all.txt",
    "maximilian": "https://raw.githubusercontent.com/maximilianfeix/free-proxy-list/main/all.txt"
}
TEST_URL = "http://httpbin.org/ip"
OUTPUT_FILE = "/home/agentuser/muse/working_proxies.txt"
TIMEOUT = 5 # seconds

def fetch_proxies():
    proxies = set()
    for name, url in INPUT_SOURCES.items():
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.splitlines()
                # Clean up if some are already formatted
                for line in lines:
                    line = line.replace('http://', '').replace('socks5://', '').strip()
                    if line: proxies.add(line)
        except Exception as e:
            print(f"[!] Error fetching {name}: {e}")
    return list(proxies)

def test_proxy(proxy):
    try:
        # Test as HTTP proxy first
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        resp = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        if resp.status_code == 200:
            return proxy
    except:
        return None
    return None

def main():
    print("[*] Fetching new proxy candidates...")
    candidates = fetch_proxies()
    print(f"[*] Found {len(candidates)} total candidates. Testing in parallel...")
    
    working = []
    # Use ThreadPoolExecutor for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(test_proxy, p): p for p in candidates[:200]} # Test first 200
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                working.append(result)
                print(f"[OK] {result}")
    
    # Save working proxies
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(working))
    
    print(f"\n[*] Scan complete. Saved {len(working)} working proxies to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
