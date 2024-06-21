from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, FloatType, DoubleType

def main():       
    jars_path = "/home/growlt243/Downloads/hadoop-aws-3.3.4.jar,/home/growlt243/Downloads/aws-java-sdk-bundle-1.11.1026.jar"
    
    aaccess_key = "-"
    secret_access_key = "-"
    data_path = '-'
    checkpoint_folder_path = '-'

    spark = SparkSession.builder.appName("KafkaProject")\
    .config("spark.jars", jars_path)\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")\
    .config("spark.hadoop.fs.s3a.access.key", access_key)\
    .config("spark.hadoop.fs.s3a.secret.key", secret_access_key)\
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")\
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
    query = streamWriter(airDF,checkpoint_folder_path,data_path)
    query.awaitTermination()
 
if __name__ == "__main__":
    main()