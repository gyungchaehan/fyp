import pandas as pd

# Load the first CSV file
file1 = 'news_data_2022_new.csv'  # Replace with your first CSV file path
df1 = pd.read_csv(file1)

# Load the second CSV file
file2 = 'combined_file_second.csv'  # Replace with your second CSV file path
df2 = pd.read_csv(file2)

# Concatenate the two DataFrames
# By default, it concatenates along the rows (axis=0)
combined_df = pd.concat([df1, df2], ignore_index=True)

# Save the concatenated DataFrame to a new CSV file
combined_df.to_csv('news_data_2022.csv', index=False)

print("CSV files concatenated successfully!")