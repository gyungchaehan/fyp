import requests, json, os, dotenv

dotenv.load_dotenv()

key = os.getenv("NEWS_API_KEY")

url = "https://api.thenewsapi.com/v1/news/all"
categories = "general, science, business, tech, politics"
language = "en"
published_after = "2021-01-01"
api_key = key

params = {
    "categories": categories,
    "language": language,
    "published_after": published_after,
    "api_token": api_key
}

output_dir = "output"

def get_api_response():
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "api-result.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        print("Error fetching articles:", response.text)