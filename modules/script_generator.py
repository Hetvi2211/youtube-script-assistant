"""
script_generator.py
LangChain chains for Title Generation, Hook Generation, and Full YouTube Script Writing.
"""

from modules.llm import get_llm
from modules.prompts import TITLE_PROMPT, HOOK_PROMPT, SCRIPT_PROMPT

def generate_titles(topic: str, audience: str, tone: str, style: str, llm=None) -> str:
    """
    Generates 5 YouTube video title suggestions based on user preferences.
    """
    if llm is None:
        llm = get_llm()
    chain = TITLE_PROMPT | llm
    response = chain.invoke({
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "style": style
    })
    return response.content

def generate_hooks(topic: str, audience: str, tone: str, llm=None) -> str:
    """
    Generates 5 YouTube hook options across different styles.
    """
    if llm is None:
        llm = get_llm()
    chain = HOOK_PROMPT | llm
    response = chain.invoke({
        "topic": topic,
        "audience": audience,
        "tone": tone
    })
    return response.content

def generate_script(topic: str, audience: str, tone: str, length: str, style: str, llm=None) -> str:
    """
    Generates a full YouTube video script structured with hooks, intro, main content, and CTA.
    """
    if llm is None:
        llm = get_llm()
    chain = SCRIPT_PROMPT | llm
    response = chain.invoke({
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "length": length,
        "style": style
    })
    return response.content
