
import requests
import os

# URLs for About Page (Chef / Restaurant Context)
urls = [
    # Hero Background - Indian Spices/Texture
    ("about-hero.jpg", "https://picsum.photos/seed/indianhero/1920/1080"),
    # Chef Sudhi (Representational)
    ("chef-sudhi.jpg", "https://picsum.photos/seed/chefman/800/800"),
    # Vibrant Flavors / Street Food
    ("vibrant-food.jpg", "https://picsum.photos/seed/indianstreetfood/1024/768")
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

os.makedirs('static/images/about', exist_ok=True)

print("Downloading About Page Images...")
for filename, url in urls:
    try:
        print(f"Downloading {filename}...")
        r = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=15)
        if r.status_code == 200:
            with open(f'static/images/about/{filename}', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Success: {filename}")
        else:
            print(f"Failed {filename}: Status {r.status_code}")
    except Exception as e:
        print(f"Exception {filename}: {e}")

print("About Images Done.")
