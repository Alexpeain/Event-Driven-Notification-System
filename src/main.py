import os
import json
import boto3
import urllib.request
from datetime import datetime, timedelta
from dotenv import load_dotenv
from botocore.exceptions import ClientError

"""
The is for local machine.
Use AWS : Have to Remove all dotenv and os.getenv when upload to lambda function
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
dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")

dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(dynamodb_table_name)

def format_game_summary(game):
    try:
        # Validate required fields
        required_fields = ['GameID', 'HomeTeam', 'AwayTeam', 'Status', 'DateTimeUTC']
        for field in required_fields:
            if field not in game:
                print(f"Missing required field: {field}")
                return None
                
        game_id = str(game["GameID"]) 
        home_team = game["HomeTeam"]
        away_team = game["AwayTeam"]
        status = game["Status"]
        home_score = game.get("HomeTeamScore", 0)
        away_score = game.get("AwayTeamScore", 0)
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
        
        item = {
            'ID': game_id, 
            'Summary': summary,
            'Status': status,
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'HomeScore': home_score,
            'AwayScore': away_score,
            'Timestamp': start_time_str
        }
        
        return item
    except Exception as e:
        print(f"Error formatting game summary: {e}")
        return None

def fetch_games():
    try:
        date = datetime.utcnow().strftime('%Y-%m-%d')
        start_url = f"https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/{date}?key={sports_api_key}"
        url = start_url.replace(" ","") # Remove any whitespace characters
        request = urllib.request.Request(url)
        request.add_header('Ocp-Apim-Subscription-Key', sports_api_key)

        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                print(f"API returned status code: {response.status}")
                return []
            data = response.read().decode()
            return json.loads(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in fetch_games: {e}")
        return []

def lambda_handler(event, context):
    try:
        # Initialize the SNS client
        sns_client = boto3.client("sns", region_name=region_name)
        
        # Fetch game data from the sports API
        games = fetch_games()
        
        if not games:
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Message="No NBA games scheduled for today.",
                Subject="NBA Game Updates"
            )
            return {"statusCode": 200, "body": "No games for today."}
        
        # Save game summaries to DynamoDB and publish to SNS
        valid_games = []
        for game in games:
            try:
                item = format_game_summary(game)
                if item:
                    table.put_item(Item=item)
                    valid_games.append(item)
                    print(f"Saved summary for game {game['GameID']} to DynamoDB")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ProvisionedThroughputExceededException':
                    print("DynamoDB throughput exceeded")
                elif error_code == 'ResourceNotFoundException':
                    print("Table not found")
                else:
                    print(f"Unknown DynamoDB error: {error_code}")

        # Format and publish game summaries to SNS
        if valid_games:
            try:
                messages = [game['Summary'] for game in valid_games]
                final_message = "\n---\n".join(messages)
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=final_message,
                    Subject="NBA Game Updates"
                )
                print("Message published to SNS successfully.")
            except Exception as e:
                print(f"Error publishing to SNS: {e}")
                return {"statusCode": 500, "body": f"Error publishing to SNS: {e}"}
        
        return {"statusCode": 200, "body": "Game updates sent successfully."}
    except Exception as e:
        print(f"Unexpected error in lambda_handler: {e}")
        return {"statusCode": 500, "body": "Internal server error"}

# Debugging: Run the function locally
if __name__ == "__main__":
    event = {"game": "Test Event"}
    context = {}
    lambda_handler(event, context)