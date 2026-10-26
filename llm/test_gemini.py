import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=(
        "You are a legacy modernization engineer. "
        "Explain in three sentences why dependency "
        "analysis is important before migrating a "
        "SQL Server table."
    )
)

print("\n=== GEMINI RESPONSE ===")
print(response.text)
