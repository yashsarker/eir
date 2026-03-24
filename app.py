import requests
from bs4 import BeautifulSoup
import re
import json
import os
import glob

cookies = {
    'cf_clearance': '.Cwg24HrFQ4cMeb6e_2oVGfFg1kkcDjnhJTQCprhojI-1774293909-1.2.1.1-MpKrP7WrQBLzOaLkp36lRzIhpyq6nL5d4O4pFZadtGdxAXq_I27WS2rEJv4TseMJwvFwt7FjuQQENNa_A3bMXUz_aSwEkeyTfSXaCeSMP0dDQFliTy1e2EbsOTpHZ3vgkE4tGOlbf.I2NzweqRXKxDld7i1jl4NEVBfGxelQRCGAzN_I59kn3FT8yHLIdj0Vow2pM28UB_3XWxVHkVQ_JNJSyLrlXgi5GXYX7seoqPk',
    '_ga': 'GA1.1.1139795519.1774293911',
    'domain-alert': '1',
    'fpestid': 'iOECTy_JebGLHfNlnFFQLV5JsaqiaLXnlOzx2gXTk-YUX0BKGLe0ZJvN0c00m2BCqeuoJg',
    '_ga_7BWGJ9MXSS': 'GS2.1.s1774335963$o2$g0$t1774335963$j60$l0$h0'
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "if-modified-since": "Tue, 24 Mar 2026 05:00:54 GMT",
    "priority": "u=0, i",
    "cookie": "cf_clearance=.Cwg24HrFQ4cMeb6e_2oVGfFg1kkcDjnhJTQCprhojI-1774293909-1.2.1.1-MpKrP7WrQBLzOaLkp36lRzIhpyq6nL5d4O4pFZadtGdxAXq_I27WS2rEJv4TseMJwvFwt7FjuQQENNa_A3bMXUz_aSwEkeyTfSXaCeSMP0dDQFliTy1e2EbsOTpHZ3vgkE4tGOlbf.I2NzweqRXKxDld7i1jl4NEVBfGxelQRCGAzN_I59kn3FT8yHLIdj0Vow2pM28UB_3XWxVHkVQ_JNJSyLrlXgi5GXYX7seoqPk; _ga=GA1.1.1139795519.1774293911; domain-alert=1; fpestid=iOECTy_JebGLHfNlnFFQLV5JsaqiaLXnlOzx2gXTk-YUX0BKGLe0ZJvN0c00m2BCqeuoJg; _ga_7BWGJ9MXSS=GS2.1.s1774335963$o2$g0$t1774335963$j60$l0$h0",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"146.0.7680.153"',
    "sec-ch-ua-full-version-list": '"Chromium";v="146.0.7680.153", "Not-A.Brand";v="24.0.0.0", "Google Chrome";v="146.0.7680.153"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"19.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
}

CACHE_FILE = 'iframe_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)

def process_movies():
    input_files = glob.glob('input*.json')

    if not input_files:
        print("Error: No input files found (e.g., input.json, input1.json)!")
        return

    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)
    
    iframe_cache = load_cache()

    for file_path in input_files:
        output_file = file_path.replace('input', 'output')
        
        print(f"\n--- Processing: {file_path} to {output_file} ---")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        extracted_items = []

        for movie in input_data.get('movies', []):
            title = movie.get('title')
            watch_url = movie.get('links', {}).get('watch')
            print(f"Fetching: {title}")

            iframe_src = None

            try:
                resp = session.get(watch_url, timeout=20)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    iframe = soup.find('iframe')
                    
                    if iframe and 'src' in iframe.attrs:
                        iframe_src = iframe['src']
                        iframe_cache[watch_url] = iframe_src
                        save_cache(iframe_cache)
            except Exception as e:
                print(f"Warning: watch_url failed for {title} - {e}")

            if not iframe_src:
                if watch_url in iframe_cache:
                    print(f"-> Using CACHED iframe for {title}...")
                    iframe_src = iframe_cache[watch_url]
                else:
                    print(f"-> Failed! No live response and no cache found for {title}.")
                    continue 

            if iframe_src:
                try:
                    iframe_headers = headers.copy()
                    iframe_headers['Referer'] = watch_url
                    
                    iframe_res = session.get(iframe_src, headers=iframe_headers, timeout=20)
                    m3u8_match = re.search(r'file\s*:\s*"(https?://[^"]+\.m3u8[^"]*)"', iframe_res.text)
                    
                    if m3u8_match:
                        extracted_items.append({
                            "id": title,
                            "title": title,
                            "poster": movie.get('thumbnail'),
                            "stream_url": m3u8_match.group(1),
                            "headers": {"Referer": "https://speedostream1.com/"}
                        })
                        print(f"-> Success! Stream URL fetched.")
                    else:
                        print(f"-> No m3u8 found in iframe for {title}.")
                except Exception as e:
                    print(f"Error fetching iframe content for {title}: {e}")

        if extracted_items:
            final_output = {
                "hero": [extracted_items[0]],
                "categories": [
                    {
                        "name": f"Latest from {file_path}", 
                        "items": extracted_items 
                    }
                ]
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved to {output_file}")
        else:
            print(f"No items extracted for {file_path}")

if __name__ == "__main__":
    process_movies()
