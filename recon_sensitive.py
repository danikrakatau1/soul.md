import urllib.request
import urllib.error

base_url = "https://web.galeriundanganofficial.com"

paths = [
    "/robots.txt",
    "/sitemap.xml",
    "/xmlrpc.php",
    "/wp-links-opml.php",
    "/wp-config.php.bak",
    "/.env",
    "/backup.zip",
    "/wp-content/debug.log",
    "/wp-json/wp/v2/users",
    "/wp-json/wp/v2/posts",
]

print("=== CHECKING SENSITIVE FILES & ENDPOINTS ===")
for path in paths:
    url = base_url + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"[FOUND] {url} -> Status: {res.status} (Size: {len(res.read())} bytes)")
    except urllib.error.HTTPError as e:
        print(f"[MISSING/BLOCKED] {url} -> Status: {e.code}")
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
