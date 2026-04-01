import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from utils.forensic_scraper import ForensicScraper

if __name__ == "__main__":
    scraper = ForensicScraper(download_dir="../backend/static/dataset")
    # You can customize search terms and max_videos here
    results = scraper.run_full_scraping(pbs_terms=None, max_videos_per_source=5)
    print(f"Scraping complete. {len(results)} recordings processed.")
    for r in results:
        print(r)











