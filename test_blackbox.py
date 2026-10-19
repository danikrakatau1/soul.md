import g4f
from g4f.client import Client

client = Client()
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        provider=g4f.Provider.Blackbox,
        messages=[{"role": "user", "content": "Halo, balas dengan 1 kata: Hadir"}]
    )
    print("BERHASIL:", response.choices[0].message.content)
except Exception as e:
    print("GAGAL:", e)
