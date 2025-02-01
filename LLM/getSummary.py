from openai import OpenAI
import json

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="insert here",
)

summary = []

# Load the extracted message from the JSON file
with open('output/extracted_articles.json', 'r', encoding='utf-8') as file:
    articles = json.load(file)

for article in articles:
  title = article["title"]
  content = article["content"]

  # Call the OpenAI API to summarize the text and predict its impact on oil prices
  completion = client.chat.completions.create(
    extra_headers={
      "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    model="meta-llama/llama-3.2-3b-instruct:free",
    messages=[
      {
        "role": "user",
        "content": f"title = {title}, content = {content}. Explain on whether the news would impact oil prices in a positive, negative, or neutral way. Also elaborate on the scale of the impact"
      }
    ]
  )

 
  result = {
      "title": title,
      "output": completion.choices[0].message.content
  }

  summary.append(result);

with open(f'output/summary.json', 'w') as output_file:
    json.dump(summary, output_file, indent=4)
