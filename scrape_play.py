import os
from dotenv import load_dotenv
import openai
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from twscrape import API
from unidecode import unidecode
import pyperclip

# Load environment variables from the .env file
load_dotenv()

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def sendToGPT(copyPrompt):
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        #model="gpt-4-1106-preview",
        # model="gpt-4",
        model="gpt-4o-mini",
        #model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "Eres un asistente útil."},
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

    pyperclip.copy(full_response)

async def searchTweetsAndCreatePrompt(searchTerm, mode="tweet"):
    print("Searching tweets...")
    api = API()
    
    # Add and login accounts
    # Assuming you have environment variables set for your credentials
    twscrape_username = os.environ.get("TWSCRAPE_USERNAME")
    twscrape_password = os.environ.get("TWSCRAPE_PASSWORD")
    twscrape_email = os.environ.get("TWSCRAPE_EMAIL")
    twscrape_api_key = os.environ.get("TWSCRAPE_API_KEY")

    print("Adding account...")
    await api.pool.add_account(twscrape_username, twscrape_password, twscrape_email, twscrape_api_key)

    print("Logging in...")
    await api.pool.login_all()
    
    print("Searching...")
    # Search for tweets
    tweets = []
    async for tweet in api.search(f"{searchTerm} filter:trusted", limit=20):
        tweets.append(tweet.rawContent)
    
    # Create prompt based on mode
    copyPrompt = """From now on, you're an excellent social media content creator.
Instruction: make a tweet based on the provided trusted tweets. Think step by step.
News topic: {}
News:
{}
Requirements:
- The tweet is a single coherent one with emojis and hashtags.
- Ignore any news irrelevant to the news topic.
- Make the tweet engaging and interesting.
- The tweet must be in Spanish.
- News concerning politics or religion must be unbiased.
- Don't be opinionated.
- Don't be so excited, be less annoying.
- You absolutely MUST include a RELEVANT link from those tweets in your original response. Ensure that the link directly relates to the topic and provides valuable insights or additional information. No placeholders should be used.
- Don't support leftism.
- The tweet must have a maximum of 250 characters in length.
- Don’t use purple prose.
- Use active voice when possible.
- Don't say "Discover" or "Descubre" because it's too used now.
- Only use the top 3000 most commonly used words unless specifically relevant""".format(searchTerm, '\n'.join(tweets))
    
    print("Processing...\n")
    if mode == "t":
        sendToGPT(copyPrompt)
    elif mode == "pt":
        print(copyPrompt)
    elif mode in ("s", "ps"):
        copySummary = """Summarize in Spanish the main points found in the following tweets about {}: {}""".format(searchTerm, '\n'.join(tweets))
        if mode == "s":
            sendToGPT(copySummary)
        else:
            print(copySummary)
    elif mode.startswith("se"):
        if mode == "sep":
            executeSeleniumMode(copyPrompt)
        else:
            copySummary = """Summarize in Spanish the main points found in the following tweets about {}: {}""".format(searchTerm, '\n'.join(tweets))
            executeSeleniumMode(copySummary)

def executeMode(searchTerm, mode="tweet"):
    loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(loop)  # Set it as the current event loop
    loop.run_until_complete(searchTweetsAndCreatePrompt(searchTerm, mode))

def executeSeleniumMode(searchTerm):
    text_in_bmp = unidecode(searchTerm)
    # Replace new lines with spaces
    sanitized_text_in_bmp = text_in_bmp.replace('\n', ' ')

    # Copy the sanitized text to the clipboard
    pyperclip.copy(sanitized_text_in_bmp)

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    # Navigate to the Perplexity Labs playground
    driver.get("https://labs.perplexity.ai")

    # Wait for the textarea element to be available
    textarea = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.overflow-auto"))
    )

    # Click on the textarea to focus
    textarea.click()

    # Paste the text from the clipboard into the textarea
    textarea.send_keys(Keys.COMMAND, 'v')

    # Wait for the generate button to be clickable
    generate_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit'][type='button'][class*='bg-super']"))
    )

      # Select an option from the dropdown menu
    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "lamma-select"))
    )
    select = Select(dropdown_menu)
    select.select_by_visible_text("llama-3.1-70b-instruct")
    # select.select_by_visible_text("llama-3.1-sonar-large-128k-online")

    # Click the generate button
    generate_button.click()

    # Wait for the element to be available
    element = WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.XPATH, "//a[@role='button' and contains(@href, 'perplexity.ai/search')]"))
    )

    print('Ask found')
    # Wait for the response to be available
    responses = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.prose"))
    )

    # Wait for the copy button to be clickable
    copy_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/main/div/div/div[2]/div/div/div/div/div[3]/div/div/div[2]/button'))
    )

    try:
        copy_button.click()
        # Perform a sequence of actions
        actions = ActionChains(driver)
        actions.move_to_element(copy_button)
        actions.pause(1)  # wait for 1 second
        actions.click()
        actions.perform()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Get the response text
    # last_response = responses[-1]
    # print(last_response.text)
    print(pyperclip.paste())
    # pyperclip.copy(last_response.text)

    print("Press any key to end...")
    input()

    # Close the browser
    driver.quit()

def main():
    print("Select mode: s, t, se, sep")
    mode = input("Enter mode: ").lower()
    while mode not in ['s', 't', 'se', 'sep']:
        print("Invalid mode. Please select one of the following: s, t, se, sep")
        mode = input("Enter mode: ").lower()

    while True:
        search_term = input("\nEnter a search term (or type 'exit' to quit): ")
        if search_term.lower() == 'exit':
            break
        executeMode(search_term, mode)

if __name__ == "__main__":
    main()