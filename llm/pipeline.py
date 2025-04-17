import json
import requests
import ollama
import pydantic
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import logging

def setup_logger(log_file):
    """Sets up a logger to write to a file and the console."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_llm_analysis(article_text, ollama_api_url, logger):
    """
    Sends the article text to the Ollama API for analysis and returns the LLM's
    response.
    """
    try:
        prompt = f"""
        Analyze the following news article and assess its potential impact on oil price futures. Provide your response in JSON format, with the following keys:

        *   "Relevancy": An integer from 1 to 5 indicating how direct the impact on oil price the article content has (1: Not at all direct, 5: Very direct)
        *   "Likeliness": An integer from 1 to 5 on the likeliness of the change in price following the events discussed (1: Minimal change, 5: Significant change)
        *   "Price": An integer from 1 to 5 indicating the price direction (1: Definite decrease, 5: Definite increase, 3: Neutral)
        *   "Confidence": An integer from 1 to 5 indicating the confidence in the above scores (1: Not at all confident, 5: Very confident)
        *   "Time Horizon": A string indicating the time horizon (e.g., "Next Week", "Next Month", "Long-Term")
        *   "Key Drivers": A list of strings identifying the key drivers of your analysis
        *   "Uncertainty Factors": A list of strings identifying potential uncertainty factors
        *   "Justification": A string providing a detailed justification of your analysis

        Here's an example of the expected JSON format:

        {{
            "Relevancy": 4,
            "Likeliness": 3,
            "Sentiment": 2,
            "Confidence": 5,
            "Time Horizon": "Next Month",
            "Key Drivers": ["Supply disruptions"],
            "Uncertainty Factors": ["Geopolitical Stability"],
            "Justification": "The disruption in oil supply is imminent given the nature of this report, considering there has been increased amount of warfare in the middle east. This will affect the prices negatively for the duration of 1 month, give or take."
        }}

        Now, analyze the following news article:

        {article_text}
        """

        data = {
            "prompt": prompt.format(article_text=article_text),
            "stream": False,
            "model": "deepseek-r1:8b",
        }

        response = requests.post(ollama_api_url, json=data, stream=False)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_response = response.json()
        return json_response["response"]

    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing with Ollama API: {e}")
        return None


def extract_justification(llm_output):
    """Extracts the justification paragraph from the LLM output."""
    match = re.search(r"Justification:\s*(.*)", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None  # Or raise an exception if justification is required


def analyze_sentiment(text):
    """Analyzes the sentiment of the given text using VADER."""
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text)
    return vs["compound"]


def process_jsonl(jsonl_file, ollama_api_url, logger):
    """
    Reads a JSONL file, analyzes article text using Ollama and VADER, and adds
    the results to the JSONL file.
    """

    with open(jsonl_file, "r+") as f:  # Open for reading and writing
        lines = f.readlines()
        f.seek(0)  # Rewind to the beginning of the file
        f.truncate()  # Clear the file

        for line in lines:
            try:
                data = json.loads(line.strip())  # Remove any leading/trailing whitespace from the line
                article_text = data.get("article_text")

                if not article_text:
                    logger.info(
                        f"Skipping entry due to missing 'article_text': {data.get('uuid')}"
                    )
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")  # Keep original data
                    continue

                # Get LLM Analysis
                llm_output = get_llm_analysis(article_text, ollama_api_url, logger)

                if llm_output:
                    # Extract Justification
                    justification_text = extract_justification(llm_output)

                    if justification_text:
                        # Analyze sentiment of LLM output
                        vader_score = analyze_sentiment(justification_text)

                        # Add LLM output and VADER score to JSON
                        data["llm_output"] = llm_output
                        data["vader_score"] = vader_score

                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        logger.info(f"Added LLM output and VADER score to JSON.")
                    else:
                        logger.warning(f"Could not extract justification from LLM output.")
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")  # Keep original data
                else:
                    logger.error(f"Failed to retrieve LLM output for article.")
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")  # Keep original data

            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                f.write(line)  # Preserve the original invalid line
            except Exception as e:
                logger.error(f"Error processing entry: {e}")


# Example Usage
jsonl_file = "news_data_oil.jsonl"  # Replace with your JSONL file
ollama_api_url = "http://localhost:11434/api/generate"  # Replace with your Ollama API URL
log_file = "pipeline.log"  # Specify the log file name

# Set up logging
logger = setup_logger(log_file)

# Log the start of the process
logger.info("Starting the processing...")

process_jsonl(jsonl_file, ollama_api_url, logger)

# Log the end of the process
logger.info("Finished processing.")
