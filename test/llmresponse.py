import json
import textwrap
import re
from ollama import chat
from ollama import ChatResponse

def get_response():
  summary = []

  with open('output/extracted_articles.json', 'r', encoding='utf-8') as file:
      articles = json.load(file)

  for article in articles:
    title = article["title"]
    content = article["content"]

    response: ChatResponse = chat(model='deepseek-r1', messages=[
      {
        'role': 'user',
        'content': 'You are given a series of news articles. For each article, please analyze the content and predict its impact on oil prices. Please elaborate on the scale of the impact.',
      },
    ])

    output = response['message']['content']
    
    reasoning = re.findall(r"<think>(.*?)</think>", output, re.DOTALL)
    if reasoning:
      reasoning = reasoning[0].strip()
    
    response_stripped = re.sub(r"<think>.*?</think>\n*", "", output, flags=re.DOTALL).strip()

    result = {
        "title": title,
        "reasoning": reasoning,
        "response": response_stripped
    }
    summary.append(result)
    title_shortened = textwrap.shorten(title, width=20, placeholder="...")
    print(f"Article \"{title_shortened}\" completed successfully!")

  with open(f'output/summary.json', 'w') as output_file:
      json.dump(summary, output_file, indent=4)