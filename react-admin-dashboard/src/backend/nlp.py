import json
from ollama import generate
import pydantic
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class Response(pydantic.BaseModel):
    relevancy: int
    likeliness: int
    price: int
    confidence: int
    time_horizon: str
    key_drivers: list[str]
    uncertainty_factors: list[str]
    justification: str


def get_llm_analysis(article_text, ollama_api_url):
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

                Now, analyze the following news article:

                {article_text}
                """

        response = generate(
            model="deepseek-r1:8b",
            prompt=prompt.format(article_text=article_text),
            stream=False,
            format=Response.model_json_schema(),
        )

        output = Response.model_validate_json(response.response)
        return output.dict()

    except Exception as e:
        print(f"Error with Ollama: {e}")
        return None


def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scoers(text)
    return vs["compound"]


def process_jsonl(jsonl_file, ollama_api_url):
    with open(jsonl_file, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()

        for line in lines:
            try:
                data = json.loads(line.strip())
                article_text = data.get("article_text")

                if not article_text:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    continue

                llm_output = get_llm_analysis(article_text, ollama_api_url)

                if llm_output:
                    justification = llm_output.get("justification")

                    if justification:
                        vader_score = analyze_sentiment(justification)

                        data["llm_output"] = llm_output
                        data["vader_score"] = vader_score

                f.write(json.dumps(data, ensure_ascii=False) + "\n")

            except Exception as e:
                print(f"VADER produced error: {e}")


jsonl_file = "news_data.jsonl"
ollama_api_url = "http://localhost:11434/api/generate"
process_jsonl(jsonl_file, ollama_api_url)
