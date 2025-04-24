import json
import http.client
import urllib.parse
from datetime import datetime, timedelta
import os


def api_call(api_token, published_after, page=1):
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

    conn.request('GET', '/v1/news/all?{}'.format(params_encoded))
    res = conn.getresponse()
    data = res.read()

    json_data = json.loads(data.decode('utf-8'))
    return json_data


def write_news_to_jsonl(news_data, filename='news_data.jsonl'):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in news_data:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')


def get_last_article_time(filename='news_data.jsonl'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            last_line = None
            for line in file:
                last_line = line
            if last_line:
                last_article = json.loads(last_line)
                return last_article['published_at']
                print(last_article['published_at'])
            else:
                return None
    except FileNotFoundError:
        return None


def start():
    filename = os.path.join("data", "news_data.jsonl")

    three_weeks_ago = (datetime.now() - timedelta(weeks=3)).strftime('%Y-%m-%d')
    last_time = get_last_article_time(filename) or three_weeks_ago

    rate_limit = 3
    all_news_data = []

    try:
        response_data = api_call(api_token, last_time, page=1)
        meta_found = response_data.get('meta', {}).get('found', 0)
        print(f"Total number of articles found: {meta_found}")
        total_pages = (meta_found + rate_limit - 1) // rate_limit

        for page in range(1, total_pages + 1):
            response_data = api_call(api_token, last_time, page)
            news_data = response_data.get('data', [])
            all_news_data.extend(news_data)
            print(f"Downloaded articles from page {page}")
            # time.sleep(0.1)

    except Exception as e:
        print(f"Encountered error {e} during data collection")
        return []

    all_news_data.reverse()
    write_news_to_jsonl(all_news_data, filename)
    print("Retrieved and stored all articles.")
