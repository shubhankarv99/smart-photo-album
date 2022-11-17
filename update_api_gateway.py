print("start")
import os
os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

import ruamel.yaml
from pathlib import Path
import boto3
import argparse
from botocore.client import ClientError
 
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--stackname", help = "Name of stack created for stack_1.yaml", default='sv-stack-1')
parser.add_argument("-b", "--bucketname", help = "Name of the bucket in which api gate way will go", default='sv-b1-frontend')
args = parser.parse_args()

client = boto3.client("sts")
                      

account_id = client.get_caller_identity()["Account"]

print("a")

cloudformation = boto3.resource('cloudformation')
stack_apis3arn = cloudformation.StackResource(args.stackname,'apigateways3role')
apigateways3rolearn = stack_apis3arn.physical_resource_id

stack_lf2arn = cloudformation.StackResource(args.stackname,'lf2')
lf2arn = stack_lf2arn.physical_resource_id

swagger_file = ruamel.yaml.round_trip_load(Path("api_gateway.yaml").read_text(), preserve_quotes=True)
swagger_file['paths']['/search']['get']['x-amazon-apigateway-integration']['uri'] = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:{account_id}:function:{lf2arn}/invocations"
swagger_file['paths']['/upload/{bucket}/{filename}']['put']['x-amazon-apigateway-integration']['credentials'] = f"arn:aws:iam::{account_id}:role/{apigateways3rolearn}"

f = open('api_gateway.yaml', 'w+')
ruamel.yaml.round_trip_dump(swagger_file, f, explicit_start=True)
f.close()

print("b")
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = s3.Bucket(args.bucketname)
if bucket.creation_date:  
    response = s3_client.upload_file("api_gateway.yaml", args.bucketname, "AI-Photo-Search-v1-swagger-apigateway-v1.yaml")
else:
    s3_client.create_bucket(args.bucketname)
    response = s3_client.upload_file("api_gateway.yaml", args.bucketname, "AI-Photo-Search-v1-swagger-apigateway-v1.yaml")

# print(f"arn:aws:lambda:us-east-1:{account_id}:function:{lf2arn}")
# aws cloudformation create-stack --template-body file://stack_2.yaml --capabilities CAPABILITY_IAM --stack-name test2 --parameters ParameterKey=lf2arn,ParameterValue=arn:aws:lambda:us-east-1:227712325985:function:lf2-cf
