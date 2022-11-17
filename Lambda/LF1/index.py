import json
import logging
import boto3
import uuid
import requests
import json
from datetime import datetime
from pprint import pprint

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    # TODO implement
    
    logger.debug(f"[USER][EVENT] {event}")
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_name = event['Records'][0]['s3']['object']['key']
    logger.debug(f"[USER][NAME] Bucket: {bucket_name}  Image: {image_name}")
    
    client_rec =boto3.client('rekognition', region_name = 'us-east-1')
    response_res = client_rec.detect_labels(Image={'S3Object':{'Bucket':bucket_name,'Name':image_name}},
        MaxLabels=10)
    logger.debug(f"[USER][RECOGNITION] {response_res}")
    # print("Recognition Done")
    
    client_s3 = boto3.client('s3')
    response_s3 = client_s3.head_object(Bucket=bucket_name, Key=image_name)
    logger.debug(f"[USER][S3] {response_s3}")
    
    meta_labels = []
    try:
        meta_labels = [l.strip() for l in response_s3['Metadata']['customlabels'].strip().split(',')]
    except KeyError:
        meta_labels = []

    labels = [label['Name'] for label in response_res['Labels']] + meta_labels
    
    a1 = {}
    a1["objectKey"] = image_name
    a1["bucket"] = bucket_name
    a1["createdTimestamp"] = str(datetime.now())
    a1["labels"] = labels
    logger.debug(f"[USER][ES JSON] {a1}")
    
    host = 'https://search-sv-photos-zmrwllokdrva47w42s6dg5jxi4.us-east-1.es.amazonaws.com'
    _index = 'photos'
    _type = 'Photo'
    _id = uuid.uuid1().hex
    
    path = '/{}/{}/{}/'.format(_index, _type, _id)
    master_user = ""
    master_password = ""
    
    url = host + path
    r = requests.post(url, auth=(master_user, master_password), json=a1)
    print("lf1 response: ",r)
    #logger.debug(json.loads(r.content))
    

    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
