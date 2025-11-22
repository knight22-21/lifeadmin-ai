from groq import Groq
from app.core.config import settings
from app.schemas.task import ParsedTask
import json

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """
You are LifeAdmin AI, a document understanding and automation assistant.
Your job is to extract task-related information from noisy OCR text.

Your output MUST be valid JSON with EXACTLY these keys:
- task_type
- amount
- due_date
- provider
- reminder_days_before

RULES:
1. "task_type" MUST ALWAYS be a non-null string.
2. Allowed values for "task_type": "invoice", "receipt", "bill", "other".
3. If you are unsure, set "task_type" = "other". NEVER return null for task_type.
4. All other fields may be null if missing or unclear.
5. Return only the JSON. No extra text.
"""

def parse_ocr_with_llm(ocr_text: str) -> ParsedTask:
    prompt = f"""
Extract structured information from the following OCR text and return JSON only.

OCR TEXT:
{ocr_text}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)

        return ParsedTask(
            task_type=data.get("task_type"),  # now guaranteed non-null
            amount=data.get("amount"),
            due_date=data.get("due_date"),
            provider=data.get("provider"),
            reminder_days_before=data.get("reminder_days_before"),
            raw_text=ocr_text
        )

    except Exception as e:
        raise ValueError(f"LLM parsing failed: {str(e)}\nModel Output: {content}")
