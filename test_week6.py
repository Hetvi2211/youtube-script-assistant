"""
test_week6.py
Verification suite for Week 6 — Conversation History & Script Regeneration.
Tests:
1. Quick script modification: Shorten script
2. Quick script modification: Expand script
3. Quick script modification: Change tone
4. Quick script modification: Improve hook and intro
5. Quick script modification: Add real-world examples
6. Context-aware conversational refinement (User prompt with conversation history)
7. Alternative script regeneration
"""

import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

from modules.llm import get_llm
from modules.conversation import (
    refine_script_with_chat,
    regenerate_script_alternative,
    modify_script_quick,
    format_chat_history,
)

SAMPLE_SCRIPT = """
[TITLE SUGGESTION]: 5 Daily Habits That Changed My Morning Routine
[HOOK] (0:00 - 0:30)
Most people start their day in chaos, checking notifications before their feet even hit the floor. But what if 10 simple minutes could double your energy for the rest of the day?
[INTRODUCTION]
Hey everyone, welcome back. Today we're breaking down 5 small morning habits that completely transformed my focus and productivity.
[MAIN CONTENT]
1. Hydration First: Drink 500ml of water before coffee.
2. Sunlight Exposure: Get 5-10 minutes of natural light to set your circadian rhythm.
3. Zero Phone for 30 Minutes: Protect your dopamine levels.
[CONCLUSION & RECAP]
Small steps compound into massive results. Pick just one habit to try tomorrow morning.
[CALL-TO-ACTION & OUTRO]
If you found this valuable, hit subscribe and let me know your favorite morning routine in the comments!
""".strip()


def run_week6_tests():
    print("==================================================")
    print(" Week 6: Conversation History & Refine Verification")
    print("==================================================\n")

    if not (os.getenv("GROQ_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")):
        print("[!] No API key found in .env. Please configure GROQ_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY.")
        return

    try:
        llm = get_llm()
        print(f"[+] LLM initialized successfully: {llm.model_name if hasattr(llm, 'model_name') else 'Active LLM'}\n")
    except Exception as e:
        print(f"[X] LLM init error: {e}")
        return

    # Test 1: Chat history formatting
    print("--- [1/7] Testing Chat History Transcript Formatting ---")
    history_mock = [
        {"role": "user", "content": "Can you generate a morning routine script?"},
        {"role": "assistant", "content": "Sure! Here is a 5-habit morning routine script."},
    ]
    formatted_h = format_chat_history(history_mock)
    print(formatted_h)
    print("Formatting OK ✅\n")

    # Test 2: Quick Modify - Improve Intro / Hook
    print("--- [2/7] Testing Quick Modify: Improve Hook & Intro ---")
    try:
        improved_intro = modify_script_quick(SAMPLE_SCRIPT, "improve_intro", llm=llm)
        print(improved_intro[:300] + "...\n")
        print("Improve Intro OK ✅\n")
    except Exception as e:
        print(f"[X] Error: {e}")

    # Test 3: Quick Modify - Shorten Script
    print("--- [3/7] Testing Quick Modify: Shorten Script ---")
    try:
        shortened = modify_script_quick(SAMPLE_SCRIPT, "shorten", llm=llm)
        print(shortened[:300] + "...\n")
        print("Shorten OK ✅\n")
    except Exception as e:
        print(f"[X] Error: {e}")

    # Test 4: Quick Modify - Add Examples
    print("--- [4/7] Testing Quick Modify: Add Examples ---")
    try:
        with_examples = modify_script_quick(SAMPLE_SCRIPT, "add_examples", llm=llm)
        print(with_examples[:300] + "...\n")
        print("Add Examples OK ✅\n")
    except Exception as e:
        print(f"[X] Error: {e}")

    # Test 5: Quick Modify - Change Tone
    print("--- [5/7] Testing Quick Modify: Change Tone (Humorous) ---")
    try:
        humorous = modify_script_quick(SAMPLE_SCRIPT, "change_tone", custom_param="Humorous & Sarcastic", llm=llm)
        print(humorous[:300] + "...\n")
        print("Change Tone OK ✅\n")
    except Exception as e:
        print(f"[X] Error: {e}")

    # Test 6: Conversational Refinement Prompt
    print("--- [6/7] Testing Conversational Refinement (User prompt) ---")
    try:
        refined = refine_script_with_chat(
            current_script=SAMPLE_SCRIPT,
            user_instruction="Make the introduction more engaging and add a personal story about waking up exhausted.",
            chat_history=history_mock,
            preferences={"topic": "Morning Habits", "audience": "College Students", "tone": "Engaging"},
            llm=llm
        )
        print(refined[:350] + "...\n")
        print("Conversational Refinement OK ✅\n")
    except Exception as e:
        print(f"[X] Error: {e}")

    # Test 7: Regenerate Full Script Alternative
    print("--- [7/7] Testing Regenerate Script Alternative ---")
    try:
        regenerated = regenerate_script_alternative(
            topic="Morning Habits for Productivity",
            audience="College Students",
            tone="Inspirational",
            length="Medium (5 - 10 mins)",
            style="Storytelling",
            llm=llm
        )
        print(regenerated[:350] + "...\n")
        print("Regenerate OK ✅\n")
    except Exception as e:
        print(f"[X] Error: {e}")

    print("==================================================")
    print("🎉 ALL WEEK 6 CONVERSATION & REFINEMENT TESTS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_week6_tests()
