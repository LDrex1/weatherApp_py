import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import json
from datetime import datetime
from dotenv import load_dotenv
import argparse
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

# Function to parse arguments with cities added as default 
def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and upload weather data to S3.")
    parser.add_argument('--cities', nargs='+', default=['London', 'Moscow', 'Beijing'], help="List of cities to fetch weather data for.")
    return parser.parse_args()

# Weather Api Class
class WeatherApi:

    # Class constructor 
    def __init__(self):
        # Class Attributes
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
        self.bucket_name =  os.getenv('AWS_S3_BUCKET_NAME','weatherapp4587')
        self.region = os.getenv('AWS_REGION','eu-west-1')
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.cities = os.getenv('CITIES', 'London, Moscow').split(',')
        self.session = requests.Session()

    # Function to check for/create Bucket
    def create_bucket(self):
        
        bucketexists = False # create bucket guard
        try:
        # Check if there is an available bucket
            print('Connecting to S3 bucket ...')
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f'bucket {self.bucket_name} found')
            bucketexists = True # Set guard to true if bucket exists
            return True
        # Execptions for ClientError
        except ClientError as e:
        # If the bucket doesn't exist or another error occurs
            if e.response['Error']['Code'] == 'NoSuchBucket':
                print(f'Bucket {self.bucket_name} does not exist, creating new bucket...')
                
            else:
                print(f'Failed to check bucket: {e}')
            
                
        # Create a new bucket is none is found        
        if bucketexists == False:
            try:
                # Case 1: for us-east-1 region
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                # Case 2: for other regions
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                print(f'S3 bucket, {self.bucket_name}  created successfully.')
                return True
            except Exception as e:  
                print(f'Failed to create S3 bucket, try again. {e}')
                return False

    # Retry connection attempt 3 times if there is faliure
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_weather_data(self, city):
        # Get weather data parameters
        params ={'q':city,'appid':self.api_key,'units':'imperial'} # query parameters

        # Send a GET request to OpenWeatherMap API and handle exceptions if request fails  or fails to fetch data
        try:
            response = self.session.get(self.base_url, params=params)
            # Raise an exception if the HTTP request returned an unsuccessful status code
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch weather data for {city}:  {e}')
            return None

    # upload process to S3 
    def upload_data_to_s3(self, city, weather_data):
        # If no data is found on the city 
        if not weather_data:
            print('Data not available')
            return False
        
        # If there is availiable data on the city
        timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
        filename = f'weatherdata/{city}/{timestamp}.json'

        try: 
            # Add timestamp to weather data dictionary
            weather_data['timestamp'] = timestamp
            # put action
            self.s3_client.put_object(
                Bucket = self.bucket_name,
                Key=filename,
                Body = json.dumps(weather_data),
                ContentType = 'application/json'

            )
            print(f'Weather data uploaded succesfull')
            return True
        except NoCredentialsError:
             print("AWS credentials not found.")
             return False
        except PartialCredentialsError:
             print("Incomplete AWS credentials provided.")
             return False
        except Exception as e:
            print(f'Error uploading weather data, error details: {e}')
            return False
        
    # App flow configuration
    @staticmethod
    def main():
        # Initialize WeatherApi instance
        weatherapp = WeatherApi()
        # Call create_bucket method
        is_bucket_created = weatherapp.create_bucket()
        if not is_bucket_created:
            print ('Bucket could not be created, closing application')
            return 
        
        # Get  cities list from arguments
        args = parse_args()
        cities = args.cities

        # Get weather data on each city and upload to s3 bucket
        for city in cities:
            print(f'Getting weather data for {city}')
            weather_data = weatherapp.get_weather_data(city)
            if weather_data:
                temp = weather_data['main']['temp']
                feels_like = weather_data['main']['feels_like']
                humidity = weather_data['main']['humidity']
                description = weather_data['weather'][0]['description']

                print(f'Weather data for {city}')
                print(f'Temperature: {temp}°F')
                print(f'Feels Like: {feels_like}°F')
                print(f'Humidity: {humidity}%')
                print(f'Description: {description}')

                # Call upload method
                uploaded = weatherapp.upload_data_to_s3(city, weather_data)
                if uploaded:
                    print(f'Weather data for {city} saved')
            else:
                print(f'Weather data not available for {city}')

if __name__ == "__main__":
   WeatherApi.main()
   