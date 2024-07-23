import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import regexp_replace, split,col,lit,to_date,datediff,regexp_extract,round,when,to_timestamp,concat,lpad,unix_timestamp, from_unixtime,date_format
from awsglue.utils import getResolvedOptions
import boto3
import base64
from botocore.exceptions import ClientError
import json

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME','file_name'])
file_name = args['file_name']



sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)
print(file_name)

file_path = "s3://ashish-project-silver-temp/FlightDataSilver/"+ file_name
# df = glueContext.create_dynamic_frame.from_options(format_options={},connection_type ="s3",format="parquet",connection_options ={"paths":[file_path]})
# sdf = df.toDF()
sdf = spark.read.format("parquet").option("header", "true").load(file_path)


rename_dict = {
    "Date of Booking":"Date_of_Booking",
    "Date of Journey":"Date_of_Journey",
    "Departure Time": "Departure_Time",
    "Arrival Time": "Arrival_Time",
    "Total Stops": "Total_Stops",
}

current_columns = sdf.columns

for old_col, new_col in rename_dict.items():
    if old_col in current_columns:
        sdf = sdf.withColumnRenamed(old_col, new_col)

# Turn Price in Integer

sdf = sdf.withColumn("Price", regexp_replace("Price", ",", "").cast("integer"))
constant_date = to_date(lit('15-01-2023'), 'dd-MM-yyyy')


journey_split_col = split(sdf["Date_of_Journey"], "[-/]")

year_threshold =2000
month_threshold =12

sdf = sdf.withColumn("Date_of_Booking",constant_date)\
       .withColumn("Company", split(sdf["Airline-Class"], "\n").getItem(0)) \
       .withColumn("Flight_Route", split(sdf["Airline-Class"], "\n").getItem(1)) \
       .withColumn("Ticket_Class", split(sdf["Airline-Class"], "\n").getItem(2))\
       .withColumn("Departure_Location",split(sdf["Departure_Time"], "\n").getItem(1))\
       .withColumn("Departure_Time", split(sdf["Departure_Time"], "\n").getItem(0)) \
       .withColumn("Arrival_Location", split(sdf["Arrival_Time"], "\n").getItem(1))\
       .withColumn("Arrival_Time", split(sdf["Arrival_Time"], "\n").getItem(0)) \
       .withColumn("hours", regexp_extract(col("Duration"), r"(\d{2})h", 1).cast("int"))\
       .withColumn("minutes", regexp_extract(col("Duration"), r"(\d{2})m", 1).cast("int"))\
       .withColumn("total_hours", col("hours") + col("minutes") / 60)\
       .withColumn("Duration", round(col("total_hours"),2))\
       .withColumn("jdate", journey_split_col.getItem(0).cast("int")) \
       .withColumn("jmonth", journey_split_col.getItem(1).cast("int")) \
       .withColumn("jyear", journey_split_col.getItem(2).cast("int")) \
       .withColumn("new_col1",when(col("jdate") > year_threshold, col("jyear")).otherwise(col("jdate")))\
       .withColumn("new_col2",when(col("jyear") < year_threshold, col("jdate")).otherwise(col("jyear")))\
       .drop("jdate","jyear")\
       .withColumnRenamed("new_col1", "jdate") \
       .withColumnRenamed("new_col2", "jyear")\
       .drop("total_hours","Airline-Class")\
       .withColumn("new_col1",when(col("jmonth") >5, col("jdate")).otherwise(col("jmonth")))\
       .withColumn("new_col2",when(col("jmonth") >5, col("jmonth")).otherwise(col("jdate")))\
       .drop("jdate","jmonth","Date_of_Journey")\
       .withColumnRenamed("new_col1", "jmonth")\
       .withColumnRenamed("new_col2", "jdate")\
       .drop_duplicates().dropna(subset=["Price"])

sdf = sdf.withColumn("Dept_hr", split(sdf["Departure_Time"], ":").getItem(0)) \
       .withColumn("Dept_min", split(sdf["Departure_Time"], ":").getItem(1)) \
       .withColumn("jmonth", when(col("jmonth").cast("int") < 10, lpad(col("jmonth"), 2, "0")).otherwise(col("jmonth")))\
       .withColumn("jrndatetime", to_timestamp(concat(
        col("jyear"), lit("-"),col("jmonth"), lit("-"),col("jdate"), lit(" "),col("Dept_hr"), lit(":"),col("Dept_min")), "yyyy-MM-dd HH:mm"))\
        .withColumn("unix_time", unix_timestamp(col("jrndatetime")))\
        .withColumn("Journey_unix", col("unix_time") + (col("hours") * 3600) + (col("minutes") * 60))\
        .withColumn("arvdatetime", from_unixtime(col("Journey_unix")))\
        .withColumn("daystilljourn", datediff(col("jrndatetime"), col("Date_of_Booking")))\
        .withColumn("arvdatetime", date_format("arvdatetime", "yyyy-MM-dd HH:mm:ss"))\
        .withColumn("jrndatetime", date_format("arvdatetime", "yyyy-MM-dd HH:mm:ss"))\
        .withColumn("Date_of_Booking", date_format("Date_of_Booking", "yyyy-MM-dd"))\
        .drop("Departure_Time","jyear","jmonth","jdate","Dept_hr","Dept_min","hours","minutes","unix_time","Journey_unix",'Arrival_Time')


sfOptions = {
    "sfURL": "https://(url).snowflakecomputing.com",
    "sfUser": "username",
    "sfPassword": "Password",
    "sfDatabase": "DATABASEName",
    "sfSchema": "SCHEMANME",
    "sfWarehouse": "WAREHOUSENAME"
}

sdf.write \
    .format("net.snowflake.spark.snowflake") \
    .options(**sfOptions) \
    .option("dbtable",'FLIGHT_DATA') \
    .mode("append") \
    .save()
    
spark.stop()
job.commit()
