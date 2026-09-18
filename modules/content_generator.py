"""
content_generator.py
LangChain chains for generating YouTube Description, Keywords, Tags, Hashtags, and Call to Actions.
"""

from modules.llm import get_llm
from modules.prompts import DESCRIPTION_PROMPT, METADATA_PROMPT

def generate_youtube_description(title: str, audience: str, script: str, llm=None) -> str:
    """
    Generates an SEO-friendly YouTube video description with timestamps and CTAs.
    """
    if llm is None:
        llm = get_llm()
    chain = DESCRIPTION_PROMPT | llm
    response = chain.invoke({
        "title": title,
        "audience": audience,
        "script": script
    })
    return response.content

def generate_youtube_metadata(topic: str, title: str, script: str, llm=None) -> str:
    """
    Generates a complete YouTube metadata package: Keywords, Tags, Hashtags, and CTA copy.
    """
    if llm is None:
        llm = get_llm()
    chain = METADATA_PROMPT | llm
    response = chain.invoke({
        "topic": topic,
        "title": title,
        "script": script
    })
    return response.content
