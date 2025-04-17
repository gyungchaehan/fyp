import csv
from collections import deque

def get_published_at_last_row(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Use deque to efficiently get the last row
        last_row = deque(reader, maxlen=1)

        # Extract the published_at data from the last row
        last_published_at = last_row[0]['published_at'] if last_row else None

    return last_published_at

# Example usage
csv_file = 'news_data_2022.csv'  # Update with the path to your CSV file
last_published_at = get_published_at_last_row(csv_file)

print(f"The published_at data from the last row in the CSV file is: {last_published_at}")