from pytube import Channel
import requests
from bs4 import BeautifulSoup

def scrape_pbs_youtube(channel_url="https://www.youtube.com/c/PBSNewsHour/videos", limit=10):
    c = Channel(channel_url)
    video_data = []

    for url in c.video_urls[:limit]:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string
            video_data.append({
                "title": title,
                "url": url
                # You can add more parsing logic for date/speaker if available
            })
        except Exception as e:
            print(f"[ERROR] scraping {url}: {e}")

    return video_data
