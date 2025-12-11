import json
import re
from ollama import Client

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

def sql_query_ollama_with_client(prompt: str, model: str):
    from ollama import Client
    client = Client()

    response = client.chat(model=model, messages=[
        {"role": "user", "content": prompt}
    ])

    raw_output = response["message"]["content"].strip()

    # Debug print (optional)
    # print("RAW OLLAMA OUTPUT:", raw_output)

    # Try to parse JSON safely


    # try:
    #     model_json = json.loads(raw_output)
    # except Exception:
    #     # LLM returned invalid JSON — fallback format
    #     return {
    #         "query": "",
    #         "confidence": 0.0,
    #         "tokens": 0,
    #         "error": "Model returned invalid JSON",
    #         "raw_output": raw_output
    #     }

    parsed = extract_json(raw_output)

    if parsed is None:
        return {
            "query": "",
            "confidence": 0.0,
            "tokens": 0,
            "raw_output": raw_output,
            "error": "Invalid JSON returned"
        }

    # Ensure required fields exist
    return {
        "query": parsed.get("query", ""),
        "confidence": parsed.get("confidence", 0.0),
        "Sent_tokens": response.get("prompt_eval_count", 0),  # ollama token count
        "Generated_tokens": response.get("eval_count", 0)  # ollama token count

        # "raw_output":raw_output
    }

    # Ensure required fields exist
    return {
        "insight": parsed.get("insight", ""),
        "implication": parsed.get("implication", ""),
        "suggestions": parsed.get("suggestions", []),
        "evidence": parsed.get("evidence", []),
        "confidence": parsed.get("confidence", 0.0),
        "sent_tokens": response.get("prompt_eval_count", 0),  # ollama token count
        "generated_tokens": response.get("eval_count", 0)  # ollama token count

        # "raw_output":raw_output
    }



def text_query_ollama_with_client(prompt: str, model: str):
    
    client = Client()

    response = client.chat(model=model, messages=[
        {"role": "user", "content": prompt}
    ])

    raw_output = response["message"]["content"].strip()

    # Debug print (optional)
    # print("RAW OLLAMA OUTPUT:", raw_output)

    # Try to parse JSON safely


    # try:
    #     model_json = json.loads(raw_output)
    # except Exception:
    #     # LLM returned invalid JSON — fallback format
    #     return {
    #         "query": "",
    #         "confidence": 0.0,
    #         "tokens": 0,
    #         "error": "Model returned invalid JSON",
    #         "raw_output": raw_output
        # }

    parsed = extract_json(raw_output)

    if parsed is None:
        return {
            "insight": "",
            "implication": "",
            "suggestions": [],
            "evidence": [],
            "confidence": 0.0,
            "sent_tokens": 0,
            "generated_tokens": 0
        }

    # Ensure required fields exist
    return {
        "insight": parsed.get("insight", ""),
        "implication": parsed.get("implication", ""),
        "suggestions": parsed.get("suggestions", []),
        "evidence": parsed.get("evidence", []),
        "confidence": parsed.get("confidence", 0.0),
        "sent_tokens": response.get("prompt_eval_count", 0),  # ollama token count
        "generated_tokens": response.get("eval_count", 0)  # ollama token count

        # "raw_output":raw_output
    }


