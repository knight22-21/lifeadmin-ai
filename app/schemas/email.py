from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailPayload(BaseModel):
    to: EmailStr
    subject: str
    body: str
    sender: Optional[EmailStr] = "studyjamgenai33@gmail.com"

