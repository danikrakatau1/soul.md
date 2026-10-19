import asyncio
from curl_cffi import requests
from playwright.async_api import async_playwright

async def stealth_playwright_test():
    print("[*] Launching Playwright with Stealth Configuration...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        # Inject anti-detection scripts (navigator.webdriver = false, etc.)
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        page = await context.new_page()
        
        try:
            print("[*] Navigating with Stealth Context...")
            response = await page.goto("https://cloud.siliconflow.com/account/ak", timeout=30000)
            print(f"[+] Status: {response.status}")
            print(f"[+] Final URL: {page.url}")
            
            # Take a screenshot to inspect if WAF challenge is passed
            await page.screenshot(path="/home/agentuser/muse/stealth_result.png")
            print("[+] Stealth screenshot saved to /home/agentuser/muse/stealth_result.png")
            
        except Exception as e:
            print(f"[-] Stealth navigation error: {e}")
        finally:
            await browser.close()

def test_curl_cffi():
    print("[*] Testing TLS Fingerprint Spoofing via curl_cffi...")
    try:
        r = requests.get("https://cloud.siliconflow.com/account/ak", impersonate="chrome120", timeout=15)
        print(f"[+] curl_cffi Status: {r.status_code}")
        print(f"[+] Response length: {len(r.text)} bytes")
    except Exception as e:
        print(f"[-] curl_cffi error: {e}")

if __name__ == "__main__":
    test_curl_cffi()
    asyncio.run(stealth_playwright_test())
