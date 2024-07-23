from random import choice
from confluent_kafka import Producer
import pandas as pd
import time

conf = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all'
}

producer = Producer(conf)

def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message produced: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


def send_csv_to_kafka(csv_file, topic, batch_size=10000, sleep_time=90):
    df = pd.read_csv(csv_file)
    total_rows = len(df)
    
    for start in range(0, total_rows, batch_size):
        end = min(start + batch_size, total_rows)
        batch_df = df[start:end]
        
        for index, row in batch_df.iterrows():
            row_json = row.to_json()
            producer.produce(topic, value=row_json, callback=acked)
        
        producer.flush()
        print(f"Batch {start // batch_size + 1} sent, sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)
    
    
    producer.flush()
    print("All messages sent!")

csv_file = 'path.csv'
topic = 'flight'
send_csv_to_kafka(csv_file, topic)
