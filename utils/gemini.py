from google.genai import Client
import os

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt):
    response = client.models.generate(
        model="gemini-1.5-flash",
        prompt=prompt
    )
    return response.text
