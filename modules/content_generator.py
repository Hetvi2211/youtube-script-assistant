"""Validated LangChain workflow for YouTube Content Packages (Week 10)."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

from modules.llm import get_llm
from modules.prompts import METADATA_PROMPT

DEFAULT_MAX_TAGS_CHARS = 500  # YouTube character limit for tags


class ContentPackageError(RuntimeError):
    """Raised when a content package cannot be safely generated or parsed."""


class ContentPackage(BaseModel):
    """Structured representation of a complete YouTube Content Package."""

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    keywords: List[str] = Field(min_length=1)
    tags: List[str] = Field(min_length=1)
    hashtags: List[str] = Field(min_length=1)
    call_to_action: str = Field(min_length=1)
    raw_output: Optional[str] = None


def script_fingerprint(script: str) -> str:
    """Return a stable identifier for associating metadata with its source script."""
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def package_is_current(
    package: Optional[Dict[str, Any]],
    stored_hash: Optional[str],
    current_script: str,
) -> bool:
    """Check if the content package matches the currently selected script."""
    if not package or not stored_hash or not current_script.strip():
        return False
    return stored_hash == script_fingerprint(current_script.strip())


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
    raise ContentPackageError("The LLM returned an unsupported response format.")


def parse_metadata_sections(raw_text: str, fallback_title: str = "") -> Dict[str, Any]:
    """
    Parse the LLM response text into structured fields:
    description, keywords, tags, hashtags, and call_to_action.
    Supports either JSON format or formatted Markdown / section headers.
    """
    cleaned = raw_text.strip()

    # 1. Try JSON parse if response looks like JSON
    if cleaned.startswith("```json") or (cleaned.startswith("{") and cleaned.endswith("}")):
        json_clean = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        json_clean = re.sub(r"\s*```$", "", json_clean)
        try:
            payload = json.loads(json_clean)
            if isinstance(payload, dict):
                return {
                    "title": payload.get("title") or fallback_title or "Untitled Video",
                    "description": payload.get("description", "").strip(),
                    "keywords": [k.strip() for k in payload.get("keywords", []) if k.strip()],
                    "tags": [t.strip() for t in payload.get("tags", []) if t.strip()],
                    "hashtags": [h.strip() for h in payload.get("hashtags", []) if h.strip()],
                    "call_to_action": payload.get("call_to_action", "").strip(),
                    "raw_output": cleaned,
                }
        except Exception:
            pass

    # 2. Section-based regex / header parsing
    # Look for standard headers in METADATA_PROMPT:
    # 1. KEYWORDS
    # 2. YOUTUBE TAGS
    # 3. HASHTAGS
    # 4. CALL-TO-ACTION (CTA) VARIATIONS
    # Also optionally DESCRIPTION if included.

    result = {
        "title": fallback_title or "YouTube Video",
        "description": "",
        "keywords": [],
        "tags": [],
        "hashtags": [],
        "call_to_action": "",
        "raw_output": cleaned,
    }

    # Normalize section patterns
    section_patterns = {
        "description": r"(?:\[?DESCRIPTION\]?|1\.\s*\[?DESCRIPTION\]?|###?\s*Description)(.*?)(?=(?:\[?(?:KEYWORDS|YOUTUBE TAGS|TAGS|HASHTAGS|CALL-TO-ACTION|CTA)\]?|\d+\.\s*\[?(?:KEYWORDS|TAGS|HASHTAGS|CALL-TO-ACTION|CTA)\]?|###?\s*(?:Keywords|Tags|Hashtags|CTA))|$)",
        "keywords": r"(?:\[?KEYWORDS\]?|\d+\.\s*\[?KEYWORDS\]?|###?\s*Keywords)(.*?)(?=(?:\[?(?:YOUTUBE TAGS|TAGS|HASHTAGS|CALL-TO-ACTION|CTA)\]?|\d+\.\s*\[?(?:TAGS|YOUTUBE TAGS|HASHTAGS|CALL-TO-ACTION|CTA)\]?|###?\s*(?:Tags|Hashtags|CTA))|$)",
        "tags": r"(?:\[?YOUTUBE TAGS\]?|\[?TAGS\]?|\d+\.\s*\[?(?:YOUTUBE TAGS|TAGS)\]?|###?\s*(?:YouTube Tags|Tags))(.*?)(?=(?:\[?(?:HASHTAGS|CALL-TO-ACTION|CTA)\]?|\d+\.\s*\[?(?:HASHTAGS|CALL-TO-ACTION|CTA)\]?|###?\s*(?:Hashtags|CTA))|$)",
        "hashtags": r"(?:\[?HASHTAGS\]?|\d+\.\s*\[?HASHTAGS\]?|###?\s*Hashtags)(.*?)(?=(?:\[?(?:CALL-TO-ACTION|CTA)\]?|\d+\.\s*\[?(?:CALL-TO-ACTION|CTA)\]?|###?\s*(?:Call-to-Action|CTA))|$)",
        "cta": r"(?:\[?CALL-TO-ACTION(?:\s*\(CTA\))?(?:\s*VARIATIONS)?\]?|\d+\.\s*\[?CALL-TO-ACTION(?:\s*\(CTA\))?(?:\s*VARIATIONS)?\]?|###?\s*Call-to-Action.*)(.*)$",
    }

    desc_match = re.search(section_patterns["description"], cleaned, re.IGNORECASE | re.DOTALL)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    kw_match = re.search(section_patterns["keywords"], cleaned, re.IGNORECASE | re.DOTALL)
    if kw_match:
        kw_text = kw_match.group(1).strip()
        # Parse numbered list, bullet points, or comma-separated
        lines = [line.strip() for line in kw_text.splitlines() if line.strip()]
        keywords = []
        for line in lines:
            # strip numbers like "1. ", "- ", "* "
            item = re.sub(r"^(?:\d+[\.\)]|\-|\*)\s*", "", line).strip()
            if "," in item and not item.startswith("e.g."):
                parts = [p.strip() for p in item.split(",") if p.strip()]
                keywords.extend(parts)
            elif item:
                keywords.append(item)
        result["keywords"] = [k for k in keywords if len(k) > 1]

    tag_match = re.search(section_patterns["tags"], cleaned, re.IGNORECASE | re.DOTALL)
    if tag_match:
        tag_text = tag_match.group(1).strip()
        # Tags are usually comma-separated or numbered
        tags = []
        lines = [line.strip() for line in tag_text.splitlines() if line.strip()]
        for line in lines:
            line_cleaned = re.sub(r"^(?:\d+[\.\)]|\-|\*)\s*", "", line).strip()
            if "," in line_cleaned:
                tags.extend([t.strip() for t in line_cleaned.split(",") if t.strip()])
            elif line_cleaned:
                tags.append(line_cleaned)
        result["tags"] = [t.lstrip("#").strip() for t in tags if t.strip()]

    hash_match = re.search(section_patterns["hashtags"], cleaned, re.IGNORECASE | re.DOTALL)
    if hash_match:
        hash_text = hash_match.group(1).strip()
        # Extract words starting with # or list items
        hashtags = re.findall(r"#[A-Za-z0-9_]+", hash_text)
        if not hashtags:
            # fallback to lines or words
            items = re.findall(r"\b[A-Za-z0-9_]+\b", hash_text)
            hashtags = [f"#{item}" for item in items]
        result["hashtags"] = list(dict.fromkeys(hashtags))

    cta_match = re.search(section_patterns["cta"], cleaned, re.IGNORECASE | re.DOTALL)
    if cta_match:
        result["call_to_action"] = cta_match.group(1).strip()

    # Fallback if hashtags were directly present anywhere in the text
    if not result["hashtags"]:
        found = re.findall(r"#[A-Za-z0-9_]+", cleaned)
        if found:
            result["hashtags"] = list(dict.fromkeys(found))

    return result


def generate_content_package(
    topic: str,
    title: str,
    script: str,
    audience: str = "General Audience",
    llm: Any = None,
) -> Dict[str, Any]:
    """
    Generate a complete YouTube Content Package:
    - Title
    - Hook (extracted or confirmed from script)
    - Full Script
    - SEO Description
    - Keywords
    - Tags
    - Hashtags
    - Call-to-Action (CTA)

    Returns a JSON-compatible dictionary.
    """
    if not script or not script.strip():
        raise ValueError("Cannot generate a content package from an empty script.")
    if not topic or not topic.strip():
        raise ValueError("A topic is required to generate a content package.")

    clean_script = script.strip()
    clean_topic = topic.strip()
    clean_title = (title or "").strip() or clean_topic

    if llm is None:
        llm = get_llm(temperature=0.3)

    from langchain_core.runnables import ensure_config, Runnable
    from modules.prompts import DESCRIPTION_PROMPT, METADATA_PROMPT

    # Coerce to runnable if needed (e.g. callable or custom mock)
    runnable_llm = llm if isinstance(llm, Runnable) else (llm.invoke if hasattr(llm, "invoke") else llm)

    # 1. Generate Description
    try:
        desc_chain = DESCRIPTION_PROMPT | runnable_llm
        desc_response = desc_chain.invoke({
            "title": clean_title,
            "audience": audience,
            "script": clean_script,
        })
        desc_text = _response_text(desc_response).strip()
    except Exception as error:
        raise ContentPackageError(f"Description generation failed: {error}") from error

    # 2. Generate Metadata (Keywords, Tags, Hashtags, CTA)
    try:
        meta_chain = METADATA_PROMPT | runnable_llm
        meta_response = meta_chain.invoke({
            "topic": clean_topic,
            "title": clean_title,
            "script": clean_script,
        })
        meta_text = _response_text(meta_response).strip()
    except Exception as error:
        raise ContentPackageError(f"Metadata generation failed: {error}") from error

    # Parse and structure metadata
    parsed = parse_metadata_sections(meta_text, fallback_title=clean_title)

    # Use dedicated description if parsed didn't find one or if generated separately
    final_description = parsed["description"] if parsed["description"] else desc_text

    # Extract Hook from script if possible
    hook_match = re.search(r"\[HOOK\][^\n]*\n(.*?)(?=\n\[|\Z)", clean_script, re.DOTALL | re.IGNORECASE)
    hook = hook_match.group(1).strip() if hook_match else clean_script[:200].strip()

    package = {
        "title": clean_title,
        "hook": hook,
        "script": clean_script,
        "description": final_description,
        "keywords": parsed["keywords"],
        "tags": parsed["tags"],
        "hashtags": parsed["hashtags"],
        "call_to_action": parsed["call_to_action"],
        "raw_metadata": meta_text,
    }

    # Validate with Pydantic
    try:
        ContentPackage(
            title=package["title"],
            description=package["description"],
            keywords=package["keywords"] if package["keywords"] else ["YouTube", clean_topic],
            tags=package["tags"] if package["tags"] else [clean_topic],
            hashtags=package["hashtags"] if package["hashtags"] else [f"#{clean_topic.replace(' ', '')}"],
            call_to_action=package["call_to_action"] if package["call_to_action"] else "Subscribe for more content!",
            raw_output=meta_text,
        )
    except Exception as err:
        # If strict validation fails due to empty lists, provide safe defaults
        if not package["keywords"]:
            package["keywords"] = [clean_topic, "YouTube Tutorial", "Guide"]
        if not package["tags"]:
            package["tags"] = [clean_topic, "tutorial", "guide"]
        if not package["hashtags"]:
            package["hashtags"] = [f"#{clean_topic.replace(' ', '')}"]
        if not package["call_to_action"]:
            package["call_to_action"] = "Like, comment, and subscribe for more insightful videos!"

    return package


def generate_youtube_description(title: str, audience: str, script: str, llm: Any = None) -> str:
    """
    Backwards-compatible wrapper: Generates an SEO-friendly YouTube video description.
    """
    if llm is None:
        llm = get_llm()
    from langchain_core.runnables import Runnable
    runnable_llm = llm if isinstance(llm, Runnable) else (llm.invoke if hasattr(llm, "invoke") else llm)
    chain = DESCRIPTION_PROMPT | runnable_llm
    response = chain.invoke({
        "title": title,
        "audience": audience,
        "script": script,
    })
    return _response_text(response)


def generate_youtube_metadata(topic: str, title: str, script: str, llm: Any = None) -> str:
    """
    Backwards-compatible wrapper: Generates YouTube metadata text.
    """
    if llm is None:
        llm = get_llm()
    from langchain_core.runnables import Runnable
    runnable_llm = llm if isinstance(llm, Runnable) else (llm.invoke if hasattr(llm, "invoke") else llm)
    chain = METADATA_PROMPT | runnable_llm
    response = chain.invoke({
        "topic": topic,
        "title": title,
        "script": script,
    })
    return _response_text(response)


def format_package_as_text(package: Dict[str, Any]) -> str:
    """Format the complete content package as clean text for display or export."""
    keywords_str = ", ".join(package.get("keywords", []))
    tags_str = ", ".join(package.get("tags", []))
    hashtags_str = " ".join(package.get("hashtags", []))

    text_parts = [
        "==================================================",
        "YOUTUBE COMPLETE CONTENT PACKAGE",
        "==================================================",
        f"\nTITLE:\n{package.get('title', '')}\n",
        f"\nHOOK:\n{package.get('hook', '')}\n",
        f"\nSCRIPT:\n{package.get('script', '')}\n",
        f"\nDESCRIPTION:\n{package.get('description', '')}\n",
        f"\nKEYWORDS:\n{keywords_str}\n",
        f"\nTAGS:\n{tags_str}\n",
        f"\nHASHTAGS:\n{hashtags_str}\n",
        f"\nCALL-TO-ACTION (CTA):\n{package.get('call_to_action', '')}\n",
        "==================================================",
    ]
    return "\n".join(text_parts)
