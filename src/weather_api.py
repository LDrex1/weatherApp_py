import os
import requests
import boto3
import json
from datetime import datetime
from dotenv import load_dotenv

class weatherApi:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
        self.bucket_name =  os.getenv('AWS_S3_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION','eu-west-1')
        self.s3_client = boto3.client('s3', region_name=self.region)

    