import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# 1. Load the keys from your hidden .env file into memory
load_dotenv()

# 2. Extract the credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

print("Attempting to connect to your Azure AI Foundry model...")

# 3. Initialize the Azure OpenAI Client
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version="2024-06-01"
)

# 4. Send a tiny test message to your 'gpt-4o' deployment
try:
    response = client.chat.completions.create(
        model="gpt-4o",  # This must match your deployment name in the portal
        messages=[
            {"role": "user", "content": "Hello brain! Confirm you can read this message."}
        ],
        max_tokens=20
    )
    print("\n--- Success! Azure Response ---")
    print(response.choices[0].message.content.strip())

except Exception as e:
    print("\n--- Connection Error ---")
    print(f"Something went wrong: {e}")