import json
import os
from newspaper import Article, Config

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"
config = Config()
config.browser_user_agent = user_agent

def get_articles():
    with open("output/api-result.json", "r", encoding="utf-8") as file:
        api_data = json.load(file)

    extracted_articles = []

    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for entry in api_data["data"]:
        url = entry["url"]
        try:
            article = Article(url)
            article.download()
            article.parse()

            # You can optionally perform NLP tasks like article.nlp() here
            title = article.title
            content = article.text

            extracted_articles.append({
                "url": url,
                "title": title,
                "content": content
            })
        except Exception as e:
            print(f"Error fetching or parsing the article at {url}: {e}")

    with open(os.path.join(output_dir, "extracted_articles.json"),
            "w", encoding="utf-8") as out_file:
        json.dump(extracted_articles, out_file, indent=2, ensure_ascii=False)
