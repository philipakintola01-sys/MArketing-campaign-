import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    print(f"Testing Groq with Model: {model}")
    print(f"API Key present: {'Yes' if api_key and 'your' not in api_key else 'No'}")
    
    if not api_key or 'your' in api_key:
        print("ERROR: GROQ_API_KEY is either missing or still set to placeholder in .env")
        return

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, are you online?"}],
        )
        print("SUCCESS: Groq replied!")
        print(f"Response: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_groq()
