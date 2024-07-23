from __future__ import print_function
import boto3
import time, urllib
import json
import os

print ("*"*80)
print ("Initializing..")
print ("*"*80)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    glue = boto3.client('glue')
    # TODO implement
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    target_bucket = 'project-target-ashish'
    copy_source = {'Bucket': source_bucket, 'Key': object_key}
    print ("Source bucket : ", source_bucket)
    print ("Target bucket : ", target_bucket)
    print ("Target filename : ", filename)
    print ("Target objkey : ", object_key)

    try:
        print ("Using waiter to waiting for object to persist through s3 service")
        waiter = s3.get_waiter('object_exists')
        waiter.wait(Bucket=source_bucket, Key=object_key)
        response = glue.start_job_run(
            JobName='AshishETL',
            Arguments={
                '--file_name': filename,
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Success')
        }
    except Exception as err:
        print ("Error -"+str(err))
        return {'Error':json.dumps(str(err))}
