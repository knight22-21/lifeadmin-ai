from pydantic import BaseModel
from datetime import date

class ParsedTask(BaseModel):
    task_type: str
    amount: str | None = None
    due_date: date | None = None
    provider: str | None = None
    reminder_days_before: int | None = 3  # default 3-day reminder
    raw_text: str                         # Include original OCR text
