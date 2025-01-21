import os
import json
from main import lambda_handler  # Replace with your script name

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Print environment variables to verify they are loaded correctly
print("AWS_REGION:", os.getenv("AWS_REGION"))
print("DYNAMODB_TABLE_NAME:", os.getenv("DYNAMODB_TABLE_NAME"))

# Create a test event and context
test_event = {}
test_context = {}

# Call the lambda_handler function
response = lambda_handler(test_event, test_context)

# Print the response
print(json.dumps(response, indent=4))
