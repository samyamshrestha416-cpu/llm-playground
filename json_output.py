import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel , ValidationError

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Recipe(BaseModel):
    title: str
    ingredients: list[str]
    steps: list[str]

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="give a simple recipe for making a chocolate cake",
    config=types.GenerateContentConfig(
        system_instruction="You are a patient tutor. Explain with short example",
        temperature=0.7,
        response_mime_type="application/json",
        response_schema=Recipe,
    ),
)
print(response.text)

try:
    recipe = Recipe.model_validate_json(response.text)
    print(recipe.title)
    print(recipe.ingredients)
    print(recipe.steps)
except Exception as e:
    print("The model returned invalid data: ", e)