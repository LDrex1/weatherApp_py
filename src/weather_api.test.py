import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError, ClientError
from tenacity import RetryError
from weather_api import WeatherApi 

@pytest.fixture
def weather_api():
    return WeatherApi()

@patch('requests.Session.get')
def test_get_weather_data_success(mock_get, weather_api):
    # Mock for successful fetch
    mock_get.return_value.status_code = 200
    # Mock value
    mock_get.return_value.json.return_value = {
        "main": {"temp": 70, "feels_like": 68, "humidity": 50},
        "weather": [{"description": "clear sky"}]
    }
    
    result = weather_api.get_weather_data('London')

    # assertions
    assert result is not None
    assert 'main' in result
    assert result['main']['temp'] == 70
    assert result['weather'][0]['description'] == 'clear sky'

@patch('requests.Session.get')
def test_get_weather_data_failure(mock_get, weather_api):
    mock_get.side_effect = Exception("API is down")
    with pytest.raises(RetryError):
        result = weather_api.get_weather_data('London')
        assert result is None
    assert mock_get.call_count == 3


@patch('weather_api.boto3.client')
def test_bucket_exists(mock_boto3, weather_api):
    # Use Mock client
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3

    weather_api.s3_client = mock_s3
   
    # Simulate that head_bucket exists (No exception)
    mock_s3.head_bucket.return_value = None 

    result = weather_api.create_bucket()

    mock_s3.head_bucket.assert_called_once()

    # Check that create_bucket is NOT called when bucket exists
    mock_s3.create_bucket.assert_not_called()

    # Assertions
    assert result is True

# specific test parameters for creating a new bucket (with us-east-1 special case and other regions)
@pytest.mark.parametrize("region, expected_call", [
    ("us-east-1", {'Bucket': 'test-bucket'}),
    ("eu-west-1", {'Bucket': 'test-bucket', 'CreateBucketConfiguration': {'LocationConstraint': 'eu-west-1'}})
])
@patch('weather_api.boto3.client')
def test_create_new_bucket(mock_boto3,region, weather_api, expected_call):
    # Use Mock client
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3
    weather_api.s3_client = mock_s3
   
    # Simulate that head_bucket to raise an exception that bucket does not exist
    mock_s3.head_bucket.side_effect = ClientError(
        error_response={
            'Error': {
                'Code': 'NoSuchBucket',
                'Message': 'The specified bucket does not exist.'
            }
        },
        operation_name='HeadBucket'
    )

    # Simulate that create_bucket success
    mock_s3.create_bucket.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

    # Defining test parameters
    weather_api.bucket_name = "test-bucket"
    weather_api.region = region
    # Now, call the method you want to test
    result = weather_api.create_bucket()

    # Check that head_bucket was called once to check if the bucket exists
    mock_s3.head_bucket.assert_called_once_with(Bucket=weather_api.bucket_name)

    # Check that create_bucket is called once
    mock_s3.create_bucket.assert_called_once_with(**expected_call)


@patch('weather_api.boto3.client')
def test_upload_data_to_s3_success(mock_boto3, weather_api):
    # Use Mock client to upload data
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3
    weather_api.s3_client = mock_s3


    mock_s3.put_object.return_value = True

    # Test weather data to be uploaded    
    weather_data = {
        "main": {"temp": 70, "feels_like": 68, "humidity": 50},
        "weather": [{"description": "clear sky"}]
    }

    
    result = weather_api.upload_data_to_s3("London", weather_data)

    # Assertions
    assert result is True
    mock_s3.put_object.assert_called_once()


@patch('weather_api.boto3.client')
def test_upload_data_to_s3_failure(mock_boto3, weather_api):
    # Use Mock client 
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3
    weather_api.s3_client = mock_s3

    # Simulate that put_object raises an exception (no credentials)
    mock_s3.put_object.side_effect = NoCredentialsError()

    # Test weather data to be uploaded
    weather_data = {
        "main": {"temp": 70, "feels_like": 68, "humidity": 50},
        "weather": [{"description": "clear sky"}]
    }

    # Assertions
    result = weather_api.upload_data_to_s3("London", weather_data)
    assert result is False
    mock_s3.put_object.assert_called_once()




  