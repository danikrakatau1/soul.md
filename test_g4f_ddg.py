import asyncio
from g4f.client import Client

client = Client()

print("[*] Menguji g4f dengan provider khusus (DuckDuckGo)...")
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        provider="DuckDuckGo", # Pakai provider DuckDuckGo yang lebih kebal
        messages=[{"role": "user", "content": "Halo! Jawab singkat: siapa kamu?"}]
    )
    print("\n[HASIL AI]:")
    print(response.choices[0].message.content)
except Exception as e:
    print("[-] Gagal dengan DuckDuckGo:", e)
