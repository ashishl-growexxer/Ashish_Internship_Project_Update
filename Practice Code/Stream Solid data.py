import csv
import time

def data_stream(csv_file, chunk_size, interval):

    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
                time.sleep(interval)
        if chunk:
            yield chunk

# Example usage:
csv_file = '/home/growlt243/Desktop/Working Consistently/00 Data/csv_data/airfoil_self_noise.csv'
chunk_size = 10
interval = 1  # seconds

for chunk in data_stream(csv_file, chunk_size, interval):
    for row in chunk:
        print(row)
    print('------------------------------------------------------------------------------')
