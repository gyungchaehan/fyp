from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    #note: depending on how you installed (e.g., using source code download versus pip install), you may need to import like this:
    #from vaderSentiment import SentimentIntensityAnalyzer
import json


# Load the extracted message from the JSON file
with open('output/summary.json', 'r', encoding='utf-8') as file:
    summaries = json.load(file)

analyzer = SentimentIntensityAnalyzer()
score = []

for summary in summaries:
    vs = analyzer.polarity_scores(summary['output'])
    result = {
      "title": summary['title'],
      "score": vs
  }
    score.append(result);

with open(f'output/sentimentScore.json', 'w') as output_file:
    json.dump(score, output_file, indent=4)