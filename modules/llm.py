"""
llm.py
Initializes the Language Model interface using LangChain.
Supports switching between Google Gemini, OpenAI, and Groq providers.
"""

import os
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

# Load environment variables from .env file
load_dotenv()

DEFAULT_PROVIDER = "groq"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


def get_llm(provider: str = None, model_name: str = None, temperature: float = 0.7) -> BaseChatModel:
    """
    Returns an initialized LangChain LLM instance based on available API keys or specified provider.
    
    Supported providers:
    - 'google' or 'gemini': Uses langchain-google-genai (Gemini 1.5/2.0 Flash)
    - 'openai': Uses langchain-openai (GPT-4o-mini / GPT-4o)
    - 'groq': Uses langchain-groq (Llama 3.3 70B)
    """
    
    # Groq is the active default; explicit provider arguments remain supported.
    if not provider:
        provider = DEFAULT_PROVIDER
            
    provider = provider.lower()
    
    if provider in ["google", "gemini"]:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            selected_model = model_name or "gemini-1.5-flash"
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY is missing in .env file.")
            return ChatGoogleGenerativeAI(
                model=selected_model,
                temperature=temperature,
                google_api_key=api_key
            )
        except ImportError:
            raise ImportError("Please install langchain-google-genai: pip install langchain-google-genai")
            
    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            selected_model = model_name or "gpt-4o-mini"
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is missing in .env file.")
            return ChatOpenAI(
                model=selected_model,
                temperature=temperature,
                openai_api_key=api_key
            )
        except ImportError:
            raise ImportError("Please install langchain-openai: pip install langchain-openai")

    elif provider == "groq":
        try:
            from langchain_groq import ChatGroq
            selected_model = model_name or DEFAULT_GROQ_MODEL
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY is missing in .env file. "
                    "Add your Groq API key to the local .env file."
                )
            return ChatGroq(
                model_name=selected_model,
                temperature=temperature,
                groq_api_key=api_key
            )
        except ImportError:
            raise ImportError("Please install langchain-groq: pip install langchain-groq")

    else:
        raise ValueError(f"Unsupported provider '{provider}'. Choose from 'google', 'openai', or 'groq'.")
