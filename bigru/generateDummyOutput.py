import pandas as pd
import random

# Define the number of rows
num_rows = 942

# Create a list to hold the data
data = []

# Generate the data
for _ in range(num_rows):
    score = random.uniform(-1, 1)  # Random float from -1 to 1
    data.append({"score": score})

# Create a DataFrame
df = pd.DataFrame(data)

# Write the DataFrame to a CSV file
df.to_csv('lstm_file.csv', index=False)

print("CSV file 'lstm_file.csv' generated successfully with 942 rows.")