# Weather Data Collector and S3 Uploader

This Python project fetches weather data for specified cities from the OpenWeather API and uploads the data to an AWS S3 bucket for storage. The application supports retry mechanisms for API calls, handles bucket creation, and logs relevant weather details for the user. It also contains tests to verify that all actions are working as intended.

---

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Example Output](#example-output)

---

## Features

- Fetches real-time weather data for multiple cities.
- Automatically creates an S3 bucket if it doesn't exist.
- Retries API calls up to 3 times in case of failures.
- Saves weather data in JSON format with a timestamp.
- Logs key weather information, including temperature, humidity, and weather description.

---

## Prerequisites

- [Python](https://www.python.org/) v3.12 or higher installed on your system.
- AWS credentials configured for your environment (via AWS CLI or environment variables).
- OpenWeather API key.
- Access to an S3 bucket or permission to create one.

---

## Directory Structure
```bash
project_root/
│
├── src/
│   ├── weather_api.py          # Main script for fetching and uploading weather data
|   └── weather_api.test.py     # Test file
│
├── requirements.txt             # Project dependencies
├── README.md                    # Project documentation
├── .env                         # Environment variables (not committed to version control)
```

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/LDrex1/weatherApp_py.git
   cd WeatherApp_py
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   
## Usage
1. **Set up Environment Variables**
   ```makefile
   OPENWEATHER_API_KEY=your_openweather_api_key
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=your_aws_region
   AWS_S3_BUCKET_NAME=your_s3_bucket_name
   CITIES=London,Moscow,Beijing
   ```
2. **Run the Test**
   ```bash
   cd src
   pytest -v
   ```
2. **Run the Application**
   ```bash
   python weather_api.py
   ```
   with command line arguments
   ```bash
   python weather_api.py --cities NewYork Tokyo Paris
   ```

## Example Output
   ```bash
    Getting weather data for London
    Weather data for London:
    Temperature: 55.4°F
    Feels Like: 52.2°F
    Humidity: 60%
    Description: overcast clouds
    Weather data for London saved

    Getting weather data for Moscow
    Weather data not available for Moscow
   ``` 
  **S3 bucket File Structure**
  ```bash
   watherApp_py/
    ├── London/
    │   ├── 23012025-113045.json
    │   ├── 23012025-120050.json
    │   └── ...
    ├── Beijing/
    │   ├── 23012025-113045.json
    │   └── ...
   ```
  
    
    
    



  
