from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import tempfile
from pathlib import Path

# Existing imports
from app.ocr.ocr_space import extract_text_from_file
from app.schemas.ocr import OCRResult
from app.integrations.supabase_client import log_ocr_text
from app.parsers.llm_parser import parse_ocr_with_llm
from app.schemas.task import ParsedTask

# Your workflow import (actual one you use)
from app.graph.workflow import run_workflow


app = FastAPI(title="LifeAdmin AI")

# ------------------------------------------------------
# 1) Serve Frontend
# ------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """
    Serves the HTML UI.
    """
    with open("app/frontend/index.html", "r") as f:
        return f.read()


# ------------------------------------------------------
# 2) Existing endpoints (unchanged)
# ------------------------------------------------------
@app.get("/health")
def root():
    return {"message": "LifeAdmin AI backend is running"}


@app.post("/ocr-test", response_model=OCRResult)
async def test_ocr(file: UploadFile = File(...)):
    """
    Test OCR processing using OCR.Space.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    result = extract_text_from_file(temp_path)

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

    parsed = result["ParsedResults"][0]
    parsed_text = parsed.get("ParsedText", "")
    confidence = parsed.get("FileParseExitCode")

    log_ocr_text(parsed_text, result)

    return OCRResult(
        raw_text=parsed_text,
        confidence=confidence,
        full_response=result
    )


@app.post("/parse-test", response_model=ParsedTask)
async def test_parsing(ocr_text: str):
    """
    Test LLM-based OCR text → task parser.
    """
    return parse_ocr_with_llm(ocr_text)


# ------------------------------------------------------
# 3) Stage 11 — UI pipeline endpoint (CORRECTED)
# ------------------------------------------------------
@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    """
    UI upload → save to temp file → trigger existing run_workflow(file_path)
    """
    # Save upload to temp file (workflow expects a path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        # MATCHES YOUR test_pipeline() EXACTLY
        result = run_workflow(str(temp_path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "filename": file.filename,
        "result": result
    }
