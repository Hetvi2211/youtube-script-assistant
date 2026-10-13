# 🎬 YouTube Script Writing Assistant Using LangChain & Streamlit

An AI-powered web application built with **LangChain**, **Streamlit**, and **Large Language Models (LLMs)** to help YouTube content creators plan, generate, analyze, improve, break down, and export high-performing video scripts and YouTube SEO metadata.

---

## 🎯 Features

- 💡 **Catchy Title Generation**: Generate engaging YouTube titles tailored to your topic and tone.
- 📜 **Full Script Writing**: Produce structured video scripts featuring hooks, introductions, main body points, CTAs, and outros.
- ⚙️ **Custom Preferences**: Adjust target audience, tone, video duration, and content style.
- 🔍 **AI Script Analyzer**: Evaluate script hook strength, pacing, clarity, and visual appeal.
- ✨ **AI Script Improvement**: Iteratively polish and rewrite scripts based on AI analysis or user feedback.
- 🎬 **Scene Breakdown**: Automatically convert scripts into camera-ready production scene plans (Visuals, Audio, On-Screen Text).
- 📦 **YouTube Content Package**: Generate YouTube descriptions, target keywords, tags, hashtags, and CTAs.
- 💾 **Multi-Format Export**: Download complete outputs in **TXT**, **PDF**, or **DOCX** format.

---

## 🏗️ Architecture & Workflow

```text
User Input → Streamlit UI → Preference Configuration → LangChain Prompts → LLM API
                                                                             │
  ┌──────────────────────────────────────────────────────────────────────────┘
  ▼
Output Processing:
  ├── Title & Script Generation
  ├── AI Script Analysis
  ├── AI Script Improvement
  ├── Scene Breakdown
  └── YouTube Package (Description, Tags, Hashtags, CTA)
  │
  ▼
Export Engine (TXT / PDF / DOCX)
```

---

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Framework**: [LangChain](https://www.langchain.com/)
- **Language**: Python 3.10+
- **Export Libraries**: `python-docx`, `fpdf2` / `reportlab`
- **Configuration**: `python-dotenv`

---

## 🚀 Quick Start & Environment Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** and **Git** installed.

### 2. Clone Repository & Navigate
```bash
git clone https://github.com/YOUR_USERNAME/youtube-script-assistant.git
cd youtube-script-assistant
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Key
Copy `.env.example` to `.env` and add your LLM API Key:
```bash
# Windows PowerShell
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Edit `.env` and configure Groq as the active provider:
```env
GROQ_API_KEY=your_groq_api_key_here
```

The project still preserves optional OpenAI and Google provider support through
`modules/llm.py` when an explicit provider is passed to `get_llm()`.

### 6. Run Application
```bash
streamlit run app.py
```

---

## 📁 Repository Structure

```text
youtube-script-assistant/
│
├── app.py                      # Streamlit App Entrypoint
├── modules/                    # LangChain & Logic Modules
│   ├── llm.py                  # LLM setup & provider initialization
│   ├── prompts.py              # Prompt template definitions
│   ├── script_generator.py     # Script & Title chains
│   ├── script_analyzer.py      # Validated Week 7 script analysis chain
│   ├── script_improver.py      # Script refinement chain
│   ├── scene_generator.py      # Scene breakdown chain
│   ├── content_generator.py    # Description, tags & metadata chain
│   └── exporter.py             # Export generator (TXT/PDF/DOCX)
├── utils/                      # Helper utilities
│   └── helpers.py              # State & formatting utilities
├── docs/                       # Project Documentation
│   └── project_requirements.md
├── .env.example                # Sample environment file
├── .gitignore                  # Git ignore standard rules
├── requirements.txt            # Dependency list
└── README.md                   # Project Overview & Setup Guide
```

## 📊 Week 7: AI Script Analyzer

The Week 7 analyzer evaluates the currently active generated or edited script.
It does not analyze a sample script and it does not rewrite the script.

### Analyzer objectives and criteria

After the user clicks **Analyze Script**, the app sends the active script to
the existing LangChain LLM factory with the selected topic, audience, tone,
video length, and content style. The response is validated as structured JSON
and evaluated across:

1. Hook quality
2. Script structure
3. Audience suitability
4. Tone consistency
5. Repetition
6. Engagement
7. Call-to-action (CTA)
8. Clarity
9. Approximate reading time

The analyzer calculates word count and estimated narration time in Python at
the configurable default rate of 140 words per minute. Individual criteria use
a 0-10 scale. The overall score is the arithmetic mean of the nine criterion
scores, converted to 0-100; it is an AI-assisted estimate, not an objective
scientific measurement.

### Using the analyzer

1. Start the app with `streamlit run app.py`.
2. Enter a topic and preferences, then select **Generate Content**.
3. Open the **AI Script Analyzer** tab and select **Analyze Script**.
4. Review the overall score, assessment, criterion explanations, strengths,
   missing elements, and prioritized suggestions.
5. If the script is regenerated, edited, or restored, analyze it again. Older
   results are cleared and are never displayed as belonging to the new draft.

### Analysis output shape

The reusable `modules/script_analyzer.py` function returns a JSON-compatible
dictionary:

```text
{
  overall_score: number,
  overall_summary: string,
  criteria: [{criterion, score, rating, explanation, suggestion}],
  strengths: [string],
  improvement_suggestions: [string],
  missing_elements: [string],
  word_count: integer,
  estimated_reading_time_minutes: number
}
```

Malformed or incomplete LLM JSON, unsupported responses, missing API
configuration, and provider/network failures produce an explicit user-facing
error. The analyzer never invents a successful fallback report.

### Week 7 tests

Week 7 tests use mocked LangChain responses and do not consume API credits:

```bash
python -m unittest -v test_script_analyzer.py
```

The suite covers strong and weak hooks, missing CTAs, repetition, empty and
short scripts, different preferences, malformed output, LLM failure, and
stale analysis after regeneration.

---

## 👥 Team 
- Dhara Patel 
- Hetvi Rabari 
