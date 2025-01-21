import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json
from datetime import datetime
from dotenv import load_dotenv
import argparse
from tenacity import retry, stop_after_attempt, wait_fixed

# function to parse arguments with cities added as default 
def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and upload weather data to S3.")
    parser.add_argument('--cities', nargs='+', default=['London', 'Moscow', 'Beijing'], help="List of cities to fetch weather data for.")
    return parser.parse_args()

class weatherApi:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
        self.bucket_name =  os.getenv('AWS_S3_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION','eu-west-1')
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.cities = os.getenv('CITIES').split(',')
        self.session = requests.Session()


    def create_bucket(self):
        # Check if there is an available bucket
        try:
            print('Connecting to S3 bucket ...')
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f'bucket {self.bucket_name} found')

        # Create a new bucket is none is found
        except:
            print('Creating S3 bucket ...')
        try:
            self.s3_client.create_bucket(Bucket=self.bucket_name, Create_BucketConfiguration={'LocationConstraint': self.region})
            print(f'S3 bucket, {self.bucket_name}  created successfully.')
        except Exception as e:  
            print(f'Failed to create S3 bucket, try again. {e}')

    # Retry connection attempt 3 times if there is faliure
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_weather_data(self, city):

        params ={'q':city,'appid':self.api_key,'units':'imperial'} # query parameters

        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f'Error fetching weather data: {e}')
            return None

    # upload process to S3 
    def upload_data_to_s3(self, city, weather_data):

        if not weather_data:
            print('Data not available')
            return False
        
        timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
        filename = f'weatherdata/{city}/{timestamp}'

        try: 
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
        except PartialCredentialsError:
             print("Incomplete AWS credentials provided.")
        except Exception as e:
            print(f'Error uploading weather data, error details: %s /n')
            return False
        

    def main():
        weatherapp = weatherApi()

        weatherapp.create_bucket()
        args = parse_args()
        cities = args.cities

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

                uploaded = weatherapp.upload_data_to_s3(city, weather_data)
                if uploaded:
                    print(f'Weather data for {city} saved')
            else:
                print(f'Weather data not available for {city}')
    if __name__ == "__main__":
        main()