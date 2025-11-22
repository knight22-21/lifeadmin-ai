import requests
from app.core.config import settings

OCR_API_URL = "https://api.ocr.space/parse/image"

def extract_text_from_file(file_path: str) -> dict:
    """
    Sends file to OCR.Space API and returns OCR results.
    """
    with open(file_path, 'rb') as f:
        payload = {
            'apikey': settings.OCR_SPACE_API_KEY,
            'language': 'eng',
            'isOverlayRequired': False
        }

        response = requests.post(
            OCR_API_URL,
            files={'filename': f},
            data=payload
        )

    if response.status_code != 200:
        raise Exception(f"OCR API Error: {response.text}")

    return response.json()
