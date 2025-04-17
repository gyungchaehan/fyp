import json

def count_successful_articles(jsonl_file):
    """
    Counts the number of entries in a JSONL file that have the 'article_text' field.
    """
    success_count = 0
    total_count = 0
    try:
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                total_count += 1
                try:
                    data = json.loads(line.strip())
                    if "article_text" in data:
                        success_count += 1
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error at line {total_count}: {e}")
                    # Optionally, you might want to log the malformed line
    except FileNotFoundError:
        print(f"Error: File not found: {jsonl_file}")
        return None  # Or raise the exception
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    return success_count, total_count


# Example Usage
jsonl_file = "news_data_oil.jsonl"  # Replace with the path to your JSONL file

result = count_successful_articles(jsonl_file)

if result is not None:
    success_count, total_count = result
    print(f"Total entries: {total_count}")
    print(f"Number of articles successfully processed: {success_count}")
    print(f"Number of articles NOT successfully processed: {total_count - success_count}")
else:
    print("Counting failed. Check the error messages above.")
