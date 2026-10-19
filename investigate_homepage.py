import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")

from hyperbrowser import Hyperbrowser
from playwright.sync_api import sync_playwright
import time, requests, uuid, re
requests.packages.urllib3.disable_warnings()

API_KEY = "hb_cdfc571755daac8231b0c1812ec4"

def make_email():
    domains = requests.get("https://box.celana-ar-store.my.id/domains", verify=False, timeout=10).json()
    domain = domains["hydra:member"][0]["domain"]
    username = f"bot_{uuid.uuid4().hex[:8]}"
    email = f"{username}@{domain}"
    password = "SecurePass123!"
    requests.post("https://box.celana-ar-store.my.id/accounts", json={"address": email, "password": password}, verify=False, timeout=10)
    token = requests.post("https://box.celana-ar-store.my.id/token", json={"address": email, "password": password}, verify=False, timeout=10).json().get("token")
    return email, password, token

def get_otp(token):
    msgs = requests.get("https://box.celana-ar-store.my.id/messages", headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=10).json().get("hydra:member", [])
    if msgs:
        msg = requests.get(f"https://box.celana-ar-store.my.id/messages/{msgs[0]['id']}", headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=10).json()
        body = msg.get("text") or msg.get("intro") or ""
        m = re.search(r"\b\d{6}\b", body)
        if m:
            return m.group(0)
    return None

print("[*] Buat fresh email...")
email, password, mail_token = make_email()
print(f"[+] Email: {email}")

client = Hyperbrowser(api_key=API_KEY)
session = client.sessions.create()
print(f"[+] Session: {session.id}")

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://muse.ai/", timeout=60000)
        time.sleep(3)

        # Restart + Send OTP
        res_data = page.evaluate("""async () => {
            let r1 = await fetch('/api/auth/native/restart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
            let d1 = await r1.json();
            let csrf = d1.csrf_token;
            let r2 = await fetch('/api/auth/native/send-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-hatch-csrf-token': csrf
                },
                body: JSON.stringify({contact_point: '%s', region: 'US'})
            });
            return {status: r2.status, csrf: csrf};
        }""" % email)
        print(f"[+] Send OTP: {res_data}")

        time.sleep(10)

        # Tunggu OTP (retry lebih lama)
        otp = None
        for i in range(30):
            otp = get_otp(mail_token)
            if otp:
                break
            print(f"  [{i+1}/30] Nunggu OTP...")
            time.sleep(6)

        if not otp:
            print("[-] OTP gak masuk setelah 3 menit!")
            browser.close()
            client.sessions.stop(session.id)
            sys.exit(1)

        print(f"[+] OTP: {otp}")

        # Confirm OTP
        conf = page.evaluate("""async (data) => {
            let r = await fetch('/api/auth/native/confirm-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-hatch-csrf-token': data.csrf
                },
                body: JSON.stringify({otp_code: data.otp})
            });
            return {status: r.status, json: await r.json()};
        }""", {"csrf": res_data["csrf"], "otp": otp})
        print(f"[+] Confirm OTP: {conf}")

        time.sleep(3)

        # Register Completion
        reg = page.evaluate("""async (data) => {
            let r = await fetch('/api/auth/native/register-completion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-hatch-csrf-token': data.csrf
                },
                body: JSON.stringify({
                    date_of_birth: data.dob,
                    first_name: data.depan,
                    last_name: data.tukang,
                    tos_content_version: 'ntm_create_account:default_v1_meta_account_v2+docs_v1'
                })
            });
            return {status: r.status, json: await r.json()};
        }""", {"csrf": res_data["csrf"], "dob": "1995-05-15", "depan": "Sari", "tukang": "Wijaya"})
        print(f"[+] Register: {reg}")

        time.sleep(3)

        # Navigate ke /access
        page.goto("https://muse.ai/access", timeout=60000)
        time.sleep(5)
        print(f"[+] URL setelah /access: {page.url}")

        # Cek homepage content
        print(f"\n[*] Cek homepage content...")
        print(f"Title: {page.title()}")
        print(f"URL: {page.url}")

        # Cari semua button dan link
        buttons = page.locator("button").all()
        print(f"\n[*] Buttons found ({len(buttons)}):")
        for i, btn in enumerate(buttons):
            try:
                text = btn.inner_text(timeout=2000)
                visible = btn.is_visible()
                if visible and text.strip():
                    print(f"  [{i}] Button: '{text.strip()}'")
            except:
                pass

        # Cari link
        links = page.locator("a").all()
        print(f"\n[*] Links found ({len(links)}):")
        for i, link in enumerate(links):
            try:
                text = link.inner_text(timeout=2000)
                href = link.get_attribute("href")
                visible = link.is_visible()
                if visible and text.strip():
                    print(f"  [{i}] Link: '{text.strip()}' -> {href}")
            except:
                pass

        # Cari semua clickable elements yang visible
        print("\n[*] SEMUA CLICKABLE ELEMENTS:")
        clickables = page.locator("button, a, [role=button]").all()
        get_started_target = None
        for i, el in enumerate(clickables):
            try:
                text = el.inner_text(timeout=2000).strip()
                visible = el.is_visible()
                if visible and text and len(text) < 100:
                    tag = el.evaluate("e => e.tagName")
                    print(f"  [{i}] <{tag}> '{text}'")
                    if "get started" in text.lower() or "getstarted" in text.lower():
                        get_started_target = el
                        print(f"       ^^^ GET STARTED TARGET!")
            except:
                pass

        if get_started_target:
            print("\n[+] GET STARTED FOUND! Klik...")
            
            # Monitor page baru (new tab/window) setelah klik
            try:
                with context.expect_page(timeout=10000) as new_page_info:
                    get_started_target.click()
                new_page = new_page_info.value
                new_page.wait_for_load_state("networkidle")
                new_page_url = new_page.url
                print(f"[+] NEW PAGE terbuka! URL: {new_page_url}")
                new_page.screenshot(path="/home/agentuser/muse/screenshot_new_page.png")
                print("[+] Screenshot new page saved")
                
                if "verification" in new_page_url.lower():
                    print("[!] KENA VERIFIKASI!")
                else:
                    print(f"[+] LOLOS! New page URL: {new_page_url}")
                page = new_page
            except Exception as e:
                print(f"[-] Gak ada new page: {e}")
                # Fallback: cek URL page lama
                initial_url = page.url
                for wait in range(10):
                    time.sleep(2)
                    try:
                        current = page.url
                        if current != initial_url:
                            print(f"[+] URL berubah setelah {2*(wait+1)}s: {current}")
                            break
                        if wait % 3 == 2:
                            print(f"  [{2*(wait+1)}s] URL masih: {current}")
                    except:
                        print(f"  [{2*(wait+1)}s] Page udah tertutup")
                        break
                
                print(f"\n[+] URL final: {page.url if not page.is_closed() else 'page closed'}")

            # Cek page content setelah klik
            print(f"\n[*] Page content setelah Get Started:")
            try:
                if page.is_closed():
                    print("[!] Page sudah tertutup setelah klik Get Started")
                else:
                    print(f"Title: {page.title()}")
            except:
                print("[!] Page sudah tertutup setelah klik Get Started")
            
            # Cek modals, overlays
            modals = page.locator("[role=dialog], .modal, .overlay, [class*=modal], [class*=dialog]").all()
            print(f"Modals/overlays found: {len(modals)}")
            for i, m in enumerate(modals):
                try:
                    if m.is_visible():
                        txt = m.inner_text(timeout=2000)
                        print(f"  [{i}] Modal: {txt[:300]}")
                except:
                    pass

            # Cek semua visible elements lagi
            clickables2 = page.locator("button, a, [role=button]").all()
            print(f"\n[*] Clickable elements setelah Get Started ({len(clickables2)}):")
            for i, el in enumerate(clickables2):
                try:
                    text = el.inner_text(timeout=2000).strip()
                    visible = el.is_visible()
                    if visible and text and len(text) < 100:
                        tag = el.evaluate("e => e.tagName")
                        print(f"  [{i}] <{tag}> '{text}'")
                except:
                    pass

            # Cek apakah ada error message
            errors = page.locator("[class*=error], [class*=Error], .invalid").all()
            for i, err in enumerate(errors):
                try:
                    if err.is_visible():
                        print(f"  Error [{i}]: {err.inner_text(timeout=2000)}")
                except:
                    pass

            page.screenshot(path="/home/agentuser/muse/screenshot_after_getstarted.png", full_page=True)
            print("\n[+] Screenshot saved: /home/agentuser/muse/screenshot_after_getstarted.png")

            if "verification" in page.url.lower():
                print("\n[!] KENA VERIFIKASI!")
            else:
                print("\n[+] Gak ke redirect ke verifikasi.")
        else:
            print("\n[-] Get Started gak ditemukan di homepage")

        page.screenshot(path="/home/agentuser/muse/screenshot_homepage.png", full_page=True)
        print("\n[+] Screenshot saved: /home/agentuser/muse/screenshot_homepage.png")

        browser.close()
finally:
    client.sessions.stop(session.id)
