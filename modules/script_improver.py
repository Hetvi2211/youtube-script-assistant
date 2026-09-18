"""
script_improver.py
LangChain chain for enhancing and rewriting YouTube video scripts based on analysis reports.
"""

from modules.llm import get_llm
from modules.prompts import IMPROVEMENT_PROMPT

def improve_script(original_script: str, analysis: str, user_feedback: str = "Focus on retention and strong spoken delivery.", llm=None) -> str:
    """
    Rewrites and enhances the original script using AI analysis feedback and optional user directives.
    """
    if llm is None:
        llm = get_llm()
    chain = IMPROVEMENT_PROMPT | llm
    response = chain.invoke({
        "script": original_script,
        "analysis": analysis,
        "user_feedback": user_feedback
    })
    return response.content
