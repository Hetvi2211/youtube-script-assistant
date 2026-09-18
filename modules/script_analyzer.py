"""
script_analyzer.py
LangChain chain for analyzing YouTube video scripts across retention, hook, structure, and clarity metrics.
"""

from modules.llm import get_llm
from modules.prompts import ANALYZER_PROMPT

def analyze_script(script: str, llm=None) -> str:
    """
    Evaluates the provided YouTube script across 8 core retention metrics
    and returns a formatted analysis report with ratings and suggestions.
    """
    if llm is None:
        llm = get_llm()
    chain = ANALYZER_PROMPT | llm
    response = chain.invoke({"script": script})
    return response.content
