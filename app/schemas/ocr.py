from pydantic import BaseModel

class OCRResult(BaseModel):
    raw_text: str
    confidence: float | None
    full_response: dict
