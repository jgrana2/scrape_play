import tweepy
import os
from dotenv import load_dotenv
import aioconsole
import json
import time

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

def countdown():
    data_file = 'countdown_data.json'
    
    # Initialize data if file doesn't exist
    if not os.path.exists(data_file):
        initial_data = {
            'current_value': 17,
            'last_reset': time.time()
        }
        with open(data_file, 'w') as f:
            json.dump(initial_data, f)
    
    # Read existing data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    current_value = data['current_value']
    last_reset = data['last_reset']
    current_time = time.time()
    
    # Reset if 24 hours have passed
    if current_time - last_reset >= 86400:
        current_value = 17
        last_reset = current_time
    
    # Get return value and decrement for next call
    return_value = current_value
    current_value -= 1
    
    # Save updated data
    with open(data_file, 'w') as f:
        json.dump({
            'current_value': current_value,
            'last_reset': last_reset
        }, f)
    
    return return_value

async def post(text):
    print("Press Enter to post, or type 's' to skip.")

    # Asynchronously wait for user input
    confirmation = await aioconsole.ainput()

    if confirmation.strip() == '':
        # Authenticate to Twitter
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )

        # Create a tweet
        try:
            response = client.create_tweet(text=text)
            print("Tweet posted successfully!")
            # Update and display countdown
            current_count = countdown()  # <-- Added countdown call
            print(f"\nPosts remaining before daily reset: {current_count}\n")
        except Exception as e:  # Catch all exceptions
            print(f"Error posting tweet: {e}")  # Print the error but don't kill the program
    elif confirmation.lower() == 's':
        print("Tweet posting aborted.")
    else:
        print("Invalid input. Tweet posting aborted.")