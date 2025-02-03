import os
from dotenv import load_dotenv
import openai
import asyncio
from twscrape import API
from unidecode import unidecode
import sys
import pyperclip
from typing import List, Dict
from gpt import sendToGPT
from gt import get_google_trends
from tt import get_twitter_trends
from create_post import post
import json
import re
from typing import List, Dict
import aioconsole

# Load environment variables from the .env file
load_dotenv()

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def clean_trend_name(trend_name: str) -> str:
    """
    Cleans the trend name by removing trailing numerical data like '12K', '18K', etc.
    Args:
        trend_name (str): The original trend name with possible trailing numbers.
    Returns:
        str: The cleaned trend name without trailing numbers.
    """
    # Regular expression to remove trailing numbers with optional 'K' or 'M'
    cleaned_name = re.sub(r'\d+[KM]?$', '', trend_name).strip()
    return cleaned_name

def fix_encoding(trend_name: str) -> str:
    """
    Attempts to fix common encoding issues in trend names.
    Args:
        trend_name (str): The trend name with potential encoding issues.
    Returns:
        str: The trend name with corrected encoding.
    """
    try:
        # Attempt to fix encoding by assuming it was decoded incorrectly
        return trend_name.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If fixing fails, return the original trend name
        return trend_name

def get_trends_json(ttrends: List[Dict], gtrends: List[Dict]) -> Dict:
    """
    Combine Twitter and Google trends into a single list and return as a JSON object.
    Args:
        ttrends (List[Dict]): List of Twitter trends.
        gtrends (List[Dict]): List of Google trends.
    Returns:
        Dict: JSON object with a single key "trends".
    Requirements:
        Do not include the number of views.
    """
    combined_trends = []
    
    # Extract and clean trend names from Twitter
    for trend in ttrends:
        trend_name = trend.get("name")
        if trend_name:
            fixed_name = fix_encoding(trend_name)
            cleaned_name = clean_trend_name(fixed_name)
            combined_trends.append(cleaned_name)
    
    # Extract and clean trend titles from Google
    for trend in gtrends:
        trend_title = trend.get("title")
        if trend_title:
            fixed_title = fix_encoding(trend_title)
            cleaned_title = clean_trend_name(fixed_title)
            combined_trends.append(cleaned_title)
    
    # Return the combined trends without any numerical data
    return {"trends": combined_trends}

def sendToGPT(copyPrompt, use_ollama=False):
    if use_ollama:
        client = openai.OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama'  # Required but unused
        )
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[
                {"role": "user", "content": copyPrompt}
            ],
            stream=True
        )
    else:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="o1-mini",
            messages=[
                {"role": "user", "content": copyPrompt}
            ],
            stream=True
        )
    
    full_response = ""
    
    # Stream the response
    for chunk in response:
        if chunk.choices[0].delta.content is not None:  # Check for NoneType instead of "None"
            print(chunk.choices[0].delta.content, end='')  # Specify end parameter
            full_response += chunk.choices[0].delta.content

    print()  # Ensures a newline
    pyperclip.copy(full_response)
    return full_response


async def searchTweetsAndCreatePrompt(searchTerm, mode="t", format="s"):
    api = API()
    
    # Search for tweets
    tweets = []
    search_query = f"{searchTerm} filter:links"
    try:
        async for tweet in api.search(search_query, limit=20):
            tweets.append(tweet.rawContent)
    except Exception as e:
        print(f"[ERROR] Error during tweet search: {e}")
        return

    if not tweets:
        print(f"[WARNING] No tweets found for the trend: '{searchTerm}'")
        return
    
    # Create base prompt and adjust the length requirement based on the format
    lengthRequirement = "The tweet must have a maximum of 250 characters in length." if format == "s" else "The tweet must have a minimum of 450 characters in length."
    
    copyPrompt = """From now on, you're a skilled social media content creator.
Instruction: Create an engaging tweet based on the provided trusted tweets. Follow these steps:
News topic: {}
News:

{}

Requirements:
- {}
- The tweet is a single coherent one without emojis or hashtags.
- Ignore any news irrelevant to the news topic.
- Make the tweet engaging and interesting.
- The tweet must be in Spanish.
- News concerning politics or religion must be unbiased.
- Don't be opinionated.
- Don't be so excited, be less annoying.
- You absolutely MUST include a RELEVANT link from those tweets in your original response. Ensure that the link directly relates to the topic and provides valuable insights or additional information. No placeholders should be used.
- Don't support leftism.
- Don’t use purple prose.
- Use active voice when possible.
- Don't say "Discover" or "Descubre" because it's too used now.
- Don't say "Mas detalles aquí", simply paste the link without introducing it.
""".format(searchTerm, '\n'.join(tweets), lengthRequirement)
    
    return sendToGPT(copyPrompt)

async def main_async(trends, limit=None):
    """
    Asynchronous main function to process each trend sequentially.

    Args:
        trends (list): A list of trend strings to process.
    """
    # Validate the limit parameter
    if limit is not None:
        if not isinstance(limit, int):
            raise ValueError("Limit must be an integer.")
        if limit < 1:
            raise ValueError("Limit must be a positive integer.")
        # Slice the trends list to the specified limit
        selected_trends = trends[:limit]
    else:
        # If no limit is provided, use all trends
        selected_trends = trends

    for trend in selected_trends:
        print(f"Current trend: {trend}")
        
        # Await user confirmation to process or skip the trend
        user_input = await aioconsole.ainput("Press Enter to process or 's' to skip: ")
        
        if user_input.lower() == 's':
            print("Skipping the trend.")
            continue
        
        # Process the trend if Enter is pressed
        await post(await searchTweetsAndCreatePrompt(trend))

def main():
    """
    Main function to execute the trend summarization.
    """

    # Fetch trends from Twitter and Google
    ttrends = get_twitter_trends()
    gtrends = get_google_trends()

    if not ttrends and not gtrends:
        print("No trends found from Twitter or Google.")
        return

    # Generate the trends JSON
    trends_object = get_trends_json(ttrends, gtrends)

    trends = trends_object.get("trends", [])
    
    if not trends:
        print("[ERROR] No trends found in the provided object.")
        return
    
    # Serialize the JSON with ensure_ascii=False to preserve accents
    trends_json = json.dumps(trends_object, ensure_ascii=False, indent=2)

    # Output the JSON (you can also write this to a file)
    loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(loop)  # Set it as the current event loop
    try:
        loop.run_until_complete(main_async(trends))
    except Exception as e:
        print(f"[ERROR] An exception occurred during asynchronous processing: {e}")
    finally:
        loop.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[CRITICAL] An unhandled exception occurred: {e}")
        sys.exit(1)