from random import choice
from confluent_kafka import Producer

if __name__ == '__main__':
    config = {
        'bootstrap.servers': 'localhost:9092',
        'acks': 'all'
    }

    producer = Producer(config)

    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    # Produce data by selecting random values from these lists.
    topic = "airfoil"
    count=1
    
    with open("path/to/data.csv") as fp:
        Lines = fp.readlines()
        for line in Lines:
            producer.produce(topic, line.strip(),str(count), callback=delivery_callback)
            count += 1


    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()
