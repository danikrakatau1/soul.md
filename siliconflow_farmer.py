import asyncio
import os
from playwright.async_api import async_playwright

class SiliconFlowFarmer:
    def __init__(self):
        self.base_url = "https://cloud.siliconflow.com"
        self.output_file = "/home/agentuser/muse/siliconflow_keys.txt"

    async def run_farming_session(self):
        print(f"[*] Initializing SiliconFlow Automation Farm (Headless Mode)...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print(f"[*] Navigating to {self.base_url}/account/ak...")
                await page.goto(f"{self.base_url}/account/ak", timeout=30000)
                
                print(f"[*] Current Page Title: {await page.title()}")
                print(f"[*] Current URL: {page.url}")
                
                if "login" in page.url or "signin" in page.url:
                    print("[-] Redirected to login page. Automated login requires SMS OTP verification.")
                else:
                    print("[+] Successfully reached target page!")
                    
            except Exception as e:
                print(f"[-] Automation error: {e}")
            finally:
                await browser.close()

if __name__ == "__main__":
    farmer = SiliconFlowFarmer()
    asyncio.run(farmer.run_farming_session())
