# Tweet and Summary Generator

This Python script allows you to generate tweets and summaries based on Twitter search results and language models (LLMs). It supports both the OpenAI API and automating data retrieval from online playgrounds.

## Dependencies

Make sure you have the following dependencies installed:
- `openai` (Install via `pip install openai`)
- `asyncio`
- `selenium` (Install via `pip install selenium`)
- `twscrape` (Install via `pip install twscrape`)
- `unidecode` (Install via `pip install unidecode`)
- `pyperclip` (Install via `pip install pyperclip`)

Additionally, you need to have the appropriate web driver installed for Selenium. In this script, it's set up to use Chrome, so you'll need Chrome WebDriver.

## Usage

1. Ensure you have environment variables set up in a `.env` file for:
   - `OPENAI_API_KEY`
   - `TWSCRAPE_USERNAME`
   - `TWSCRAPE_PASSWORD`
   - `TWSCRAPE_EMAIL`
   - `TWSCRAPE_API_KEY`

2. Call the `executeMode()` function with the appropriate parameters:
   - `searchTerm`: The topic you want to search for on Twitter.
   - `mode`: The mode of operation, which can be:
     - `"tweet"`: Generates a tweet based on the provided trusted tweets.
     - `"s"`: Generates a tweet and copies it to the clipboard.
     - `"pt"`: Prints the tweet prompt without generating.
     - `"selenium"`: Uses Selenium to interact with an online playground to generate a summary.
     - `"seleniump"`: Uses Selenium to generate a summary and copies it to the clipboard.
     - `"ps"`: Generates a summary prompt and copies it to the clipboard.

## Example

```python
executeMode("Artificial Intelligence", mode="selenium")
```

This example searches for tweets related to "Artificial Intelligence" and generates a summary using Selenium, interacting with an online playground.

## Note

Ensure you have proper permissions and adhere to API usage policies when using third-party services like Twitter and OpenAI.