# 🛠️ Week 2: Environment Setup & LLM Integration Report

---

## 1. Environment & Project Architecture

- **Project Folder**: `youtube-script-assistant`
- **GitHub Repository**: [https://github.com/Hetvi2211/youtube-script-assistant](https://github.com/Hetvi2211/youtube-script-assistant)
- **Python Version**: Python 3.10.11
- **Virtual Environment**: `venv` initialized and activated (`python -m venv venv`)
- **Key Isolation**: Secrets managed via `.env` and excluded from version control via `.gitignore`

---

## 2. Technology Stack & Package Selection

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | `>=1.30.0` | UI framework for future weeks |
| `langchain` | `>=0.2.0` | AI Orchestration & Chain abstractions |
| `langchain-core` | `>=0.2.0` | Base prompt & model interfaces |
| `langchain-google-genai` | `>=1.0.0` | Integration for Google Gemini LLM API |
| `langchain-openai` | `>=0.1.0` | Integration for OpenAI GPT models |
| `langchain-groq` | `>=0.1.0` | Integration for Groq / Llama 3 models |
| `python-dotenv` | `>=1.0.0` | Safe loading of `.env` API keys |

---

## 3. LLM Provider Rationale

### Selected Primary Provider: **Google Gemini API (`gemini-1.5-flash` / `gemini-2.0-flash`)**
*(Flexible fallback options configured for OpenAI and Groq in `modules/llm.py`)*

### Why API-Based LLM was Selected:
1. **Zero Hardware Overhead**: Runs smoothly without demanding an expensive local GPU.
2. **Superior Pacing & Quality**: Pre-trained models provide better creative video hooks and structured script formatting.
3. **High Context Window**: Gemini 1.5/2.0 Flash easily accommodates large prompt contexts (titles, scripts, feedback, scene breakdowns).
4. **Cost & Speed Efficiency**: Free tier via Google AI Studio ensures rapid development with low latency.

---

## 4. LangChain Integration & Pipeline Workflow

```text
User Input Parameters (Topic, Audience, Tone, Length, Style)
                    │
                    ▼
     langchain_core.prompts.PromptTemplate
                    │
                    ▼
          modules.llm.get_llm()
  (Auto-detects GOOGLE_API_KEY / OPENAI_API_KEY)
                    │
                    ▼
        RunnableSequence (Prompt | LLM)
                    │
                    ▼
            LLM API Response
                    │
                    ▼
      Formatted Output (Title & Script)
```

---

## 5. Security & Secret Protection

- `.env.example` provides the template for team members.
- `.env` stores actual private keys (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`).
- `.gitignore` explicitly prevents `.env` and `venv/` from ever being pushed to GitHub.

---

## 6. Verification & Test Scripts

1. `test_llm.py`: Verifies environment loading, API key presence, LLM initialization, and basic prompt execution.
2. `test_prompts.py`: Executes 4 distinct prompt parameter variations (Tech, Education, Humorous, Student Audience) to benchmark LLM responsiveness.

---

## 7. Week 2 Checklist Status

- [x] Python 3.10 installed & verified
- [x] Virtual environment (`venv`) created & activated
- [x] LangChain & LLM integrations installed (`requirements.txt`)
- [x] API key configuration established (`.env` & `modules/llm.py`)
- [x] `.env` protected via `.gitignore`
- [x] GitHub repository connected ([Hetvi2211/youtube-script-assistant](https://github.com/Hetvi2211/youtube-script-assistant))
- [x] Verification script created (`test_llm.py`)
- [x] Prompt experiments suite created (`test_prompts.py`)
- [x] Week 2 Documentation report generated (`docs/week2_setup_report.md`)
