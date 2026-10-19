from g4f.client import Client

client = Client()
print("[*] Menghubungi AI gratis via g4f di VPS...")
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Sapa aku dengan gaya operator hacker senior dan sebut namaku bosku."}]
    )
    print("\n[HASIL AI]:")
    print(response.choices[0].message.content)
except Exception as e:
    print("[-] Error:", e)
