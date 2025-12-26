import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_groq_key():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in environment.")
        sys.exit(1)

    print(f"Checking Groq API Key: {api_key[:5]}...{api_key[-4:]}")

    try:
        client = Groq(api_key=api_key)
        
        # List available models
        print("Fetching available models...")
        models = client.models.list()
        available_model_ids = [m.id for m in models.data]
        print(f"Available models: {available_model_ids}")

        # Choose a model (prefer llama-3.3, then others)
        selected_model = next((m for m in available_model_ids if "llama-3.3" in m), None)
        if not selected_model:
             selected_model = next((m for m in available_model_ids if "llama" in m), available_model_ids[0])
        
        print(f"Testing with model: {selected_model}")

        # Simple request to verify connectivity and auth
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            model=selected_model,
            max_tokens=10,
        )
        print("✅ Success! Groq API responded.")
        print(f"Response: {chat_completion.choices[0].message.content}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to connect to Groq API: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    verify_groq_key()
