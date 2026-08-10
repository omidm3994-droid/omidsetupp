import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def ai_generate_text(prompt):
    response = model.generate_content(prompt)
    return response.text

def ai_generate_image(prompt):
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "image/png"}
    )
    return response
