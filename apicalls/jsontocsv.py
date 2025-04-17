import json
import csv

def convert_json_to_csv(json_file, csv_file):
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Specify field names for the CSV
    fieldnames = ['uuid', 'title', 'description', 'keywords', 'snippet', 'url', 'image_url', 'language', 'published_at', 'source', 'categories', 'relevance_score']

    # Open a CSV file for writing with UTF-8 encoding
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', extrasaction='ignore')

        # Write the headers
        writer.writeheader()

        # Write the data rows
        for item in data:
            writer.writerow(item)

# Example usage
json_file = 'news_data.json'  # Update with the path to your JSON file
csv_file = 'news_data_2021.csv'    # Specify the name of the output CSV file
convert_json_to_csv(json_file, csv_file)