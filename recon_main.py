import urllib.request
import urllib.error

domain = "https://galeriundanganofficial.com"

paths = [
    "/",
    "/wp-json/",
    "/phpmyadmin/",
    "/adminer.php",
    "/xmlrpc.php",
    "/wp-login.php"
]

print(f"=== CHECKING MAIN DOMAIN {domain} ===")
for path in paths:
    url = domain + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"[OK] {url} -> Status: {res.status}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP Error] {url} -> Status: {e.code}")
    except Exception as e:
        print(f"[Error] {url} -> {e}")
