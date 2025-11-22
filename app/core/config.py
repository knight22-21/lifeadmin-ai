import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY")
    TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
    ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
    ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL")
    DEFAULT_USER_TIMEZONE = os.getenv("DEFAULT_USER_TIMEZONE")

settings = Settings()
