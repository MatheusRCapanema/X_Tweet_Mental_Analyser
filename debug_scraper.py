
from ntscraper import Nitter
import json

def test_scrape():
    scraper = Nitter(log_level=1, skip_instance_check=False) 
    # Try a few instances if default fails
    try:
        print("Attempting to scrape _punk_melody...")
        result = scraper.get_tweets("_punk_melody", mode='user', number=5)
        print(f"Keys in result: {result.keys()}")
        if 'tweets' in result:
             print(f"Found {len(result['tweets'])} tweets.")
             if len(result['tweets']) > 0:
                 print(f"Sample: {result['tweets'][0]['text']}")
        else:
             print("No 'tweets' key in result.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape()
