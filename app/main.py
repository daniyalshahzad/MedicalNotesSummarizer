from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses     import FileResponse
import os
from .feedback_file import save_feedback
from .models import SummarizeRequest, SummarizeResponse, FeedbackRequest, FeedbackRequest, SummarySchema
from typing import List

from .summarizer import generate_summary

# --- configure logging for the API ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- instantiate FastAPI ---
app = FastAPI(title="Medical Summarization API")

# 1) Mount your JS/CSS/etc under /static
app.mount(
    "/static",
    StaticFiles(directory=os.path.join("app", "static")),
    name="static"
)

# # --- request/response schemas ---
# class SummarizeRequest(BaseModel):
#     text: str

# class SummarizeResponse(BaseModel):
#     summary: str

# class FeedbackRequest(BaseModel):
#     request_id: str
#     feedback: str

# class FeedbackRequest(BaseModel):
#     request_id: str
#     feedback: str

# class SummarySchema(BaseModel):
#     summary: str
#     key_illnesses: List[str]
#     past_treatments: List[str]
#     current_medications: List[str]
#     recommended_plan: str

@app.get("/health")
def health():
    return {"status": "ok"}

# 2) Serve index.html at the root
@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse(os.path.join("app", "static", "index.html"))

@app.post("/summarize")
def summarize(req: SummarizeRequest):

    if not req.text.strip():
        raise HTTPException(400, "Input text is empty")
    
    try:
        summary = generate_summary(req.text)

    except ValueError as ve:
        # our own guard for empty text
        raise HTTPException(status_code=400, detail=str(ve))
    
    except RuntimeError as re:
        # wrapping OpenAI errors
        logger.error("Error in summarizer: %s", re)
        raise HTTPException(status_code=502, detail="Summarization service unavailable")
    
    return {"summary": summary}

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    """
    Collect user feedback on a summary and persist it to a JSONL file.
    """
    try:
        if not req.feedback.strip():
            raise HTTPException(status_code=400, detail="Feedback cannot be empty")
        save_feedback(req.request_id, req.feedback)
    except OSError as e:
        logger.error("Failed to write feedback: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Unable to record feedback at this time"
        )
    return {"message": "Feedback recorded", "request_id": req.request_id}