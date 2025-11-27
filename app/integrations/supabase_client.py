from supabase import create_client, Client
from app.core.config import settings


class SupabaseClient:
    """
    Reusable Supabase client.
    """
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )

    def table(self, name: str):
        return self.client.table(name)


supabase_client = SupabaseClient()


def safe_log(stage: str, input_data=None, output_data=None, error=None):
    """
    Safe logging wrapper that never raises exceptions.
    """
    try:
        supabase_client.table("logs").insert({
            "stage": stage,
            "input_data": input_data,
            "output_data": output_data,
            "error": str(error) if error else None
        }).execute()
    except Exception:
        print("Warning: Logging failure – continuing workflow.")


def log_ocr_text(raw_text: str, full_response: dict):
    """
    Stores OCR results using safe logging.
    """
    try:
        supabase_client.table("ocr_logs").insert({
            "raw_text": raw_text,
            "full_response": full_response
        }).execute()
    except Exception:
        print("Warning: OCR logging failure – continuing workflow.")
