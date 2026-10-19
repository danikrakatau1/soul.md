import urllib.request
import urllib.error
import urllib.parse

target_url = "https://web.galeriundanganofficial.com/wp-admin/admin-ajax.php"

actions = [
    "elementor_ajax",
    "weddingpress_rsvp",
    "rsvp_submit",
    "wp_ajax_nopriv_elementor_ajax",
    "get_wedding_data",
    "load_more_posts",
    "revslider_ajax_action"
]

print(f"=== PROBING ADMIN-AJAX.PHP ACTIONS ON {target_url} ===")
for action in actions:
    data = urllib.parse.urlencode({'action': action}).encode('utf-8')
    try:
        req = urllib.request.Request(target_url, data=data, headers={'User-Agent': 'Mozilla/5.0'}, method='POST')
        res = urllib.request.urlopen(req, timeout=5)
        print(f"[Action: {action}] -> Status: {res.status}, Length: {len(res.read())}")
    except urllib.error.HTTPError as e:
        print(f"[Action: {action}] -> HTTP Error: {e.code}")
    except Exception as e:
        print(f"[Action: {action}] -> Error: {e}")
