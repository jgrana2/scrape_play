import os
from dotenv import load_dotenv
import openai
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
    print("\nTrends copied to clipboard!")