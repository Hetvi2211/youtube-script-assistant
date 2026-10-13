"""Validated LangChain workflow for AI-assisted YouTube script analysis."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

from modules.llm import get_llm
from modules.prompts import ANALYZER_PROMPT


DEFAULT_SPEAKING_RATE_WPM = 140
CRITERION_NAMES = (
    "Hook Quality",
    "Script Structure",
    "Audience Suitability",
    "Tone Consistency",
    "Repetition",
    "Engagement",
    "Call-to-Action (CTA)",
    "Clarity",
    "Approximate Reading Time",
)


class CriterionEvaluation(BaseModel):
    """One AI evaluation on a 0-10 scale."""

    criterion: str = Field(min_length=1)
    score: float = Field(ge=0, le=10)
    rating: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    suggestion: str = Field(min_length=1)


class ScriptAnalysis(BaseModel):
    """Validated public shape returned by :func:`analyze_script`."""

    overall_score: float = Field(ge=0, le=100)
    overall_summary: str = Field(min_length=1)
    criteria: List[CriterionEvaluation] = Field(min_length=9, max_length=9)
    strengths: List[str]
    improvement_suggestions: List[str]
    missing_elements: List[str]
    word_count: int = Field(ge=0)
    estimated_reading_time_minutes: float = Field(ge=0)


class ScriptAnalysisError(RuntimeError):
    """Raised when an analysis request or its response cannot be used safely."""


def calculate_script_metrics(
    script: str, speaking_rate_wpm: int = DEFAULT_SPEAKING_RATE_WPM
) -> Dict[str, Any]:
    """Calculate deterministic script metrics without an LLM."""
    if speaking_rate_wpm <= 0:
        raise ValueError("Speaking rate must be greater than zero words per minute.")
    word_count = len(script.split())
    return {
        "word_count": word_count,
        "estimated_reading_time_minutes": round(word_count / speaking_rate_wpm, 2),
    }


def script_fingerprint(script: str) -> str:
    """Return a stable identifier used to associate analysis with a script version."""
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def analysis_is_current(
    analysis_result: Optional[Dict[str, Any]],
    analyzed_script_hash: Optional[str],
    analyzed_script_version: Optional[int],
    script: str,
    script_version: int,
) -> bool:
    """Check that an analysis belongs to the currently displayed script."""
    return bool(
        analysis_result
        and analyzed_script_hash == script_fingerprint(script)
        and analyzed_script_version == script_version
    )


def _response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, Iterable):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        if parts:
            return "".join(parts)
    raise ScriptAnalysisError("The LLM returned an unsupported response format.")


def _decode_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ScriptAnalysisError(
                "The AI returned analysis that was not valid JSON."
            )
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as error:
            raise ScriptAnalysisError(
                "The AI returned malformed analysis JSON."
            ) from error

    if not isinstance(parsed, dict):
        raise ScriptAnalysisError("The AI analysis JSON must be an object.")
    return parsed


def _validate_analysis(
    payload: Dict[str, Any], metrics: Dict[str, Any], script: str
) -> Dict[str, Any]:
    criteria = payload.get("criteria")
    if not isinstance(criteria, list):
        raise ScriptAnalysisError("The AI analysis is missing its criteria list.")

    normalized_criteria = []
    for item in criteria:
        if not isinstance(item, dict):
            raise ScriptAnalysisError("A criterion evaluation is not an object.")
        normalized_item = dict(item)
        if "criterion" not in normalized_item and "name" in normalized_item:
            normalized_item["criterion"] = normalized_item.pop("name")
        normalized_criteria.append(normalized_item)

    payload = dict(payload)
    payload["criteria"] = normalized_criteria
    payload["word_count"] = metrics["word_count"]
    payload["estimated_reading_time_minutes"] = metrics[
        "estimated_reading_time_minutes"
    ]

    try:
        model = ScriptAnalysis.model_validate(payload)
    except Exception as error:
        raise ScriptAnalysisError(
            "The AI analysis was incomplete or used invalid field values."
        ) from error

    names = [item.criterion.strip().lower() for item in model.criteria]
    expected = {name.lower() for name in CRITERION_NAMES}
    if len(set(names)) != len(CRITERION_NAMES) or set(names) != expected:
        raise ScriptAnalysisError(
            "The AI analysis must contain exactly the nine required criteria."
        )

    result = model.model_dump()
    missing_elements = result["missing_elements"]
    cta_pattern = (
        r"\b(subscribe|like this video|comment|share|follow|"
        r"turn on notifications|check out)\b"
    )
    cta_is_present = bool(re.search(cta_pattern, script[-600:], re.IGNORECASE))
    if cta_is_present:
        missing_elements = [
            item
            for item in missing_elements
            if "cta" not in item.lower() and "call-to-action" not in item.lower()
        ]
    elif not any(
        "cta" in item.lower() or "call-to-action" in item.lower()
        for item in missing_elements
    ):
        missing_elements.append("Call-to-Action (CTA)")
    result["missing_elements"] = missing_elements
    result["overall_score"] = round(
        sum(item["score"] for item in result["criteria"]) / len(result["criteria"]) * 10,
        1,
    )
    return result


def analyze_script(
    script: str,
    audience: str = "General Audience",
    tone: str = "Informative",
    video_length: str = "Not specified",
    content_style: str = "Not specified",
    topic: str = "YouTube video",
    speaking_rate_wpm: int = DEFAULT_SPEAKING_RATE_WPM,
    llm: Any = None,
    preferences: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Analyze the supplied script and return a validated JSON-compatible dict."""
    if not isinstance(script, str) or not script.strip():
        raise ValueError("Cannot analyze an empty script.")

    if preferences:
        topic = preferences.get("topic", topic)
        audience = preferences.get("audience", audience)
        tone = preferences.get("tone", tone)
        video_length = preferences.get("length", preferences.get("video_length", video_length))
        content_style = preferences.get("style", preferences.get("content_style", content_style))

    metrics = calculate_script_metrics(script, speaking_rate_wpm)
    if llm is None:
        llm = get_llm()

    chain = ANALYZER_PROMPT | llm
    try:
        response = chain.invoke(
            {
                "script": script,
                "topic": topic,
                "audience": audience,
                "tone": tone,
                "video_length": video_length,
                "content_style": content_style,
                "word_count": metrics["word_count"],
                "estimated_reading_time_minutes": metrics[
                    "estimated_reading_time_minutes"
                ],
            }
        )
        payload = _decode_json(_response_text(response))
        return _validate_analysis(payload, metrics, script)
    except ScriptAnalysisError:
        raise
    except Exception as error:
        raise ScriptAnalysisError(
            f"Unable to complete script analysis: {error}"
        ) from error
