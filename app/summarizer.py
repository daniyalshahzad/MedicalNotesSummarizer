from openai import OpenAI, OpenAIError
import logging
import json
from pydantic import ValidationError

from .utils import OPENAI_KEY, MODEL_NAME, prettify_output
from .models import SummarySchema

CLIENT = OpenAI(api_key=OPENAI_KEY)

logger = logging.getLogger(__name__)

def generate_summary(text: str) -> str:

    if not text.strip():
        raise ValueError("Cannot summarize empty text")

    system_msg = (
        "You are a medical summarization assistant. "
        "When given a clinical note, reply with JSON only—no markdown or extra commentary."
    )

    user_msg = (
        f"Clinical note:\n\n{text}\n\n"
        "Please generate a JSON object with exactly these keys:\n"
        "```json\n"
        "{\n"
        '  "summary": "A concise paragraph overview of the patient case",\n'
        '  "key_illnesses": ["Diagnosis1", "Diagnosis2"],\n'
        '  "past_treatments": ["Treatment1", "Treatment2"],\n'
        '  "current_medications": ["Med1", "Med2"],\n'
        '  "recommended_plan": "Next steps or plan"\n'
        "}\n"
        "```\n"
        "Respond with VALID JSON only, matching this structure exactly."
    )
    try:

        response = CLIENT.responses.create(
        model= MODEL_NAME,
        input=( 
            system_msg +  user_msg
            )
        )

    except OpenAIError as e:
        logger.exception("OpenAI API call failed")
        raise RuntimeError(f"Summarization API error: {e}")
    

    usage = response.usage
    # Log token usage if available (works for both dict stubs and SDK objects)
    usage = getattr(response, "usage", None)
    if usage:
        if isinstance(usage, dict):
            input_toks = usage.get("input_tokens")
            output_toks = usage.get("output_tokens")
        else:
            input_toks = getattr(usage, "input_tokens", None)
            output_toks = getattr(usage, "output_tokens", None)

        logger.info(
            "Input tokens: %s  Output tokens: %s",
            input_toks,
            output_toks
        )

    # Raw model output (JSON string)
    raw = response.output_text.strip()

    # Parse & validate the JSON against our schema
    try:
        payload = json.loads(raw)
        summary = SummarySchema(**payload)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error("Failed to parse/validate JSON:\n%s\nRaw output:\n%s", e, raw)
        raise RuntimeError("Summarization service returned invalid JSON")

    # Return native dict for downstream code/tests
    return summary.dict()