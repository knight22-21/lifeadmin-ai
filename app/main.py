from fastapi import FastAPI
from fastapi import UploadFile, File
from app.ocr.ocr_space import extract_text_from_file
from app.schemas.ocr import OCRResult
from app.integrations.supabase_client import log_ocr_text
import tempfile

app = FastAPI(title="LifeAdmin AI")

@app.get("/")
def root():
    return {"message": "LifeAdmin AI backend is running"}


@app.post("/ocr-test", response_model=OCRResult)
async def test_ocr(file: UploadFile = File(...)):
    # Save uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    result = extract_text_from_file(temp_path)

    parsed_text = result['ParsedResults'][0]['ParsedText']
    confidence = result['ParsedResults'][0].get('FileParseExitCode')

    # Store OCR log
    log_ocr_text(parsed_text, result)

    return OCRResult(
        raw_text=parsed_text,
        confidence=confidence,
        full_response=result
    )
