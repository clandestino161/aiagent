import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import get_files_info, schema_get_files_info

# Create the tool using genai.types.Tool, not a separate import
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

available_functions = types.Tool(
    function_declarations=[schema_get_files_info]
)

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, verbose)

def generate_content(client, messages, verbose):
    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    # Check for function calls at the response level first
    if hasattr(response, 'function_calls') and response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")

            # Manually call the right function
            if function_call.name == "get_files_info":
                directory = function_call.args.get("directory", None)
                result = get_files_info("calculator", directory)  # <-- set your working dir
                print("\nFunction result:\n" + result)
            else:
                print("Unknown function.")
        return  # Exit early since we handled the function call

    # If no function calls at response level, check the parts
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                print(f"Calling function: {function_call.name}({function_call.args})")

                # Manually call the right function
                if function_call.name == "get_files_info":
                    directory = function_call.args.get("directory", None)
                    result = get_files_info("calculator", directory)  # <-- set your working dir
                    print("\nFunction result:\n" + result)
                else:
                    print("Unknown function.")
                return  # Exit early since we handled the function call
            elif hasattr(part, 'text') and part.text:
                print("Response:")
                print(part.text)
    else:
        print("No output produced.")

if __name__ == "__main__":
    main()
