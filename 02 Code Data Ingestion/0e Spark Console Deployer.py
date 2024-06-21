from pyspark.sql import SparkSession, DataFrame

def main():       
    spark = SparkSession.builder.appName("KafkaProject")\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1") \
    .getOrCreate()
 
    def read_kafka_topic(topic):
        return (spark.readStream
                .format('kafka')
                .option('kafka.bootstrap.servers', 'localhost:9092')
                .option('subscribe', topic)
                .option('startingOffsets', 'earliest')
                .load()
                .selectExpr('CAST(key AS STRING)','CAST(value AS STRING)')
                )
        
    def streamWriter(input: DataFrame):
        return (input.writeStream
                .format('console')
                .trigger(processingTime='30 seconds')
                .outputMode('append')
                .start())

    airDF = read_kafka_topic('airfoil').alias('data')
    print(airDF)
    query = streamWriter(airDF)
    query.awaitTermination()
 
if __name__ == "__main__":
    main()