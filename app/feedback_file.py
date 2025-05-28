
import os
import json
from datetime import datetime
from .utils import BASE_DIR

FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.jsonl")

def save_feedback(request_id: str, feedback: str):
    """
    Append a feedback entry as a JSON line to FEEDBACK_FILE.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "feedback": feedback
    }
    # Ensure the file exists and append
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
