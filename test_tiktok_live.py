from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, JoinEvent

# Inisialisasi client dengan target username TikTok Live
client: TikTokLiveClient = TikTokLiveClient(unique_id="@tiktok")

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"[+] Berhasil terhubung ke Live Room! Room ID: {client.room_id}")

@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    print(f"[+] Penonton bergabung: {event.user.nickname}")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"[💬] {event.user.nickname}: {event.comment}")

if __name__ == '__main__':
    print("[*] Menjalankan test koneksi TikTok Live WebCast...")
    try:
        client.run()
    except Exception as e:
        print(f"[-] Error: {e}")
