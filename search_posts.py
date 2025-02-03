import tweepy
import os
from dotenv import load_dotenv
import aioconsole

# Load environment variables from the .env file
load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

response = client.search_recent_tweets(query='Cartagena')

for tweet in response.data:
    print(tweet.id)
