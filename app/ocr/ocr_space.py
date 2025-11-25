import requests
from app.core.config import settings
from app.utils.retry import retry

OCR_API_URL = "https://api.ocr.space/parse/image"


@retry(max_attempts=3, delay=2, backoff=2)
def extract_text_from_file(file_path: str) -> str:
    """
    Sends a file to OCR.Space API with retries and returns extracted text.
    Adds:
    - retry logic
    - explicit error handling
    - standardized failure messages
    """
    try:
        with open(file_path, "rb") as f:
            payload = {
                "apikey": settings.OCR_SPACE_API_KEY,
                "language": "eng",
                "isOverlayRequired": False,
            }

            response = requests.post(
                OCR_API_URL,
                files={"filename": f},
                data=payload,
                timeout=20  # prevent hanging
            )

        if response.status_code != 200:
            raise RuntimeError(f"OCR API Error: {response.text}")

        data = response.json()

        # Validate OCR response structure
        if not data.get("ParsedResults"):
            raise ValueError("OCR failed: No ParsedResults returned")

        return data["ParsedResults"][0].get("ParsedText", "")

    except Exception as e:
        # Wrap any errors with a clear message for LangGraph
        raise RuntimeError(f"OCR extraction failed: {e}")
