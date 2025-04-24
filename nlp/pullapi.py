import http.client
import urllib.parse
import csv
import time
from datetime import datetime, timedelta
from dateutil.parser import parse

API_TOKEN = "AWJExEL2Iynpvl2zg5anHdC79MfYXEzSKPaNz6bb"
CSV_FILE = "oil_news_articles.csv"
CONN = http.client.HTTPSConnection('api.thenewsapi.com')

def get_news(published_after=None):
    params = {
        'api_token': API_TOKEN,
        'published_after': published_after,
        'categories': "general, science, business, tech, politics",
        'exclude_categories': "sports, health, entertainment, food, travel",
        'language': "en",
        'search_fields': "keywords",
        'search': "crude oil" or "Crude Oil" or "Crude oil",
        'sort': "published_at"
    }
    
    if published_after:
        params['published_after'] = published_after
    
    query = urllib.parse.urlencode(params)
    
    try:
        CONN.request('GET', f'/v1/news/all?{query}')
        res = CONN.getresponse()
        data = res.read()
        if res.status == 200:
            return data.decode('utf-8')
        else:
            print(f"API Error: {res.status} {res.reason}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def save_to_csv(json_data, filename):
    import json
    try:
        data = json.loads(json_data)
        if not data or 'data' not in data or not data['data']:
            return None
        
        fieldnames = ['uuid', 'title', 'description', 'url', 'published_at', 'source']
        last_published = None
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if csvfile.tell() == 0:
                writer.writeheader()
            
            for article in data['data']:
                try:
                    published_at = parse(article['published_at'])
                    row = {
                        'uuid': article.get('uuid', ''),
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': published_at.isoformat(),
                        'source': article.get('source', '')
                    }
                    writer.writerow(row)
                    
                    if last_published is None or published_at > last_published:
                        last_published = published_at
                
                except Exception as e:
                    print(f"Error processing article: {e}")
        
        return last_published
    
    except Exception as e:
        print(f"Error processing response: {e}")
        return None

def main():
    # Start from current time minus 1 day, or specific date:
    # last_published = datetime(2025, 3, 25)  # YYYY-MM-DD
    last_published = '2025-03-28T23:59:59'
    
    while True:
        print(f"\nFetching articles published after {last_published}")
        
        news_data = get_news(last_published)
        
        if news_data:
            new_last_published = save_to_csv(news_data, CSV_FILE)
            if new_last_published:
                last_published = new_last_published + timedelta(seconds=1)
                print(f"Found new articles. Last published at {last_published}")
            else:
                print("No new articles found in this batch.")
        else:
            print("Failed to fetch articles. Will retry...")
        
        time.sleep(5)  # Respect API rate limits

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    finally:
        CONN.close()