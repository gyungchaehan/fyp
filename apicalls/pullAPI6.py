import csv
import json
import http.client, urllib.parse, time
from datetime import datetime, timedelta

def pull_news_data(api_token, categories, exclude_categories, published_after, published_before, language, last_article_id=None):
    conn = http.client.HTTPSConnection('api.thenewsapi.com')

    params = {
        'api_token': api_token,
        'categories': categories,
        'exclude_categories': exclude_categories,
        'published_after': published_after,
        'published_before': published_before,
        'language': language,
    }

    params_encoded = urllib.parse.urlencode(params)

    conn.request('GET', '/v1/news/all?{}'.format(params_encoded))
    res = conn.getresponse()
    data = res.read()

    json_data = json.loads(data.decode('utf-8'))
    return json_data.get('data', [])

def write_news_data_to_csv(news_data):
    fieldnames = ['uuid', 'title', 'description', 'keywords', 'snippet', 'url', 'image_url', 'language', 'published_at', 'source', 'categories', 'relevance_score']

    try:
        with open('news_data_2022_second.csv', 'r', newline='', encoding='utf-8') as file:
            existing_data = list(csv.DictReader(file))
    except FileNotFoundError:
        existing_data = []

    combined_data = existing_data + news_data

    with open('news_data_2022_second.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=',', extrasaction='ignore')

        # Write header only if the file was empty
        if not existing_data:
            writer.writeheader()

        for item in news_data:  # Write only new data
            writer.writerow(item)

last_article_id = None
last_time = '2022-01-20T09:32:26'
many = 0

while True:
    many += 1
    print(f"round {many}")
    news_data = pull_news_data('IqNnyA5M4U0tWyxuAKAftDsZg0lICFgiGwYru9eZ',
                               'general, science, business, tech, politics',
                               'sports, health, entertainment, food, travel',
                               '2022-01-15T23:59:59',
                               last_time,
                               'en',
                               last_article_id=last_article_id)

    if not news_data:
        print("No new articles found. Exiting.")
        break

    write_news_data_to_csv(news_data)
    print(f"Downloaded {len(news_data)} articles.")

    last_article_id = news_data[-1]['uuid']
    last_time = news_data[-1]['published_at'] 
    last_time = last_time[:-8]
    dt = datetime.fromisoformat(last_time)
    new_dt = dt - timedelta(seconds=1)
    last_time = new_dt.isoformat()
    print(last_time)

    time.sleep(2)  # Add a delay of 15 seconds before fetching the next batch