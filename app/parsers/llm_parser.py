from groq import Groq
from app.core.config import settings
from app.schemas.task import ParsedTask
import json

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """
You are LifeAdmin AI, a document understanding and automation assistant.
Your job is to extract task-related information from noisy OCR text.

Your output MUST be valid JSON with the keys:
- task_type
- amount
- due_date
- provider
- reminder_days_before

If a field is missing or unclear, return null for it.
"""

def parse_ocr_with_llm(ocr_text: str) -> ParsedTask:
    prompt = f"""
Extract structured information from the following OCR text and return JSON only.

OCR TEXT:
{ocr_text}
"""
    response = client.chat.completions.create(
        model="llama3-8b-8192",   # Groq-hosted LLaMA
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    try:
        content = response.choices[0].message.content
        data = json.loads(content)
        return ParsedTask(
            task_type=data.get("task_type"),
            amount=data.get("amount"),
            due_date=data.get("due_date"),
            provider=data.get("provider"),
            reminder_days_before=data.get("reminder_days_before", 3),
            raw_text=ocr_text
        )
    except Exception as e:
        raise ValueError(f"LLM parsing failed: {str(e)}\nModel Output: {content}")
