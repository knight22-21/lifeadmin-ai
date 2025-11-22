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


# Export global client for imports elsewhere
supabase_client = SupabaseClient()


# -----------------------------------------
# Existing OCR Logging Function (kept)
# -----------------------------------------

def log_ocr_text(raw_text: str, full_response: dict):
    """
    Stores OCR result in Supabase (existing behavior).
    """
    data = {
        "raw_text": raw_text,
        "full_response": full_response
    }

    # Use the new global client
    supabase_client.table("ocr_logs").insert(data).execute()


