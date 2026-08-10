from google.genai import Client
import os

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
#   TEXT GENERATION
# -----------------------------
def ai_generate_text(prompt: str) -> str:
    response = client.models.generate(
        model="gemini-1.5-flash",
        prompt=prompt
    )
    return response.text


# -----------------------------
#   IMAGE GENERATION
# -----------------------------
def ai_generate_image(prompt: str) -> bytes:
    response = client.models.generate(
        model="gemini-1.5-flash",
        prompt=prompt,
        output="image"
    )
    return response.image
