import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import os

def process_movies():
    input_file = 'input.json'
    output_file = 'out.json'

    if not os.path.exists(input_file):
        print("Error: input.json not found!")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    scraper = cloudscraper.create_scraper()
    extracted_items = []

    for movie in input_data.get('movies', []):
        title = movie.get('title')
        watch_url = movie.get('links', {}).get('watch')
        print(f"Fetching: {title}")

        try:
            resp = scraper.get(watch_url, timeout=20)
            soup = BeautifulSoup(resp.text, 'html.parser')
            iframe = soup.find('iframe')
            
            if iframe and 'src' in iframe.attrs:
                iframe_src = iframe['src']
                iframe_res = scraper.get(iframe_src, headers={'Referer': watch_url}, timeout=20)
                
                m3u8_match = re.search(r'file\s*:\s*"(https?://[^"]+\.m3u8[^"]*)"', iframe_res.text)
                
                if m3u8_match:
                    extracted_items.append({
                        "id": title,
                        "title": title,
                        "poster": movie.get('thumbnail'),
                        "stream_url": m3u8_match.group(1),
                        "headers": {"Referer": "https://speedostream1.com/"}
                    })
        except Exception as e:
            print(f"Error: {e}")

    if extracted_items:
        final_output = {
            "hero": [extracted_items[0]],
            "categories": [{"name": "Latest Movies", "items": extracted_items}]
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        print("Update Successful!")

if __name__ == "__main__":
    process_movies()
