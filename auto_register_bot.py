import asyncio
import random
import string
import requests
from playwright.async_api import async_playwright

class MultiPlatformAutoRegister:
    def __init__(self):
        self.mail_api = "https://box.celana-ar-store.my.id"
        self.email = None
        self.password = "P@ssw0rd123!Secure"
        self.token = None

    def generate_temp_mail(self):
        try:
            r = requests.get(f"{self.mail_api}/domains")
            domain = r.json()['hydra:member'][0]['domain']
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            self.email = f"{username}@{domain}"
            
            payload = {"address": self.email, "password": self.password}
            res = requests.post(f"{self.mail_api}/accounts", json=payload)
            if res.status_code == 201:
                print(f"[+] Temp Mail Generated: {self.email}")
                token_res = requests.post(f"{self.mail_api}/token", json=payload)
                if token_res.status_code == 200:
                    self.token = token_res.json().get("token")
                return True
        except Exception as e:
            print(f"[-] Temp Mail Error: {e}")
        return False

    def check_inbox(self):
        if not self.token:
            return []
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(f"{self.mail_api}/messages", headers=headers)
        if r.status_code == 200:
            return r.json().get("hydra:member", [])
        return []

    async def register_groq(self, page):
        print("[*] Starting Groq Cloud Registration...")
        await page.goto("https://console.groq.com/login")
        print("[*] Groq automation stub ready.")

    async def register_siliconflow(self, page):
        print("[*] Starting SiliconFlow Registration...")
        await page.goto("https://cloud.siliconflow.cn/login")
        print("[*] SiliconFlow requires SMS OTP (requires SMS API integration).")

    async def register_openrouter(self, page):
        print("[*] Starting OpenRouter Registration...")
        await page.goto("https://openrouter.ai/sign-in")
        print("[*] OpenRouter automation stub ready.")

    async def register_google_aistudio(self, page):
        print("[*] Starting Google AI Studio Registration...")
        await page.goto("https://aistudio.google.com/")
        print("[*] Google AI Studio requires Google Account OAuth.")

    async def run(self, platform_name):
        if not self.generate_temp_mail():
            return
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            if platform_name == "groq":
                await self.register_groq(page)
            elif platform_name == "siliconflow":
                await self.register_siliconflow(page)
            elif platform_name == "openrouter":
                await self.register_openrouter(page)
            elif platform_name == "google":
                await self.register_google_aistudio(page)

            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    bot = MultiPlatformAutoRegister()
    asyncio.run(bot.run("groq"))
