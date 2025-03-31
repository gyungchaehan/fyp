import csv

rows = []

def get_data(csv_file_path):
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            # Create a CSV reader object
            csv_reader = csv.reader(csvfile)
            first_line = 0

            for row in csv_reader:
                first_line+=1
                # if (first_line == -1):
                #     first_line += 1
                #     continue
                # elif (first_line == 10):
                #     break
                # else:
                #     temp = row[3].split(', ')
                #     # first_line += 1
                #     if (temp.count('oil') > 0):
                #         temp_dict = {
                #             'id': row[0],
                #             'title': row[1],
                #             'url': row[5],
                #             'published_at': row[8],
                #             'source': row[-3]
                #         }
                #         rows.append(temp_dict)
            print(first_line)
                        

    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def write_data():
    fieldnames = ['id', 'title', 'url', 'published_at', 'source']

    try:
        with open('news_data_final.csv', 'r', newline='', encoding='utf-8') as file:
            existing_data = list(csv.DictReader(file))
    except FileNotFoundError:
        existing_data = []


    with open('news_data_final.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=',', extrasaction='ignore')

        if not existing_data:
            writer.writeheader()

        for item in rows:
            writer.writerow(item)


csv_file_path = 'news_data_final.csv' 
get_data(csv_file_path)
# write_data()