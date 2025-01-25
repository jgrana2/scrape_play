import tweepy
import os
from dotenv import load_dotenv
import aioconsole

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

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
        except Exception as e:  # Catch all exceptions
            print(f"Error posting tweet: {e}")  # Print the error but don't kill the program
    elif confirmation.lower() == 's':
        print("Tweet posting aborted.")
    else:
        print("Invalid input. Tweet posting aborted.")