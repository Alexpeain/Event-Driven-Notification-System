import os
import json
import boto3
import urllib.request
from datetime import datetime, timedelta
from dotenv import load_dotenv

"""
Remove all dotenv and os.getenv when upload to lambda function
in AWS have their own variables environment
"""
# Load environment variables from .env file
load_dotenv()

# Ensure AWS credentials are loaded
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("AWS_REGION", "us-east-1")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
sports_api_key = os.getenv("NBA_API_KEY")

def format_game_summary(game):
    home_team = game["HomeTeam"]
    away_team = game["AwayTeam"]
    status = game["Status"]
    home_score = game["HomeTeamScore"]
    away_score = game["AwayTeamScore"]
    start_time_utc = datetime.strptime(game["DateTimeUTC"], "%Y-%m-%dT%H:%M:%S")

    # Convert start time to Myanmar Time (UTC+6:30)
    start_time_mst = start_time_utc + timedelta(hours=6, minutes=30)
    start_time_str = start_time_mst.strftime("%Y-%m-%d %H:%M:%S")

    summary = (
        f"🏀 **Game Summary** 🏀\n"
        f"**Status**: {status}\n"
        f"**Matchup**: {away_team} vs {home_team}\n"
        f"**Start Time (Myanmar)**: {start_time_str}\n"
    )
    if status == "Final":
        summary += f"**Final Score**: {away_score} - {home_score}\n"
    elif status == "In Progress":
        summary += f"**Current Score**: {away_score} - {home_score}\n"
    return summary

def fetch_games():
    date = datetime.utcnow().strftime('%Y-%m-%d')
    url = f"https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/{date}?key={sports_api_key}"
    
    request = urllib.request.Request(url)
    request.add_header('Ocp-Apim-Subscription-Key', sports_api_key)

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
        return []
    except urllib.error.URLError as e:
        print(f"URLError: {e.reason}")
        return []

def lambda_handler(event, context):
    # Initialize the SNS client with credentials
    sns_client = boto3.client(
        "sns",
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # Fetch game data from the sports API
    games = fetch_games()
    
    if not games:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message="No NBA games scheduled for today.",
            Subject="NBA Game Updates"
        )
        return {"statusCode": 200, "body": "No games for today."}
    
    # Format game messages
    try:
        messages = [format_game_summary(game) for game in games]
        final_message = "\n---\n".join(messages)
    except Exception as e:
        print(f"Error formatting game data: {e}")
        return {"statusCode": 500, "body": "Error formatting game data"}
    
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

# Debugging: Run the function locally (you can comment this out when deploying to Lambda)
if __name__ == "__main__":
    event = {"game": "Test Event"}
    context = {}
    lambda_handler(event, context)
