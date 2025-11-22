from app.integrations.supabase_client import supabase_client
from app.schemas.log import LogEntry

class SupabaseLogger:
    TABLE_NAME = "logs"

    @staticmethod
    def log(entry: LogEntry):
        result = supabase_client.table(SupabaseLogger.TABLE_NAME).insert(entry.dict()).execute()
        return result
