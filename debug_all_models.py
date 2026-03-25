import os
import google.generativeai as genai
from dotenv import load_dotenv

# Use absolute path to .env if possible, or just configure manually for debug
load_dotenv(r"c:\Users\3cchozas\Downloads\ANTIGRAVITY\.env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found")
else:
    genai.configure(api_key=api_key)
    print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")
    try:
        with open("all_models.txt", "w", encoding="utf-8") as f:
            for m in genai.list_models():
                f.write(f"Name: {m.name}\n")
                f.write(f"Display Name: {m.display_name}\n")
                f.write(f"Supported Methods: {m.supported_generation_methods}\n")
                f.write("-" * 20 + "\n")
        print("Model list saved to all_models.txt")
    except Exception as e:
        print(f"Error: {e}")
