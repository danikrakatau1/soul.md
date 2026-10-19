import json
from curl_cffi import requests

class FullStealthFarmer:
    def __init__(self):
        self.base_url = "https://api.siliconflow.cn"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://cloud.siliconflow.com",
            "Referer": "https://cloud.siliconflow.com/"
        }

    def test_connection(self):
        print("[*] Testing connection to SiliconFlow backend with TLS Spoofing...")
        try:
            r = self.session.get(
                f"{self.base_url}/v1/models",
                headers=self.headers,
                impersonate="chrome120",
                timeout=15
            )
            print(f"[+] Status Code: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"[+] Successfully fetched models! Count: {len(data.get('data', []))}")
            else:
                print(f"[-] Response: {r.text[:200]}")
        except Exception as e:
            print(f"[-] Connection error: {e}")

    def request_otp(self, email_or_phone):
        print(f"[*] Requesting OTP / Registration trigger for: {email_or_phone}")
        payload = {"username": email_or_phone}
        try:
            r = self.session.post(
                f"{self.base_url}/v1/users/send-code",
                json=payload,
                headers=self.headers,
                impersonate="chrome120",
                timeout=15
            )
            print(f"[+] Status Code: {r.status_code}")
            print(f"[+] Response: {r.text}")
        except Exception as e:
            print(f"[-] Request OTP error: {e}")

if __name__ == "__main__":
    farmer = FullStealthFarmer()
    farmer.test_connection()
    farmer.request_otp("test_operator_99@example.com")
