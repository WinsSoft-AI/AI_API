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
    ], keep_alive='5m')

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
        # User prompt requests RAW SQL, so parsing will fail.
        # Fallback: Treat the entire stripped output as the query.
        # Use regex to robustly remove markdown code blocks (e.g. ```sql, ```)
        cleaned_sql = re.sub(r"```.*?", "", raw_output, flags=re.DOTALL).strip()
        cleaned_sql = cleaned_sql.replace("`", "") # Remove any remaining backticks
        
        return {
            "query": cleaned_sql,
            "confidence": 0.8, # Assume reasonable confidence if fallback triggered
            "Sent_tokens": response.get("prompt_eval_count", 0),
            "Generated_tokens": response.get("eval_count", 0),
            "raw_output": raw_output
        }

    # Ensure required fields exist
    return {
        "query": parsed.get("query", ""),
        # "confidence": parsed.get("confidence", 0.0),
        "Sent_tokens": response.get("prompt_eval_count", 0),
        "Generated_tokens": response.get("eval_count", 0)
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
            "greeting": "",
            "suggestions": [],
            "evidence": [],
            # "confidence": 0.0,
            "sent_tokens": 0,
            "generated_tokens": 0
        }

    # Ensure required fields exist
    return {
        "insight": parsed.get("insight", ""),
        "greeting": parsed.get("greeting", ""),
        "suggestions": parsed.get("suggestions", []),
        "evidence": parsed.get("evidence", []),
        # "confidence": parsed.get("confidence", 0.0),
        "sent_tokens": response.get("prompt_eval_count", 0),  # ollama token count
        "generated_tokens": response.get("eval_count", 0)  # ollama token count

        # "raw_output":raw_output
    }


