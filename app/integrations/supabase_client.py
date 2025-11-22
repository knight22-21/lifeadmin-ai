from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def log_ocr_text(raw_text: str, full_response: dict):
    """
    Stores OCR result in Supabase.
    """
    data = {
        "raw_text": raw_text,
        "full_response": full_response
    }
    supabase.table("ocr_logs").insert(data).execute()
