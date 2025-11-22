from app.integrations.supabase_client import supabase_client
from app.schemas.log import LogEntry

class SupabaseLogger:
    TABLE_NAME = "logs"

    @staticmethod
    def log(entry: LogEntry):
        data = entry.dict()

        # FIX: convert datetime → ISO string
        if "timestamp" in data:
            data["timestamp"] = data["timestamp"].isoformat()

        return supabase_client.table(SupabaseLogger.TABLE_NAME).insert(data).execute()
