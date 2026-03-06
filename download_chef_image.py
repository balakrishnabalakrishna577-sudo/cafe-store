
import requests
import os

# Using Pixabay with User-Agent header for a chef image
url = "https://cdn.pixabay.com/photo/2015/08/25/03/50/background-906135_1280.jpg"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

os.makedirs('static/images/about', exist_ok=True)

try:
    print(f"Downloading chef-portrait.jpg...")
    r = requests.get(url, headers=headers, stream=True, timeout=15)
    if r.status_code == 200:
        with open('static/images/about/chef-portrait.jpg', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Success: chef-portrait.jpg")
    else:
        print(f"Failed: Status {r.status_code}")
except Exception as e:
    print(f"Exception: {e}")
