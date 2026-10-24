"""Validated LangChain workflow for scene-wise YouTube script breakdowns."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

from modules.llm import get_llm
from modules.prompts import SCENE_PROMPT

DEFAULT_NARRATION_SPEED_WPM = 140
MIN_SCENE_DURATION_SECONDS = 1


class SceneBreakdownError(RuntimeError):
    """Raised when a scene breakdown cannot be safely generated or validated."""


class Scene(BaseModel):
    """One production scene in the normalized public output."""

    scene_number: int = Field(ge=1)
    start_time: str
    end_time: str
    duration_seconds: int = Field(gt=0)
    voiceover: str = Field(min_length=1)
    visual_suggestion: str = Field(min_length=1)
    on_screen_text: str


class SceneBreakdown(BaseModel):
    """JSON-compatible scene breakdown returned by :func:`generate_scene_breakdown`."""

    scenes: List[Scene] = Field(min_length=1)
    total_duration_seconds: int = Field(gt=0)
    total_scenes: int = Field(gt=0)


def script_fingerprint(script: str) -> str:
    """Return a stable identifier for associating a breakdown with its source."""
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


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
    raise SceneBreakdownError("The LLM returned an unsupported response format.")


def _decode_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise SceneBreakdownError("The AI returned scene data that was not valid JSON.")
        try:
            payload = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as error:
            raise SceneBreakdownError("The AI returned malformed scene JSON.") from error
    if not isinstance(payload, dict):
        raise SceneBreakdownError("The AI scene data must be a JSON object.")
    return payload


def _format_time(seconds: int) -> str:
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes}:{remainder:02d}"


def parse_duration_seconds(video_length: Optional[str]) -> Optional[int]:
    """Convert a UI duration label or explicit duration into target seconds."""
    if not video_length:
        return None
    match = re.search(r"(\d+)\s*-\s*(\d+)\s*(?:min|mins|minutes)", video_length, re.I)
    if match:
        return round((int(match.group(1)) + int(match.group(2))) / 2 * 60)
    match = re.search(r"(\d+)\s*(?:min|mins|minutes)", video_length, re.I)
    if match:
        return int(match.group(1)) * 60
    return None


def _target_duration(script: str, video_length: Optional[str], speaking_rate_wpm: int) -> int:
    requested = parse_duration_seconds(video_length)
    if requested:
        return requested
    return max(MIN_SCENE_DURATION_SECONDS, round(len(script.split()) / speaking_rate_wpm * 60))


def _normalize_timeline(
    raw_scenes: List[Dict[str, Any]], total_duration: int
) -> List[Dict[str, Any]]:
    if not raw_scenes:
        raise SceneBreakdownError("The AI scene data must contain at least one scene.")
    normalized: List[Dict[str, Any]] = []
    weights = [max(1, len(str(scene.get("voiceover", "")).split())) for scene in raw_scenes]
    remaining = total_duration
    cursor = 0
    for index, scene in enumerate(raw_scenes, 1):
        if not isinstance(scene, dict):
            raise SceneBreakdownError("Every scene must be a JSON object.")
        if not isinstance(scene.get("scene_number"), int) or scene["scene_number"] < 1:
            raise SceneBreakdownError("Every scene needs a positive scene_number.")
        required = ("voiceover", "visual_suggestion", "on_screen_text")
        if any(not isinstance(scene.get(field), str) or not scene[field].strip() for field in required[:2]):
            raise SceneBreakdownError("Every scene needs voiceover and visual_suggestion text.")
        if not isinstance(scene.get("on_screen_text"), str):
            raise SceneBreakdownError("Every scene needs an on_screen_text string.")
        if index == len(raw_scenes):
            duration = remaining
        else:
            duration = max(MIN_SCENE_DURATION_SECONDS, round(total_duration * weights[index - 1] / sum(weights)))
            duration = min(duration, remaining - (len(raw_scenes) - index))
        if duration <= 0:
            raise SceneBreakdownError("The requested duration is too short for the number of scenes.")
        normalized.append(
            {
                "scene_number": index,
                "start_time": _format_time(cursor),
                "end_time": _format_time(cursor + duration),
                "duration_seconds": duration,
                "voiceover": scene["voiceover"].strip(),
                "visual_suggestion": scene["visual_suggestion"].strip(),
                "on_screen_text": scene["on_screen_text"].strip(),
            }
        )
        cursor += duration
        remaining -= duration
    return normalized


def generate_scene_breakdown(
    script: str,
    audience: str = "General Audience",
    tone: str = "Informative",
    video_length: str = "Not specified",
    content_style: str = "Not specified",
    speaking_rate_wpm: int = DEFAULT_NARRATION_SPEED_WPM,
    llm: Any = None,
) -> Dict[str, Any]:
    """Generate and normalize a scene breakdown for a non-empty script."""
    if not isinstance(script, str) or not script.strip():
        raise ValueError("Cannot generate a scene breakdown for an empty script.")
    if speaking_rate_wpm <= 0:
        raise ValueError("Narration speed must be greater than zero words per minute.")
    if llm is None:
        llm = get_llm()

    target_duration = _target_duration(script, video_length, speaking_rate_wpm)
    chain = SCENE_PROMPT | llm
    try:
        response = chain.invoke(
            {
                "script": script,
                "audience": audience,
                "tone": tone,
                "video_length": video_length,
                "content_style": content_style,
                "word_count": len(script.split()),
                "target_duration_seconds": target_duration,
                "narration_speed_wpm": speaking_rate_wpm,
            }
        )
        payload = _decode_json(_response_text(response))
        raw_scenes = payload.get("scenes")
        if not isinstance(raw_scenes, list):
            raise SceneBreakdownError("The AI scene data is missing its scenes list.")
        scenes = _normalize_timeline(raw_scenes, target_duration)
        result = SceneBreakdown(
            scenes=scenes,
            total_duration_seconds=target_duration,
            total_scenes=len(scenes),
        )
        return result.model_dump()
    except SceneBreakdownError:
        raise
    except Exception as error:
        raise SceneBreakdownError(f"Scene breakdown generation failed: {error}") from error


def breakdown_is_current(
    breakdown: Optional[Dict[str, Any]], breakdown_script_hash: Optional[str], script: str
) -> bool:
    """Return whether cached scene data belongs to the selected script."""
    return bool(breakdown and breakdown_script_hash == script_fingerprint(script))
