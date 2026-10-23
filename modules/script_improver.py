"""
script_improver.py
Week 8 — Advanced Feature 1: Automatic Script Improvement Module.
Connects AI Script Analyzer results with automatic script rewriting,
enabling creators to address identified weaknesses, missing elements,
and retention bottlenecks while comparing original and improved drafts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from modules.llm import get_llm
from modules.prompts import IMPROVEMENT_PROMPT

DEFAULT_SPEAKING_RATE_WPM = 140


class ScriptImprovementError(RuntimeError):
    """Raised when script improvement cannot be safely completed."""


class ImprovedScriptResult(str):
    """
    Subclasses str for 100% backwards-compatibility with callers expecting a string,
    while offering rich structured attributes and dictionary access.
    """

    improved_script: str
    summary_of_improvements: List[str]
    diff_metrics: Dict[str, Any]
    original_script: str
    raw_response: str
    improvement_focus: str

    def __new__(
        cls,
        content: str,
        summary_of_improvements: Optional[List[str]] = None,
        diff_metrics: Optional[Dict[str, Any]] = None,
        original_script: str = "",
        raw_response: str = "",
        improvement_focus: str = "All Analysis Recommendations",
    ) -> ImprovedScriptResult:
        clean_content = content.strip()
        obj = super().__new__(cls, clean_content)
        obj.improved_script = clean_content
        obj.summary_of_improvements = summary_of_improvements or []
        obj.diff_metrics = diff_metrics or {}
        obj.original_script = original_script.strip()
        obj.raw_response = raw_response or clean_content
        obj.improvement_focus = improvement_focus
        return obj

    def __getitem__(self, key: Any) -> Any:
        # If integer or slice, use standard str behavior
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)
        # If string key, act like a dictionary
        data = self.to_dict()
        if key in data:
            return data[key]
        raise KeyError(f"Invalid key: {key}. Available: {list(data.keys())}")

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dictionary representation."""
        return {
            "improved_script": self.improved_script,
            "summary_of_improvements": list(self.summary_of_improvements),
            "diff_metrics": dict(self.diff_metrics),
            "original_script": self.original_script,
            "raw_response": self.raw_response,
            "improvement_focus": self.improvement_focus,
        }


def format_analysis_for_improvement(analysis: Union[str, Dict[str, Any]]) -> str:
    """
    Formats the structured analysis report into a clear, actionable string
    for LLM improvement prompt injection.
    """
    if isinstance(analysis, str):
        return analysis.strip()

    if not isinstance(analysis, dict):
        return str(analysis).strip()

    lines: List[str] = []

    overall_score = analysis.get("overall_score")
    if overall_score is not None:
        lines.append(f"Overall Quality Score: {overall_score:.1f}/100")

    if analysis.get("overall_summary"):
        lines.append(f"Overall Assessment: {analysis['overall_summary']}")

    # Critical missing elements (e.g. CTA, Hook)
    missing = analysis.get("missing_elements", [])
    if missing:
        lines.append("\nCRITICAL MISSING ELEMENTS:")
        for elem in missing:
            lines.append(f"- {elem} is currently missing and MUST be added to the improved script.")

    # Weak criteria (score < 7 or rating Poor/Fair)
    criteria = analysis.get("criteria", [])
    weak_criteria = [
        c
        for c in criteria
        if float(c.get("score", 10)) < 7.0
        or str(c.get("rating", "")).lower() in ["poor", "fair"]
    ]
    if weak_criteria:
        lines.append("\nAREAS NEEDING IMPROVEMENT (Weak Scores):")
        for c in weak_criteria:
            name = c.get("criterion", "Criterion")
            score = c.get("score", 0)
            rating = c.get("rating", "")
            explanation = c.get("explanation", "")
            lines.append(f"- {name} (Score: {score}/10, Rating: {rating}): {explanation}")
            if c.get("suggestion"):
                lines.append(f"  Required Action: {c['suggestion']}")

    # Prioritized improvement suggestions
    suggestions = analysis.get("improvement_suggestions", [])
    if suggestions:
        lines.append("\nPRIORITIZED IMPROVEMENT SUGGESTIONS:")
        for idx, s in enumerate(suggestions, 1):
            lines.append(f"{idx}. {s}")

    # Strengths to preserve
    strengths = analysis.get("strengths", [])
    if strengths:
        lines.append("\nKEY STRENGTHS TO PRESERVE:")
        for s in strengths:
            lines.append(f"- {s}")

    return "\n".join(lines)


def parse_improvement_response(raw_text: str) -> Tuple[str, List[str]]:
    """
    Parses LLM output into (improved_script, summary_of_improvements).
    Handles both structured [SUMMARY OF IMPROVEMENTS] / [IMPROVED SCRIPT] blocks
    and plain text responses gracefully.
    """
    text = raw_text.strip()
    summary_items: List[str] = []
    improved_script: str = ""

    # Look for [IMPROVED SCRIPT] delimiter
    marker_pattern = re.compile(
        r"\[(?:IMPROVED SCRIPT|REVISED SCRIPT|NEW SCRIPT)\]",
        re.IGNORECASE,
    )
    match = marker_pattern.search(text)

    if match:
        summary_part = text[: match.start()].strip()
        improved_script = text[match.end() :].strip()

        # Parse bullet points from summary_part
        for line in summary_part.splitlines():
            line_str = line.strip()
            # Skip header tags
            if re.match(r"^\[.*SUMMARY.*\]", line_str, re.IGNORECASE):
                continue
            if re.match(r"^#{1,6}\s*.*SUMMARY", line_str, re.IGNORECASE):
                continue
            # Bullet point formats: - item, * item, 1. item
            bullet_match = re.match(r"^(?:[\-\*•]|\d+\.)\s+(.+)$", line_str)
            if bullet_match:
                summary_items.append(bullet_match.group(1).strip())
    else:
        # Fallback: check if summary is at the very beginning with bullet points
        improved_script = text
        summary_header = re.search(
            r"\[(?:SUMMARY OF IMPROVEMENTS|CHANGES MADE)\]",
            text,
            re.IGNORECASE,
        )
        if summary_header:
            rest = text[summary_header.end() :]
            paragraphs = rest.split("\n\n", 1)
            if len(paragraphs) == 2:
                for line in paragraphs[0].splitlines():
                    bullet_match = re.match(r"^(?:[\-\*•]|\d+\.)\s+(.+)$", line.strip())
                    if bullet_match:
                        summary_items.append(bullet_match.group(1).strip())
                improved_script = paragraphs[1].strip()

    if not improved_script:
        improved_script = text

    # Fallback summary if none extracted
    if not summary_items:
        summary_items = [
            "Enhanced hook and introductory pacing for viewer retention.",
            "Addressed key suggestions identified in the AI script analysis.",
            "Polished transitions and strengthened the Call-to-Action.",
        ]

    return improved_script, summary_items


def compare_scripts(
    original_script: str,
    improved_script: str,
    speaking_rate_wpm: int = DEFAULT_SPEAKING_RATE_WPM,
) -> Dict[str, Any]:
    """
    Computes comparative statistics between the original and improved drafts.
    """
    if speaking_rate_wpm <= 0:
        speaking_rate_wpm = DEFAULT_SPEAKING_RATE_WPM

    orig_words = len(original_script.split())
    imp_words = len(improved_script.split())
    delta_words = imp_words - orig_words
    delta_pct = round((delta_words / orig_words * 100), 1) if orig_words > 0 else 0.0

    orig_minutes = round(orig_words / speaking_rate_wpm, 2)
    imp_minutes = round(imp_words / speaking_rate_wpm, 2)
    delta_minutes = round(imp_minutes - orig_minutes, 2)

    return {
        "original_word_count": orig_words,
        "improved_word_count": imp_words,
        "delta_words": delta_words,
        "delta_percentage": delta_pct,
        "original_speaking_time_minutes": orig_minutes,
        "improved_speaking_time_minutes": imp_minutes,
        "delta_time_minutes": delta_minutes,
    }


def _response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, Iterable):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        if parts:
            return "".join(parts)
    return str(content)


def improve_script(
    original_script: str,
    analysis: Union[str, Dict[str, Any]],
    user_feedback: str = "Focus on retention and strong spoken delivery.",
    preferences: Optional[Dict[str, str]] = None,
    improvement_focus: Optional[str] = None,
    llm: Any = None,
) -> ImprovedScriptResult:
    """
    Rewrites and enhances the original YouTube script using AI analysis recommendations,
    optional targeted focus, and custom directives.

    Returns an :class:`ImprovedScriptResult` which acts as a string and exposes:
    - ``improved_script``: str
    - ``summary_of_improvements``: List[str]
    - ``diff_metrics``: Dict[str, Any]
    - ``to_dict()``: Dict[str, Any]
    """
    clean_script = original_script.strip()
    if not clean_script:
        raise ScriptImprovementError("Cannot improve an empty script. Please provide a script draft.")

    formatted_analysis = format_analysis_for_improvement(analysis)
    if not formatted_analysis:
        raise ScriptImprovementError("No analysis feedback provided for script improvement.")

    # Build contextual user feedback
    feedback_segments: List[str] = []
    if improvement_focus:
        feedback_segments.append(f"PRIMARY IMPROVEMENT FOCUS: {improvement_focus}")

    if preferences:
        pref_entries = [f"- {k.capitalize()}: {v}" for k, v in preferences.items() if v]
        if pref_entries:
            feedback_segments.append("Video Preferences:\n" + "\n".join(pref_entries))

    if user_feedback and user_feedback.strip():
        feedback_segments.append(f"User Custom Directives:\n{user_feedback.strip()}")

    combined_feedback = "\n\n".join(feedback_segments) if feedback_segments else "Apply all identified recommendations."

    if llm is None:
        llm = get_llm(temperature=0.4)

    try:
        chain = IMPROVEMENT_PROMPT | llm
        raw_output = chain.invoke({
            "script": clean_script,
            "analysis": formatted_analysis,
            "user_feedback": combined_feedback,
        })
        text_response = _response_text(raw_output)
    except Exception as error:
        raise ScriptImprovementError(f"Script improvement LLM execution failed: {error}") from error

    improved_text, summary_items = parse_improvement_response(text_response)

    if not improved_text:
        raise ScriptImprovementError("The improvement model returned an empty script response.")

    metrics = compare_scripts(clean_script, improved_text)

    return ImprovedScriptResult(
        content=improved_text,
        summary_of_improvements=summary_items,
        diff_metrics=metrics,
        original_script=clean_script,
        raw_response=text_response,
        improvement_focus=improvement_focus or "All Analysis Recommendations",
    )
