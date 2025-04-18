import json
import http.client
import urllib.parse
from datetime import datetime, timedelta
import os  # TODO: implement relative directory


import json
import http.client
import urllib.parse
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional

DEFAULT_API_TOKEN = 'AWJExEL2Iynpvl2zg5anHdC79MfYXEzSKPaNz6bb'
DEFAULT_FILENAME = os.path.join("data", "news_data.jsonl")

def fetch_and_store_news(
    api_token: str = DEFAULT_API_TOKEN,
    output_file: str = DEFAULT_FILENAME,
    lookback_weeks: int = 3,
    rate_limit: int = 3
) -> None:
    """
    Main function to fetch and store news articles.
    
    Args:
        api_token: API token for the news service (defaults to built-in token)
        output_file: Path to output JSONL file (defaults to 'data/news_data.jsonl')
        lookback_weeks: Number of weeks to look back if no existing file found
        rate_limit: Max results per page
    """
    # Determine start date
    last_time = _get_last_article_time(output_file)
    if not last_time:
        last_time = (datetime.now() - timedelta(weeks=lookback_weeks)).strftime('%Y-%m-%d')
    
    all_news_data = []
    
    try:
        # Initial API call to get total count
        response_data = _api_call(api_token, last_time, page=1)
        meta_found = response_data.get('meta', {}).get('found', 0)
        print(f"Total number of articles found: {meta_found}")
        
        if meta_found == 0:
            print("No new articles found.")
            return
            
        total_pages = (meta_found + rate_limit - 1) // rate_limit

        # Fetch all pages
        for page in range(1, total_pages + 1):
            response_data = _api_call(api_token, last_time, page)
            news_data = response_data.get('data', [])
            all_news_data.extend(news_data)
            print(f"Downloaded articles from page {page}/{total_pages}")

        # Store results (newest first)
        _write_news_to_jsonl(reversed(all_news_data), output_file)
        print(f"Retrieved and stored {len(all_news_data)} articles to {output_file}")

    except Exception as e:
        print(f"Encountered error during data collection: {e}")

def _api_call(api_token: str, published_after: str, page: int = 1) -> Dict:
    """Internal function to make API calls"""
    conn = http.client.HTTPSConnection('api.thenewsapi.com')
    params = {
        'api_token': api_token,
        'published_after': published_after,
        'page': page,
        'categories': "general, science, business, tech, politics",
        'exclude_categories': "sports, health, entertainment, food, travel",
        'language': "en",
        'search_fields': "keywords",
        'search': "crude oil",
        'sort': "published_at"
    }
    params_encoded = urllib.parse.urlencode(params)
    conn.request('GET', f'/v1/news/all?{params_encoded}')
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    conn.close()
    return data

def _write_news_to_jsonl(news_data: List[Dict], filename: str) -> None:
    """Internal function to write data to JSONL file"""
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    with open(filename, 'a', encoding='utf-8') as file:
        for item in news_data:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')

def _get_last_article_time(filename: str) -> Optional[str]:
    """Internal function to get last article time"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                pass  # Read to last line
            if line:  # type: ignore
                return json.loads(line)['published_at']
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None

if __name__ == '__main__':
    fetch_and_store_news()

# def api_call(api_token, published_after, page=1):
#     conn = http.client.HTTPSConnection('api.thenewsapi.com')

#     params = {
#         'api_token': api_token,
#         'published_after': published_after,
#         'page': page,
#         'categories': "general, science, business, tech, politics",
#         'exclude_categories': "sports, health, entertainment, food, travel",
#         'language': "en",
#         'search_fields': "keywords",
#         'search': "crude oil",
#         'sort': "published_at"
#     }
#     params_encoded = urllib.parse.urlencode(params)

#     conn.request('GET', '/v1/news/all?{}'.format(params_encoded))
#     res = conn.getresponse()
#     data = res.read()

#     json_data = json.loads(data.decode('utf-8'))
#     return json_data


# def write_news_to_jsonl(news_data, filename='news_data.jsonl'):
#     with open(filename, 'a', encoding='utf-8') as file:
#         for item in news_data:
#             json.dump(item, file, ensure_ascii=False)
#             file.write('\n')


# def get_last_article_time(filename='news_data.jsonl'):
#     try:
#         with open(filename, 'r', encoding='utf-8') as file:
#             last_line = None
#             for line in file:
#                 last_line = line
#             if last_line:
#                 last_article = json.loads(last_line)
#                 return last_article['published_at']
#             else:
#                 return None
#     except FileNotFoundError:
#         return None


# if __name__ == '__main__':
#     filename = os.path.join("data", "news_data.jsonl")
    
#     today = datetime.now().strftime('%Y-%m-%d')
#     three_weeks_ago = (datetime.now() - timedelta(weeks=3)).strftime('%Y-%m-%d')
#     last_time = get_last_article_time(filename) or three_weeks_ago

#     api_token = 'AWJExEL2Iynpvl2zg5anHdC79MfYXEzSKPaNz6bb'
#     rate_limit = 3
#     all_news_data = []

#     try:
#         response_data = api_call(api_token, last_time, page=1)
#         meta_found = response_data.get('meta', {}).get('found', 0)
#         print(f"Total number of articles found: {meta_found}")
#         total_pages = (meta_found + rate_limit - 1) // rate_limit

#         for page in range(1, total_pages + 1):
#             response_data = api_call(api_token, last_time, page)
#             news_data = response_data.get('data', [])
#             all_news_data.extend(news_data)
#             print(f"Downloaded articles from page {page}")

#     except Exception as e:
#         print(f"Encountered error {e} during data collection")

#     all_news_data.reverse()
#     write_news_to_jsonl(all_news_data, filename)
#     print("Retrieved and stored all articles.")
