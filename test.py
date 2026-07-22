import yt_dlp

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("✅ SUCCESS!")
        print(f"Title: {info.get('title', 'Unknown')}")
        print(f"Duration: {info.get('duration', 0)} seconds")
        print(f"Available formats: {len(info.get('formats', []))}")
except Exception as e:
    print(f"❌ ERROR: {e}")