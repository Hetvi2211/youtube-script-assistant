"""
scene_generator.py
LangChain chain for converting YouTube scripts into scene-by-scene video production plans.
"""

from modules.llm import get_llm
from modules.prompts import SCENE_PROMPT

def generate_scene_breakdown(script: str, llm=None) -> str:
    """
    Parses a YouTube script into a structured scene-by-scene production breakdown table.
    """
    if llm is None:
        llm = get_llm()
    chain = SCENE_PROMPT | llm
    response = chain.invoke({"script": script})
    return response.content
