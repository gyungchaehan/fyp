#! pip install -r requirements.txt
import apireq, getarticle, llmresponse, sentiment

# Get the articles from the API
apireq.get_api_response()

# Extract the articles from the URLs
getarticle.get_articles()

# Generate summaries using the LLM model
llmresponse.get_response()

# Sentiment analysis on the generated summaries
sentiment.get_sentiment_score()

print("Process completed successfully!")