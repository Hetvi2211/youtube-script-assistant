"""
test_llm.py
Week 2 Verification Script: Tests Python -> LangChain -> LLM pipeline.
"""

import sys
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from modules.llm import get_llm

# Force UTF-8 encoding for standard output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables
load_dotenv()

def test_basic_llm_connection():
    print("==================================================")
    print(" Week 2 LLM Integration Verification Test")
    print("==================================================\n")
    
    # 1. Environment & API Key Verification
    google_key = os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    print("[+] API Key Check:")
    print(f" - GOOGLE_API_KEY: {'Loaded [OK]' if google_key else 'Not Found [MISSING]'}")
    print(f" - OPENAI_API_KEY: {'Loaded [OK]' if openai_key else 'Not Found [MISSING]'}")
    print(f" - GROQ_API_KEY:   {'Loaded [OK]' if groq_key else 'Not Found [MISSING]'}\n")
    
    if not (google_key or openai_key or groq_key):
        print("[!] WARNING: No API keys found in .env file.")
        print("Please edit .env and add your API key before running LLM queries.\n")
        print("Example inside .env:")
        print("GOOGLE_API_KEY=your_gemini_api_key_here\n")
        return False

    # 2. Initialize LLM via LangChain
    try:
        print("[*] Initializing LangChain LLM instance...")
        llm = get_llm(temperature=0.7)
        print("[+] LLM initialized successfully!\n")
    except Exception as e:
        print(f"[X] Error initializing LLM: {e}")
        return False

    # 3. Create LangChain Prompt Template
    template = """
You are an expert YouTube Content Strategist.

Generate 5 creative, high-performing YouTube video title ideas for the following topic:
Topic: {topic}
Target Audience: {audience}
Tone: {tone}

Format output as a numbered list with a brief 1-line explanation for each title.
"""
    prompt_template = PromptTemplate(
        input_variables=["topic", "audience", "tone"],
        template=template
    )

    # 4. Construct LangChain Chain (Prompt | LLM)
    chain = prompt_template | llm

    # 5. Run Chain Test
    test_data = {
        "topic": "Artificial Intelligence in Healthcare",
        "audience": "Medical Students & Tech Enthusiasts",
        "tone": "Informative & Engaging"
    }

    print(f"[>] Sending Test Request:")
    print(f"   Topic:    {test_data['topic']}")
    print(f"   Audience: {test_data['audience']}")
    print(f"   Tone:     {test_data['tone']}\n")

    try:
        print("[*] Waiting for LLM response...")
        response = chain.invoke(test_data)
        
        print("\n==================================================")
        print(" SUCCESS! AI Response Received via LangChain:")
        print("==================================================\n")
        print(response.content)
        print("\n==================================================")
        print("[+] Week 2 Pipeline Verification: PASSED")
        print("==================================================")
        return True
    except Exception as e:
        print(f"\n[X] Pipeline Execution Failed: {e}")
        print("Please check your API key validity and network connection.")
        return False

if __name__ == "__main__":
    test_basic_llm_connection()
