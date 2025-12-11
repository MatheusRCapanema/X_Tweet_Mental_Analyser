
from twikit import Client
import asyncio
import pandas as pd
import os
import json

async def scrape_profile_with_login(target_username, auth_info=None, cookies_path=None):
    """
    Scrapes tweets using Twikit (Authenticated).
    auth_info: dict containing 'username', 'email', 'password' (Optional if cookies provided)
    cookies_path: str (Path to cookies.json)
    """
    client = Client('en-US')
    
    try:
        # Prioritize Cookies if provided
        if cookies_path and os.path.exists(cookies_path):
            print(f"Loading cookies from {cookies_path}")
            
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            cookies_dict = {}
            if isinstance(cookies_data, list):
                print("Converting EditThisCookie (List) to internal format...")
                for c in cookies_data:
                    cookies_dict[c['name']] = c['value']
            elif isinstance(cookies_data, dict):
                cookies_dict = cookies_data
            
            # Set cookies directly (bypassing load_cookies file expectation)
            client.set_cookies(cookies_dict)
            print("Cookies set successfully.")
                
        elif auth_info:
            print("Attempting password login...")
            await client.login(
                auth_info_1=auth_info['username'],
                auth_info_2=auth_info['email'],
                password=auth_info['password']
            )
        else:
            raise ValueError("No credentials or cookies provided")
        
        # Get User
        print(f"Fetching user: {target_username}...")
        user = await client.get_user_by_screen_name(target_username)
        
        # Get Tweets
        target_count = 200
        print(f"Fetching tweets (Target: {target_count})...")
        tweets = await user.get_tweets('Tweets', count=20)
        
        all_tweets = []
        if tweets:
            all_tweets.extend(tweets)
            
            # Pagination Loop
            while len(all_tweets) < target_count:
                print(f"Accumulated {len(all_tweets)} tweets. Fetching more...")
                try:
                    more_tweets = await tweets.next()
                    if not more_tweets:
                        print("No more tweets available.")
                        break
                    all_tweets.extend(more_tweets)
                    
                    # Safety break to avoid infinite loops if something gets stuck
                    if len(more_tweets) == 0:
                        break
                        
                except Exception as e:
                    print(f"Pagination error (stopping fetch): {e}")
                    break
        
        # Trim to target_count
        all_tweets = all_tweets[:target_count]
        print(f"Total tweets fetched: {len(all_tweets)}")

        results = []
        for tweet in all_tweets:
            results.append({
                'text': tweet.text,
                'date': tweet.created_at,
                'id': tweet.id
            })
                
        return pd.DataFrame(results)

    except Exception as e:
        print(f"Twikit Error: {e}")
        return None

# Helper wrapper for Streamlit (since it's sync by default often)
def run_scrape(target_username, auth_info=None, cookies_path=None):
    return asyncio.run(scrape_profile_with_login(target_username, auth_info, cookies_path))
