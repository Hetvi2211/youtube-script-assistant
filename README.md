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
Edit `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
# OR
GOOGLE_API_KEY=your_google_gemini_api_key_here
# OR
GROQ_API_KEY=your_groq_api_key_here
```

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
│   ├── script_analyzer.py      # Script analysis chain
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

---

## 👥 Team Responsibilities

- **Member 1 (AI / Backend Lead)**: LLM setup, LangChain integration, prompt engineering, script analysis/improvement/scene generation logic.
- **Member 2 (UI / Frontend Lead)**: Streamlit UI construction, export engine integration, state management, UI testing.
