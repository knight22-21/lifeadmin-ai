from supabase import create_client, Client
from app.core.config import settings


# -----------------------------------------
# Create reusable Supabase client instance
# -----------------------------------------

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )

    def table(self, name: str):
        """
        Provides access to any Supabase table.
        """
        return self.client.table(name)


# Global client
supabase_client = SupabaseClient()


# -----------------------------------------
# NEW: Stage 10 - Safe Logging Wrapper
# -----------------------------------------

def safe_log(stage: str, input_data=None, output_data=None, error=None):
    """
    Robust logging function:
    - Never throws exceptions
    - Ensures logging failure does not break workflow
    - Converts errors to strings
    """
    try:
        supabase_client.table("logs").insert({
            "stage": stage,
            "input_data": input_data,
            "output_data": output_data,
            "error": str(error) if error else None
        }).execute()

    except Exception:
        # We do NOT crash pipeline if Supabase is down
        print("Warning: Logging failure – continuing workflow.")


# -----------------------------------------
# Existing OCR Logging Function — UPDATED to safe logging
# -----------------------------------------

def log_ocr_text(raw_text: str, full_response: dict):
    """
    Stores OCR result in Supabase (now using safe logging).
    """
    try:
        supabase_client.table("ocr_logs").insert({
            "raw_text": raw_text,
            "full_response": full_response
        }).execute()

    except Exception:
        print("Warning: OCR logging failure – continuing workflow.")
