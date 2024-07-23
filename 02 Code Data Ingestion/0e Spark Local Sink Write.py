from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, FloatType, DoubleType

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
    
    def streamWriter(input: DataFrame,checkpointFolder, output):
        return (input.writeStream
                .format('parquet')
                .option("path", output)
                .option("checkpointLocation", checkpointFolder)
                .trigger(processingTime='30 seconds')
                .outputMode('append')
                .start())            
 

    airDF = read_kafka_topic('airfoil').alias('data')
    print(airDF)
    query = streamWriter(airDF,'/path/checkpoint location','path/data')
    query.awaitTermination()
 
if __name__ == "__main__":
    main()
