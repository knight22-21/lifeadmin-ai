from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class LogEntry(BaseModel):
    stage: str                      
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
