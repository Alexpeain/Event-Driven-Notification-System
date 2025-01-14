import os
import json
import requests
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def lambda_handler(event, context):
    # Get environment variables
    api_key = os.getenv("NBA_API_KEY")
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
    sns_client = boto3.client("sns")

    # NBA API URL
    nba_api_url = "https://www.balldontlie.io/api/v1/games"
    response = requests.get(nba_api_url)

    if response.status_code == 200:
        data = response.json()
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message='Fetched NBA data successfully!',
            Subject='NBA Data Alert'
        )
        print(json.dumps(data, indent=4))  # Log the raw data for debugging
        return {
            'statusCode': 200,
            'body': json.dumps('Data fetched successfully!')
        }
    else:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message='Failed to fetch NBA data!',
            Subject='NBA Data Fetch Error'
        )
        return {
            'statusCode': response.status_code,
            'body': json.dumps('Error fetching data')
        }