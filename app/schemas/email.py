from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailPayload(BaseModel):
    to: EmailStr
    subject: str
    body: str
    sender: Optional[EmailStr] = "no-reply@lifeadmin.ai"
