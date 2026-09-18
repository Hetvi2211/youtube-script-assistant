"""
test_week3.py
Verification suite for Week 3 Prompt Engineering Pipeline.
Tests all 8 prompt templates and chains:
1. Title Generation
2. Hook Generation
3. Full Script Generation
4. Script Analysis
5. Script Improvement
6. Scene-wise Breakdown
7. YouTube Description
8. Keywords / Tags / Hashtags Package
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
from modules.script_generator import generate_titles, generate_hooks, generate_script
from modules.script_analyzer import analyze_script
from modules.script_improver import improve_script
from modules.scene_generator import generate_scene_breakdown
from modules.content_generator import generate_youtube_description, generate_youtube_metadata

def run_week3_pipeline_test():
    print("==================================================")
    print(" Week 3 Prompt System Full Pipeline Verification ")
    print("==================================================\n")
    
    # Verify API key
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
        print("[!] Warning: No API keys set in .env file.")
        print("Please configure GOOGLE_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY to test live LLM outputs.\n")
        return

    # Sample input specifications
    test_params = {
        "topic": "Artificial Intelligence in Healthcare",
        "audience": "Medical Students & Tech Enthusiasts",
        "tone": "Informative & Engaging",
        "length": "Medium (5 - 10 mins)",
        "style": "Step-by-Step Breakdown"
    }

    print("[>] Test Input Parameters:")
    for k, v in test_params.items():
        print(f"    - {k.capitalize()}: {v}")
    print("\n--------------------------------------------------")

    try:
        llm = get_llm(temperature=0.7)
        print("[+] LLM Instance Initialized Successfully.\n")
    except Exception as e:
        print(f"[X] LLM Initialization Failed: {e}")
        return

    # Step 1: Title Generation
    print("--- [1/8] Testing Title Generation Prompt ---")
    titles_output = generate_titles(
        topic=test_params["topic"],
        audience=test_params["audience"],
        tone=test_params["tone"],
        style=test_params["style"],
        llm=llm
    )
    print(titles_output[:300] + "...\n")

    # Step 2: Hook Generation
    print("--- [2/8] Testing Hook Generation Prompt ---")
    hooks_output = generate_hooks(
        topic=test_params["topic"],
        audience=test_params["audience"],
        tone=test_params["tone"],
        llm=llm
    )
    print(hooks_output[:300] + "...\n")

    # Step 3: Script Generation
    print("--- [3/8] Testing Full Script Generation Prompt ---")
    script_output = generate_script(
        topic=test_params["topic"],
        audience=test_params["audience"],
        tone=test_params["tone"],
        length=test_params["length"],
        style=test_params["style"],
        llm=llm
    )
    print(script_output[:400] + "...\n")

    # Step 4: Script Analysis
    print("--- [4/8] Testing Script Analyzer Prompt ---")
    analysis_output = analyze_script(script=script_output, llm=llm)
    print(analysis_output[:350] + "...\n")

    # Step 5: Script Improvement
    print("--- [5/8] Testing Script Improvement Prompt ---")
    improved_script_output = improve_script(
        original_script=script_output,
        analysis=analysis_output,
        user_feedback="Add a sharper hook and extra emphasis on early diagnosis benefits.",
        llm=llm
    )
    print(improved_script_output[:400] + "...\n")

    # Step 6: Scene Breakdown
    print("--- [6/8] Testing Scene-wise Breakdown Prompt ---")
    scene_output = generate_scene_breakdown(script=improved_script_output, llm=llm)
    print(scene_output[:350] + "...\n")

    # Step 7: YouTube Description
    print("--- [7/8] Testing YouTube Description Prompt ---")
    selected_title = "AI in Healthcare: How Artificial Intelligence Is Transforming Medicine"
    description_output = generate_youtube_description(
        title=selected_title,
        audience=test_params["audience"],
        script=improved_script_output,
        llm=llm
    )
    print(description_output[:350] + "...\n")

    # Step 8: YouTube Metadata Package
    print("--- [8/8] Testing Keywords / Tags / Hashtags Package Prompt ---")
    metadata_output = generate_youtube_metadata(
        topic=test_params["topic"],
        title=selected_title,
        script=improved_script_output,
        llm=llm
    )
    print(metadata_output[:350] + "...\n")

    print("==================================================")
    print(" SUCCESS! All 8 Week 3 Prompts Executed Cleanly! ")
    print("==================================================")

if __name__ == "__main__":
    run_week3_pipeline_test()
