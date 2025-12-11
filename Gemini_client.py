import json
import re
from google import genai
from config import GEMINI_API_KEY

# Assumes you have set the GEMINI_API_KEY environment variable
# If not, you can pass the api_key to the Client constructor: 
client = genai.Client(api_key=GEMINI_API_KEY)

client = genai.Client()

def extract_json(text: str):
    """
    Extract JSON from LLM output. Supports extra text, markdown, or partial wrapping.
    """
    # Find first { and last }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None  # No JSON found

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except Exception:
        return None


def sql_query_gemini(prompt: str, model: str = "gemini-2.5-flash"):
    """
    Queries the Gemini API with the given prompt and extracts a structured JSON response.
    """
    # The API expects a list of parts or a single string
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    raw_output = response.text.strip()

    # Debug print (optional)
    # print("RAW GEMINI OUTPUT:", raw_output)

    parsed = extract_json(raw_output)

    if parsed is None:
        return {
            "query": "",
            "confidence": 0.0,
            # Gemini API response object has different usage metadata access
            "tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
            "raw_output": raw_output,
            "error": "Invalid JSON returned or JSON structure missing required keys"
        }

    # Ensure required fields exist in the parsed JSON
    return {
        "query": parsed.get("query", ""),
        "confidence": parsed.get("confidence", 0.0),
        # Access token counts from the response object metadata
        "Sent_tokens": None,
        "genrated_tokens": None
    }


def text_query_gemini(prompt: str, model: str = "gemini-2.5-flash"):
    """
    Queries the Gemini API with the given prompt and extracts a structured JSON response.
    """
    # The API expects a list of parts or a single string
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    raw_output = response.text.strip()

    # Debug print (optional)
    # print("RAW GEMINI OUTPUT:", raw_output)

    parsed = extract_json(raw_output)

    if parsed is None:
        return {
            "insight": "",
            "implication": "",
            "suggestions": ["", "", ""],
            "evidence": [],
            "confidence": 0.0
        }

    # Ensure required fields exist in the parsed JSON
    return {
        "insight": parsed.get("insight", ""),
        "implication": parsed.get("implication", ""),
        "suggestions": parsed.get("suggestions", ["", "", ""]),
        "evidence": parsed.get("evidence", []),
        "confidence": parsed.get("confidence", 0.0),
        "sent_tokens": getattr(response.usage, "prompt_tokens", 0),
        "generated_tokens": getattr(response.usage, "total_tokens", 0)
    }