import os
import time, random #eroor and retryes
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors
from schemas import Recipe
from pydantic import ValidationError


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#same thing in every
parser = argparse.ArgumentParser(description="Terminal chatbot using Gemini")
parser.add_argument("--model", default="gemini-3.5-flash-lite")
parser.add_argument("--temperature", type=float, default=0.7)
args = parser.parse_args()

print(f"model: {args.model} | temperature: {args.temperature}")
print("Commands: /json <dish>   /clear   quit")
#
history = []

while True:
    user_text = input("YOU: \n")
    if user_text.lower() == "quit":
        break
    if user_text.strip()=="/clear":
        history.clear()
        print("history cleared")
        continue
    if not user_text.strip(): # not neceesary
        continue
    #JSON output for recipe request
    if user_text.startswith("/json"):
        recipe_request = user_text[len("/json"):]
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=f"give a simple recipe for {recipe_request}",
                config=types.GenerateContentConfig(
                    system_instruction="You are a patient tutor. Explain with short example",
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=Recipe,
                ),
            )
            recipe = Recipe.model_validate_json(response.text)
            print(recipe.title)
            print(recipe.ingredients)
            print(recipe.steps)
            history.append(types.Content(role="user", parts=[types.Part(text=recipe_request)]))
            history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
            
        except Exception as e:
            print("The model returned invalid data: ", e)
        continue #continue le garda json wala code history ma save hunna 
                    #edi continue vayena vane json paxi ko kura sab history ma janxa jun naramro hunxa        
            #end
    else:
        history.append(types.Content(role="user", parts=[types.Part(text=user_text)]))
 
#system prompt and temperature for the model
    config = types.GenerateContentConfig(
        system_instruction="You are a patient tutor." ,
        temperature=args.temperature,
    )
#end of system prompt and temperature for the model

#Streaming response from the model # 1-1 word gardai ans aune
#error handling and retryes for the model    
    max_retries = 4
    last = None   #count tokens for the model
    full_reply = ""
    ok = False

    for attempt in range(max_retries): #error
        try:
            print("AI:")
            for chunk in client.models.generate_content_stream(
               model="gemini-3.5-flash-lite",
               contents=history,
               config=config,
           ):
               last = chunk  #count tokens for the model
               piece = chunk.text or ""
               print(piece, end="", flush=True)
               full_reply += piece
            print()
            ok = True
            break
        except errors.APIError as e: #error
            temporary = e.code in (429, 500, 503)
            message = f"API error {e.code}: {e.message}"
        except Exception as e:
            temporary = True
            message = f"connection problem: {e}"

        print(message)
        if full_reply or not temporary or attempt == max_retries - 1:   
            break 
        wait = 2 ** attempt + random.random()
        print(f"Retrying in {wait:.1f}s...")
        time.sleep(wait)

    if full_reply:
       history.append(types.Content(role="model", parts=[types.Part(text=full_reply)]))
#Streaming end code
#token count for the model
       u = last.usage_metadata if last else None  #count tokens for the model
       if u:
           print(f"in_token :{u.prompt_token_count} out_token :{u.candidates_token_count} total_token_used :{u.total_token_count}")
#ending of token count for the model
    elif history:
        history.pop()  # remove the last user message if no reply was generated