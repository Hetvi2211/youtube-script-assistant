"""
conversation.py
Week 6 — Conversation History & Script Regeneration Module.
Provides context-aware conversational refinement, full script regeneration,
and quick modification workflows (shorten, expand, tone change, hook improvement, add examples).
"""

from typing import List, Dict, Any, Optional
from modules.llm import get_llm
from modules.prompts import (
    CONTEXT_REFINEMENT_PROMPT,
    REGENERATE_SCRIPT_PROMPT,
    SHORTEN_SCRIPT_PROMPT,
    EXPAND_SCRIPT_PROMPT,
    CHANGE_TONE_PROMPT,
    IMPROVE_INTRO_PROMPT,
    ADD_EXAMPLES_PROMPT,
)


def format_chat_history(messages: List[Dict[str, str]], max_turns: int = 6) -> str:
    """
    Formats the recent chat message history list into a readable context string for prompt injection.
    """
    if not messages:
        return "No previous conversation history."
    
    recent = messages[-max_turns:]
    formatted = []
    for msg in recent:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        formatted.append(f"{role}: {content}")
    return "\n\n".join(formatted)


def refine_script_with_chat(
    current_script: str,
    user_instruction: str,
    chat_history: List[Dict[str, str]],
    preferences: Optional[Dict[str, str]] = None,
    llm=None
) -> str:
    """
    Applies user-requested revisions to the current script in a context-aware conversational manner.
    """
    if llm is None:
        llm = get_llm()

    prefs = preferences or {}
    topic = prefs.get("topic", "YouTube Video")
    audience = prefs.get("audience", "General Audience")
    tone = prefs.get("tone", "Engaging")

    history_str = format_chat_history(chat_history)

    chain = CONTEXT_REFINEMENT_PROMPT | llm
    response = chain.invoke({
        "current_script": current_script,
        "conversation_history": history_str,
        "user_instruction": user_instruction,
        "topic": topic,
        "audience": audience,
        "tone": tone
    })
    return response.content


def regenerate_script_alternative(
    topic: str,
    audience: str,
    tone: str,
    length: str,
    style: str,
    llm=None
) -> str:
    """
    Generates a fresh alternative creative script with the same input parameters.
    """
    if llm is None:
        llm = get_llm()

    chain = REGENERATE_SCRIPT_PROMPT | llm
    response = chain.invoke({
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "length": length,
        "style": style
    })
    return response.content


def modify_script_quick(
    current_script: str,
    action: str,
    custom_param: Optional[str] = None,
    llm=None
) -> str:
    """
    Performs one-click targeted script modifications:
    - 'shorten': Condenses word count by ~25-35%.
    - 'expand': Enriches script with deeper explanation and more visual cues.
    - 'change_tone': Adapts script language and pacing to target_tone.
    - 'improve_intro': Supercharges the hook and introduction for maximum retention.
    - 'add_examples': Injects 2-3 concrete real-world examples or case studies.
    """
    if llm is None:
        llm = get_llm()

    action_normalized = action.lower().strip()

    if action_normalized == "shorten":
        chain = SHORTEN_SCRIPT_PROMPT | llm
        response = chain.invoke({"script": current_script})
        return response.content

    elif action_normalized == "expand":
        chain = EXPAND_SCRIPT_PROMPT | llm
        response = chain.invoke({"script": current_script})
        return response.content

    elif action_normalized == "change_tone":
        target_tone = custom_param or "Casual/Friendly"
        chain = CHANGE_TONE_PROMPT | llm
        response = chain.invoke({"script": current_script, "target_tone": target_tone})
        return response.content

    elif action_normalized in ["improve_intro", "improve_hook"]:
        chain = IMPROVE_INTRO_PROMPT | llm
        response = chain.invoke({"script": current_script})
        return response.content

    elif action_normalized in ["add_examples", "examples"]:
        chain = ADD_EXAMPLES_PROMPT | llm
        response = chain.invoke({"script": current_script})
        return response.content

    else:
        raise ValueError(f"Unsupported quick modification action: {action}")
