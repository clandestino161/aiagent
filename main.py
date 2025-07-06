import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def main():
    if len(sys.argv) < 2:
        print("No prompt provided")
        exit(1)
    elif "--verbose" in sys.argv:
        user_prompt = " ".join([arg for arg in sys.argv[1:] if arg != "--verbose"])
        messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)]),]
        response = client.models.generate_content(model="gemini-2.0-flash-001", contents=messages)
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(response.text)
    else:
        user_prompt = " ".join([arg for arg in sys.argv[1:] if arg != "--verbose"])
        messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)]),]
        response = client.models.generate_content(model="gemini-2.0-flash-001", contents=messages)
        print(response.text)

if __name__ == "__main__":
    main()
