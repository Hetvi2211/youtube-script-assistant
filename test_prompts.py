"""
test_prompts.py
Week 2 Prompt Engineering Experiments.
Tests 4 different scenarios (Technology, Education, Humor tone, Student audience)
to observe how prompt parameters affect LLM output quality.
"""

import sys
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from modules.llm import get_llm

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

def run_prompt_experiments():
    print("==================================================")
    print(" Week 2 Prompt Engineering Experiment Suite")
    print("==================================================\n")
    
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
        print("[!] No API Key found in .env! Please add an API key to run live experiments.\n")
        return

    llm = get_llm(temperature=0.7)

    prompt_template = PromptTemplate(
        input_variables=["topic", "audience", "tone", "style"],
        template="""
Generate 3 distinct YouTube video concept ideas based on the following preferences:
- Topic: {topic}
- Target Audience: {audience}
- Tone: {tone}
- Style: {style}

For each concept, provide:
1. Catchy Title
2. Hook Angle (Why viewers will click and watch)
"""
    )

    chain = prompt_template | llm

    experiments = [
        {
            "name": "Test 1 — Technology Focus",
            "topic": "Generative AI in Web Development",
            "audience": "Software Developers & Tech Leads",
            "tone": "Professional & Forward-looking",
            "style": "Deep-dive Analysis"
        },
        {
            "name": "Test 2 — Educational Focus",
            "topic": "Python Programming for Absolute Beginners",
            "audience": "High School & College Students",
            "tone": "Encouraging & Clear",
            "style": "Step-by-Step Tutorial"
        },
        {
            "name": "Test 3 — Funny / Casual Tone Focus",
            "topic": "Bugs & Nightmares in Machine Learning Code",
            "audience": "Junior Developers & Data Scientists",
            "tone": "Humorous & Relatable",
            "style": "Top 5 Listicle"
        },
        {
            "name": "Test 4 — Student Audience Focus",
            "topic": "How to Study for Coding Interviews Using AI",
            "audience": "Computer Science Undergrads",
            "tone": "Actionable & Motivational",
            "style": "Storytelling & Practical Tips"
        }
    ]

    for exp in experiments:
        print(f"------------ {exp['name']} ------------")
        print(f"Topic: {exp['topic']} | Tone: {exp['tone']} | Style: {exp['style']}")
        try:
            res = chain.invoke(exp)
            print("\n[+] AI Generated Concepts:\n")
            print(res.content)
            print("\n")
        except Exception as e:
            print(f"[X] Error during experiment: {e}\n")

if __name__ == "__main__":
    run_prompt_experiments()
