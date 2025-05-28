from pydantic import BaseModel
from typing import List

# --- request/response schemas ---
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str

class FeedbackRequest(BaseModel):
    request_id: str
    feedback: str

class FeedbackRequest(BaseModel):
    request_id: str
    feedback: str

class SummarySchema(BaseModel):
    summary: str
    key_illnesses: List[str]
    past_treatments: List[str]
    current_medications: List[str]
    recommended_plan: str