from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, FloatType, DoubleType

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField ,StringType
from pyspark.sql.functions import from_json,col


schema = StructType([
    StructField("Date of Booking", StringType(), True),
    StructField("Date of Journey", StringType(), True),
    StructField("Airline-Class", StringType(), True),
    StructField("Departure Time", StringType(), True),
    StructField("Arrival Time", StringType(), True),
    StructField("Duration", StringType(), True),
    StructField("Total Stops", StringType(), True),
    StructField("Price", StringType(), True)
])


jars_path = "path/to/hadoop-aws-3.3.4.jar,path/to//aws-java-sdk-bundle-1.11.1026.jar"

access_key = ""
secret_access_key = ""

data_path = '-'
checkpoint_path = '-'

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
            .option("failOnDataLoss", "false") 
            .option('startingOffsets', 'earliest')
            .load()
            .selectExpr('CAST(value AS STRING)')
            )

def streamWriter(input: DataFrame,checkpointFolder, output):
    return (input.writeStream.format('parquet')
            .option("path", output)
            .option("checkpointLocation", checkpointFolder)
            .outputMode('append')
            .start())    

        
df = read_kafka_topic('flight').alias('data')
df = df.withColumn("value", from_json(col("value"), schema)).select("value.*")
query = streamWriter(df,checkpoint_path,data_path)
query.awaitTermination()

 
 
