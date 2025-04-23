import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

def process_sentiment_data(sentiment_jsonl):
    """Process sentiment JSONL file and return a DataFrame with daily average Vader scores"""
    # Read JSONL and collect all entries
    data = []
    with open(sentiment_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                data.append({
                    'uuid': entry.get('uuid'),
                    'published_at': entry.get('published_at'),
                    'vader_score': entry.get('vader_score')
                })
            except json.JSONDecodeError:
                continue
    
    # Convert to DataFrame and remove duplicates
    df = pd.DataFrame(data).drop_duplicates(subset=['uuid'], keep='first')
    
    # Process dates and calculate daily averages
    date_scores = defaultdict(list)
    for _, row in df.iterrows():
        try:
            date_str = row['published_at'][:10]
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if pd.notna(row['vader_score']):
                date_scores[date].append(float(row['vader_score']))
        except (ValueError, TypeError):
            continue
    
    # Create date range
    start_date = datetime(2021, 1, 4).date()
    end_date = datetime(2024, 10, 1).date()
    date_range = [start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days + 1)]
    
    # Build results
    vader_data = []
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        if date in date_scores:
            avg_score = sum(date_scores[date]) / len(date_scores[date])
            vader_data.append([date_str, round(avg_score, 4)])
        else:
            vader_data.append([date_str, 0.0])
    
    return pd.DataFrame(vader_data, columns=['date', 'vader_score'])

def process_price_data(initial_prices_file):
    """Process initial oil prices and return a DataFrame with interpolated daily prices"""
    df = pd.read_csv(initial_prices_file)
    df['Date'] = pd.to_datetime(df['Date'])
    date_range = pd.date_range(start='2021-01-04', end='2024-10-01')
    df_full = pd.DataFrame(date_range, columns=['Date'])
    df_merged = pd.merge(df_full, df[['Date', 'Close']], on='Date', how='left')
    df_merged.set_index('Date', inplace=True)
    df_merged['Close'] = df_merged['Close'].interpolate(method='time', limit_area='inside')
    return df_merged.reset_index()

def create_final_output(sentiment_jsonl, initial_prices_file, predicted_prices_file, output_file):
    # Process all data sources
    vader_df = process_sentiment_data(sentiment_jsonl)
    actual_df = process_price_data(initial_prices_file)
    predicted_df = pd.read_csv(predicted_prices_file)
    
    # Combine all data
    combined_df = pd.DataFrame({
        'date': actual_df['Date'].dt.strftime('%Y-%m-%d'),
        'vader_score': vader_df['vader_score'],
        'predicted_price': predicted_df['Predicted_Close'],
        'actual_price': actual_df['Close']
    })
    
    combined_df = combined_df[combined_df['date'] <= '2024-10-01']

    # Fill any remaining NA values with 0.0
    combined_df.fillna(0.0, inplace=True)
    
    # Save to CSV
    combined_df.to_csv(output_file, index=False)
    print(f"Successfully created output file: {output_file}")

if __name__ == "__main__":
    # Define input files
    sentiment_jsonl = 'news_data.jsonl'
    initial_prices = 'historical_oil_prices.csv'
    predicted_prices = 'lstm_oil_prices.csv'
    output_file = 'input_bigru.csv'
    
    # Run the processing
    create_final_output(sentiment_jsonl, initial_prices, predicted_prices, output_file)