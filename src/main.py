import os
import json
import requests
import boto3
from datetime import datetime, timedelta
from pytz import timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def format_game_data(game):
    home_team = game['home_team']['full_name']
    visitor_team = game['visitor_team']['full_name']
    status = "Scheduled" if game['status'] == "Scheduled" else game['status']
    home_score = game['home_team_score']
    visitor_score = game['visitor_team_score']
    start_time_utc = datetime.strptime(game['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Convert start time to Myanmar Time (UTC+6:30)
    myanmar_tz = timezone("Asia/Yangon")
    start_time_mst = start_time_utc + timedelta(hours=6, minutes=30)
    start_time_str = start_time_mst.strftime("%Y-%m-%d %H:%M:%S")
    
    if status == "Final":
        return (
            f"Game Status: {status}\n"
            f"{visitor_team} vs {home_team}\n"
            f"Final Score: {visitor_score}-{home_score}\n"
            f"Start Time (Myanmar): {start_time_str}\n"
        )
    elif status == "Scheduled":
        return (
            f"Game Status: {status}\n"
            f"{visitor_team} vs {home_team}\n"
            f"Start Time (Myanmar): {start_time_str}\n"
        )
    else:
        return (
            f"Game Status: In Progress\n"
            f"{visitor_team} vs {home_team}\n"
            f"Current Score: {visitor_score}-{home_score}\n"
            f"Start Time (Myanmar): {start_time_str}\n"
        )

def lambda_handler(event, context):
    # Get environment variables
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
    sns_client = boto3.client("sns")
    
    # Today's date in UTC
    utc_today = datetime.utcnow().date()
    
    # Fetch games for today from balldontlie API
    api_url = f"https://www.balldontlie.io/api/v1/games?dates[]={utc_today}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        games = response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {"statusCode": 500, "body": "Error fetching game data"}
    
    if not games:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message="No NBA games scheduled for today.",
            Subject="NBA Game Updates"
        )
        return {"statusCode": 200, "body": "No games for today."}
    
    # Format game messages
    messages = [format_game_data(game) for game in games]
    final_message = "\n---\n".join(messages)
    
    # Publish to SNS
    try:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=final_message,
            Subject="NBA Game Updates"
        )
        print("Message published to SNS successfully.")
    except Exception as e:
        print(f"Error publishing to SNS: {e}")
        return {"statusCode": 500, "body": "Error publishing to SNS"}
    
    return {"statusCode": 200, "body": "Game updates sent successfully."}
