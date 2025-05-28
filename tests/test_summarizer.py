import pytest
from openai import OpenAIError
from app.summarizer import generate_summary, CLIENT
from types import SimpleNamespace
import json
from app.models import SummarySchema

# Valid JSON structure matching SummarySchema
VALID_JSON = {
    "summary": "A concise overview.",
    "key_illnesses": ["hypertension", "diabetes"],
    "past_treatments": ["angioplasty"],
    "current_medications": ["aspirin", "metformin"],
    "recommended_plan": "Follow up in 2 weeks."
}

class DummyResp:
    def __init__(self, content: str):
        # minimal usage metrics
        self.usage = {'input_tokens': 10, 'output_tokens': 50}
        # the raw JSON string your code will parse
        self.output_text = content


def test_generate_summary_success(monkeypatch):
    valid_obj = {
        "summary": "...",
        "key_illnesses": ["Diagnosis1", "Diagnosis2"],
        "past_treatments": ["Treatment1", "Treatment2"],
        "current_medications": ["Med1", "Med2"],
        "recommended_plan": "Next steps or plan"
    }
    raw = json.dumps(valid_obj)
    monkeypatch.setattr(
        CLIENT.responses,
        "create",
        lambda **kwargs: DummyResp(raw)
    )
    result = generate_summary("Some clinical text")
    assert isinstance(result, dict)
    assert result == valid_obj

def test_generate_summary_empty():
    with pytest.raises(ValueError):
        generate_summary("   ")

def test_generate_summary_valid_json(monkeypatch):
    """
    If the LLM returns well-formed JSON, generate_summary should parse and return it as a dict.
    """
    raw = json.dumps(VALID_JSON)
    # Stub the chat completion call
    monkeypatch.setattr(
        CLIENT.responses, "create",
        lambda **kwargs: DummyResp(raw)
    )

    result = generate_summary("Some clinical note text.")
    assert isinstance(result, dict)
    assert result == VALID_JSON
    # Validate against Pydantic schema
    SummarySchema(**result)


def test_generate_summary_malformed_json(monkeypatch):
    """
    If the LLM returns invalid JSON, generate_summary should raise RuntimeError.
    """
    # Return non-JSON content
    monkeypatch.setattr(
        CLIENT.responses, "create",
        lambda **kwargs: DummyResp("not a json")
    )
    with pytest.raises(RuntimeError) as exc_info:
        generate_summary("Some clinical note text.")
    assert "invalid json" in str(exc_info.value).lower()


def test_generate_summary_api_error(monkeypatch):
    monkeypatch.setattr(
        CLIENT.responses,
        "create",
        lambda model, input: (_ for _ in ()).throw(OpenAIError("fail"))
    )
    with pytest.raises(RuntimeError) as exc:
        generate_summary("Valid text")
    assert "Summarization API error" in str(exc.value)