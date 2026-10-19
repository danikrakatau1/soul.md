import urllib.request
import urllib.error

base_url = "https://web.galeriundanganofficial.com"

db_paths = [
    "/phpmyadmin/",
    "/pma/",
    "/adminer.php",
    "/db/",
    "/database/",
    "/mysql/",
    "/sql/",
    "/dump.sql",
    "/backup.sql",
    "/wp-content/uploads/backup.sql"
]

print("=== CHECKING FOR EXPOSED DATABASE INTERFACES & DUMPS ===")
for path in db_paths:
    url = base_url + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"[FOUND] {url} -> Status: {res.status} (Size: {len(res.read())} bytes)")
    except urllib.error.HTTPError as e:
        print(f"[MISSING/BLOCKED] {url} -> Status: {e.code}")
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
