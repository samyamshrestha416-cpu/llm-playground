import os, time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq

load_dotenv()
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GEMINI_MODEL = "gemini-3.5-flash-lite"
GROQ_MODEL = "openai/gpt-oss-120b"

def chat_gemini(messages, system ,temperature):
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["text"])],
        )
        for m in messages
    ]
    r = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, temperature=temperature),
    )
    u = r.usage_metadata
    return r.text, u.prompt_token_count, u.candidates_token_count

def chat_groq(messages , system ,temperature):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs += [{"role": m["role"], "content": m["text"]} for m in messages]
    r = groq_client.chat.completions.create(
        model=GROQ_MODEL, messages=msgs, temperature=temperature
    )
    return r.choices[0].message.content, r.usage.prompt_tokens, r.usage.completion_tokens

def chat(provider, messages, system=None, temperature=0.7):
    start = time.perf_counter()
    if provider == "gemini":
        text, t_in, t_out = chat_gemini(messages, system, temperature)
    elif provider == "groq":
        text, t_in, t_out = chat_groq(messages, system, temperature)
    else:
        raise ValueError(f"Unknown provider: {provider}")
    return {"text": text, "in": t_in, "out": t_out, "seconds": time.perf_counter() - start}

if __name__ == "__main__":
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else "gemini"
    history = []
    while True:
        text = input("YOU: ")
        if text.lower() == "quit":
            break
        history.append({"role": "user", "text": text})
        try:
            r = chat(provider, history, system="You are a patient tutor.")
        except Exception as e:
            print(f"Error ({type(e).__name__}): {e}")
            history.pop()
            continue
        print("AI:", r["text"])
        history.append({"role": "assistant", "text": r["text"]})
        print(f"[{provider}] in: {r['in']} | out: {r['out']} | {r['seconds']:.2f}s")