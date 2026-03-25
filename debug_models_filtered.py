import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    print("Searching for Gemini 1.5 models...")
    try:
        found = False
        for m in genai.list_models():
            if '1.5' in m.name or 'flash' in m.name:
                print(f"Name: {m.name}")
                print(f"Supported Methods: {m.supported_generation_methods}")
                print("-" * 20)
                found = True
        if not found:
            print("No Gemini 1.5 or Flash models found.")
    except Exception as e:
        print(f"Error: {e}")
