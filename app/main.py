from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
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
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    # Call OCR.Space API
    result = extract_text_from_file(temp_path)

    # --- Robust error handling ---
    if result.get("IsErroredOnProcessing"):
        raise HTTPException(
            status_code=400,
            detail={
                "message": "OCR.Space returned an error",
                "error": result.get("ErrorMessage"),
                "details": result
            }
        )

    if "ParsedResults" not in result:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "OCR.Space response missing ParsedResults",
                "details": result
            }
        )

    # Extract text
    parsed = result["ParsedResults"][0]
    parsed_text = parsed.get("ParsedText", "")
    confidence = parsed.get("FileParseExitCode")

    # Store log in Supabase
    log_ocr_text(parsed_text, result)

    return OCRResult(
        raw_text=parsed_text,
        confidence=confidence,
        full_response=result
    )
