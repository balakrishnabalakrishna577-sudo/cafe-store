
import requests
import os

# Picsum is designed for this
urls = [
    ("gallery-1.jpg", "https://picsum.photos/seed/indianfood1/800/600"),
    ("gallery-2.jpg", "https://picsum.photos/seed/curry/800/600"),
    ("gallery-3.jpg", "https://picsum.photos/seed/spices/800/600"),
    ("gallery-4.jpg", "https://picsum.photos/seed/biryani/800/600"),
    ("gallery-5.jpg", "https://picsum.photos/seed/sweets/800/600")
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

os.makedirs('static/images/gallery', exist_ok=True)

print("Downloading from Picsum...")
for filename, url in urls:
    try:
        print(f"Downloading {filename}...")
        r = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=15)
        if r.status_code == 200:
            with open(f'static/images/gallery/{filename}', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Success: {filename}")
        else:
            print(f"Failed {filename}: Status {r.status_code}")
    except Exception as e:
        print(f"Exception {filename}: {e}")

print("Done.")
