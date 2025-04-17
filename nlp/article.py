# 42m 48s

import json
import newspaper
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_article_text(url):
    """
    Fetches and extracts the text content from a given URL using newspaper3k.
    """
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except newspaper.ArticleException as e:
        print(f"Newspaper3k failed to download or parse {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None


def process_jsonl(jsonl_file):
    """
    Reads a JSONL file, fetches article text from URLs, adds the text to each
    JSON object, and overwrites the line in the original JSONL file.
    """

    with open(jsonl_file, "r+") as f:  # Open for reading and writing
        lines = f.readlines()
        f.seek(0)  # Rewind to the beginning of the file
        f.truncate() # Clear the file

        for line in lines:
            try:
                data = json.loads(line.strip()) # Remove any leading/trailing whitespace from the line
                article_url = data.get("url")

                if not article_url:
                    print(f"Skipping entry due to missing 'url': {data.get('uuid')}")
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")  # Keep original data
                    continue

                if not is_valid_url(article_url):
                    print(f"Skipping invalid URL: {article_url}")
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")  # Keep original data
                    continue

                article_text = get_article_text(article_url)

                if article_text:
                    data["article_text"] = article_text  # Add article text to JSON
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    print(f"Added article text from {article_url} to JSON.")
                else:
                    print(f"Failed to retrieve article from {article_url}")
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")  # Keep original data

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                f.write(line)  # Preserve the original invalid line
            except Exception as e:
                print(f"Error processing entry: {e}")
                # Consider logging the error and the original line


# Example Usage
jsonl_file = "news_data_oil.jsonl"  # Replace with your JSONL file

process_jsonl(jsonl_file)
