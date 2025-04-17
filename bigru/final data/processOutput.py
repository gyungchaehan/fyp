import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def jsonl_to_csv(input_jsonl_path, output_csv_path):
    with open(input_jsonl_path, 'r', encoding='utf-8') as jsonl_file, \
         open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        
        writer = csv.writer(csv_file)
        writer.writerow(['uuid', 'published_at', 'vader_score']) 
        
        for line in jsonl_file:
            try:
                data = json.loads(line.strip())
                writer.writerow([
                    data.get('uuid'),
                    data.get('published_at'),
                    data.get('vader_score')  
                ])
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line[:50]}...")  

def dropDuplicates(input_path): 
    df = pd.read_csv(input_path)
    df.drop_duplicates(subset=['uuid'], keep='first').to_csv('sentiment_score/unique_sentiment.csv', index=False)

def process_vader_scores(input_csv, output_csv):
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 10, 10)
    date_range = [start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days + 1)]
    
    date_scores = defaultdict(list)
    for row in data:
        try:
            date_str = row['published_at'][:10]  
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if row['vader_score']:
                date_scores[date].append(float(row['vader_score']))
        except (ValueError, KeyError):
            continue
    
    # Calculate daily averages
    results = []
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        if date in date_scores:
            avg_score = sum(date_scores[date]) / len(date_scores[date])
            results.append([date_str, round(avg_score, 4)])
        else:
            results.append([date_str, 0.0])
    
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'avg_vader_score'])
        writer.writerows(results)

def process_initial_score(input_csv):
    input_df = pd.read_csv(input_csv)
    input_df['Date'] = pd.to_datetime(input_df['Date'])
    date_range = pd.date_range(start='2021-01-04', end='2024-10-01')
    df_full = pd.DataFrame(date_range, columns=['Date'])
    df_merged = pd.merge(df_full, input_df[['Date', 'Close']], on='Date', how='left')
    df_merged.set_index('Date', inplace=True)
    df_merged['Close'] = df_merged['Close'].interpolate(method='time', limit_area='inside')
    df_merged.reset_index(inplace=True)
    df_merged.to_csv('extract_actual.csv', index=False)

def getFinalInput(vader_file, predicted_file, actual_file):
    vader_df = pd.read_csv(vader_file)
    predicted_df = pd.read_csv(predicted_file)
    actual_df = pd.read_csv(actual_file)

    combined_df = pd.DataFrame({
        'date':actual_df['Date'],
        'vader_score': vader_df['avg_vader_score'],  
        'predicted_price': predicted_df['Predicted_Close'],  
        'actual_price': actual_df['Close']  
    })

    combined_df.to_csv('input_bigru.csv', index=False)

def replace_empty_with_zero(value):
    return value if value else '0.0'

def fillWithZeros(input, output):
    with open(input, mode='r', newline='', encoding='utf-8') as input_file, open(output, 'w', newline='', encoding='utf-8') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        header = next(reader)
        writer.writerow(header)

        for row in reader:
            updated_row = [replace_empty_with_zero(value) for value in row]
            writer.writerow(updated_row)

    print("Done")

if __name__ == "__main__":
    input_path = Path('sentiment_score/news_data_oil_expanded.jsonl')  
    output_path = Path('sentiment_score/extract_sentiment.csv') 
    
    # Sentiment Scores
    jsonl_to_csv(input_path, output_path)
    dropDuplicates('sentiment_score/extract_sentiment.csv')
    process_vader_scores('sentiment_score/unique_sentiment.csv', 'sentiment_score/final_vader_scores.csv')

    # Interpolate initial price
    # process_initial_score("initial_oil_prices.csv")

    # Combine all three
    # getFinalInput("final_vader_scores.csv", "predicted_oil_prices_sq14.csv", "extract_actual.csv")

    # Patch with zero
    # fillWithZeros("input_bigru.csv", "input_bigru_zero.csv")