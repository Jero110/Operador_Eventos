import os
from dotenv import load_dotenv
import requests

# Load the environment variables from a .env file
load_dotenv()

# Fetch the OpenAI API key from the environment
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("No API key found. Please set OPENAI_API_KEY in your environment variables.")

def tweet(query: str) -> str:
    try:
        # Ensure the API key exists
        if not API_KEY:
            return "Error: No API key available"

        # Make a POST request to OpenAI's API
        response = requests.post(
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4-turbo",  # Use GPT-4 turbo (mini version, if applicable)
                "messages": [
                    {
                        "role": "system",
                        "content": "Generate tweets for a university. Include emojis related to the topic but use them moderately. Return only the tweet without instructions."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1
            }
        )
        
        # Parse the JSON response
        result = response.json()
        if response.status_code != 200:
            error_message = result.get("error", {}).get("message", "Unknown error")
            return f"Error: {error_message}"
            
        # Extract and return the tweet content
        return result['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"Error: {str(e)}"
