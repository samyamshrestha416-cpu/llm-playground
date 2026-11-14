LLM Playground

demo

A terminal chatbot that talks to Google's Gemini API directly, with no LangChain or other framework. I built it to understand what really happens when you call an LLM API: how messages are sent, how streaming works, what tokens are, and what goes wrong.

Features
Chat with memory. The API remembers nothing, so the program sends the whole conversation on every call.
Streaming replies. Answers appear word by word as Gemini writes them.
System prompt and temperature. Control the model's role and how random its answers are.
Token counts. Every reply is followed by the input, output, and total tokens used.
Retries with exponential backoff. Temporary failures (rate limits, server errors, lost connection) are retried after 1, 2, then 4 seconds, plus a little random jitter. The program never retries after part of an answer has been printed.
Structured JSON output. The /json command returns a recipe as validated data using Pydantic.
Command-line options. Choose the model and temperature when you start the program.
Setup
Install uv.
Clone this repo and install the libraries:
bash
git clone https://github.com/YOUR_USERNAME/llm-playground.git
cd llm-playground
uv sync
Get a free API key from Google AI Studio.
Create a file named .env in the project folder with one line:
GEMINI_API_KEY=your_key_here

Never commit this file. It is already listed in .gitignore.

Run
bash
uv run main.py
uv run main.py --temperature 0
uv run main.py --model gemini-3.5-flash-lite --temperature 1.2
uv run main.py --help

Model names change over time. If you get a "model not found" error, copy a current name from the Gemini docs.

Chat commands
Command	What it does
/json <dish>	Returns a recipe as structured data (title, ingredients, steps)
/clear	Clears the conversation history, so the model forgets earlier messages
quit	Exits the program
Project files
File	Purpose
main.py	The chat loop, streaming, retries, token counts, and commands
schemas.py	The Pydantic Recipe model used for JSON output
.env	Your secret API key (not committed)
What I learned
The API has no memory. The model only knows what I send in each request, so the history list has to be sent every time. That is also why the input token count grows with every message.
Tokens decide cost. Long conversations cost more because the whole history is sent again each turn.
Temperature changes variety, not intelligence. At 0 the answers are steady and almost repeatable. At 1.5 they vary a lot.
Streaming needs care. The full reply has to be collected piece by piece before saving it to history, and token counts come from the last chunk.
Retry only what can recover. Rate limits and server errors are worth retrying. Bad keys and bugs in my own code are not. With Wi-Fi off, the error is not an API error at all, because Google never replies.
Indentation is logic in Python. One misplaced break inside the streaming loop cut every answer to one word and caused a confusing NameError.
Structured output. Describing the shape with a Pydantic class and validating the result means bad model output is caught instead of crashing the program.
Next

This is Project 1 of a series on building AI applications. Next I will turn this into a FastAPI service with streaming endpoints, login, rate limiting, and caching.
