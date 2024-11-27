import os
from dotenv import load_dotenv
import requests

buffer_years=2
load_dotenv()
OPENROUTER_API_KEY2 = os.getenv('OPENROUTER_API_KEY2') # <-- Put your API key here
def tweet(query):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY2}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
            },
            json={
                "model": "meta-llama/llama-3.2-90b-vision-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "quiero generar tweets para una uniiversidad, que te-nga emojis pero moderados y relacionados al tema no los sobreuses, que solo regrese el tweet sin la instruccion"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1
            }
        )
        
        result = response.json()
        if 'error' in result:
            return f"Error: {result['error']}"
            
        date = result['choices'][0]['message']['content'].strip()
        return date

    except Exception as e:
        return f"Error: {str(e)}"