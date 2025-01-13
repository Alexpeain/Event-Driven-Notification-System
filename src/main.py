import json
import requests
import boto3

def lambda_handler(event, context):
    # Define the NBA API endpoint for teams
    url = "https://data.nba.net/data/10s/prod/v1/2023/teams.json"
    
    # Make a GET request to the NBA API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        
        # Extract team information
        teams = data.get('league', {}).get('standard', [])
        team_list = [{"fullName": team['fullName'], "abbreviation": team['tricode']} for team in teams]
        
        # Create the message
        message = "NBA Teams:\n" + "\n".join([f"{team['fullName']} ({team['abbreviation']})" for team in team_list])

        # Send notification via SNS
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:your-region:your-account-id:NBAUpdates', # Replace with your SNS Topic ARN
            Message=message,
            Subject='NBA Team Updates'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps("Notification sent successfully!")
        }
    else:
        return {
            'statusCode': response.status_code,
            'body': json.dumps({"error": "Failed to retrieve data"})
        }