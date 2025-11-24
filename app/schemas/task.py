from pydantic import BaseModel, field_validator

class ParsedTask(BaseModel):
    task_type: str
    amount: str | int | None = None
    due_date: str | None = None
    provider: str | None = None
    reminder_days_before: int | None = 3  # default 3-day reminder
    raw_text: str                         # Include original OCR text
    email: str = "americaitalybelgium111@gmail.com"  # Default email if none provided

    @field_validator("amount", mode="before")
    def cast_amount_to_str(cls, v):
        if v is None:
            return v
        return str(v)

