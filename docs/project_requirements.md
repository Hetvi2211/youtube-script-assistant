# YouTube Script Writing Assistant Using LangChain and Streamlit
## Week 1: Project Planning & Requirement Analysis Document

---

## 1. Final Project Title
**YouTube Script Writing Assistant Using LangChain and Streamlit**

---

## 2. Project Idea
The project is a **Generative AI-based web application** designed to empower YouTube content creators in generating, analyzing, improving, and structuring video scripts and metadata.

The user provides a video topic along with key preferences such as:
- **Target Audience** (e.g., Beginners, Tech Enthusiasts, Students)
- **Tone** (e.g., Casual, Professional, Humorous, Inspirational)
- **Video Length** (e.g., 2 mins, 5 mins, 10 mins, 15+ mins)
- **Content Style** (e.g., Storytelling, Step-by-Step Tutorial, Listicle, Review)

Using **LangChain** and a **Large Language Model (LLM)**, the system generates optimized video titles and a structured script. Users can then perform AI-driven script analysis, automatic script enhancement, scene-by-scene breakdown generation, and export a complete YouTube metadata package (Description, Tags, Hashtags, Call-to-Action).

---

## 3. Problem Statement
Creating high-performing YouTube content demands substantial effort across multiple stages:
1. **Ideation & Title Creation**: Finding hook-driven, SEO-friendly titles.
2. **Script Structure**: Maintaining viewer retention through structured hooks, intros, main body points, and CTAs.
3. **Pacing & Production Planning**: Converting scripts into practical scene breakdowns for recording/editing.
4. **Metadata Optimization**: Crafting YouTube-optimized descriptions, tags, and hashtags for search visibility.

Existing AI writers provide generic text generation without tailored YouTube workflows or iterative script analysis and breakdown. This project delivers a unified, single-window assistant tailored specifically for video content creators.

---

## 4. Proposed Solution & Main Workflow

```text
[ Enter Topic ] 
     ↓
[ Select Preferences: Audience / Tone / Length / Style ]
     ↓
[ Generate Title + Full Script ]
     ↓
[ AI Script Analyzer (Pacing, Structure, Engagement Check) ]
     ↓
[ AI Script Improvement (Refine Hooks, Tone Alignment) ]
     ↓
[ Scene-by-Scene Video Production Plan ]
     ↓
[ Generate YouTube Metadata Package (Description, Tags, Hashtags, CTA) ]
     ↓
[ Export Content (TXT, PDF, DOCX) ]
```

---

## 5. Project Goal
> **To develop an AI-powered YouTube content assistant using LangChain and Large Language Models to generate, analyze, improve, and structure video content based on user requirements.**

---

## 6. Project Objectives
1. Develop an interactive **Streamlit-based UI**.
2. Integrate an LLM via **LangChain**.
3. Generate engaging, SEO-optimized **YouTube Video Titles**.
4. Generate comprehensive, structured **YouTube Video Scripts**.
5. Enable full preference customization (Audience, Tone, Length, Style).
6. Maintain **conversation history** for iterative script refinement.
7. Perform automated **AI Script Analysis** (Readability, Hook Strength, Key Takeaways).
8. Provide **AI Script Improvement** suggestions and one-click script enhancements.
9. Produce **Scene-wise Breakdowns** (Visuals, Audio/Voiceover, On-screen text, Timestamps).
10. Generate full **YouTube Packages** (Description, Keywords/Tags, Hashtags, Call-to-Action).
11. Enable multi-format **Export options** (TXT, PDF, DOCX).

---

## 7. Scope of the Project

### In Scope
- **Core Engine**: Topic input, parameter controls (Audience, Tone, Length, Style), AI title generator, AI script generator, LangChain prompt templates, conversation memory.
- **Advanced Features**: Script analyzer, automatic script improver, scene breakdown generator, YouTube SEO content package generator, document exporter.
- **Interface**: Clean, responsive Streamlit dashboard.

### Out of Scope (Future Scope)
- Automatic video rendering or editing
- Automated YouTube API uploading
- Full channel analytics & view tracking
- Custom LLM model training / fine-tuning
- Native text-to-speech / voice generation

---

## 8. Target Users
- **YouTube Content Creators**: Channels looking to streamline their scripting pipeline.
- **Beginner YouTubers**: Creators needing structured script guidance and SEO metadata assistance.
- **Educational Content Creators & Students**: Presenters producing structured tutorials.
- **Freelance Scriptwriters**: Copywriters seeking AI-assisted drafting tools.
- **Social Media Managers**: Teams producing multi-platform video content.

---

## 9. Functional Requirements (FR)

| ID | Requirement | Description |
|---|---|---|
| **FR-01** | Topic Input | Accept user video topic string |
| **FR-02** | Target Audience Selection | Accept specified audience profile |
| **FR-03** | Tone Selection | Accept tone configuration (Informative, Humorous, Serious, etc.) |
| **FR-04** | Video Length | Accept target duration (e.g., Short <3 min, Medium 5-10 min, Long 10-15+ min) |
| **FR-05** | Content Style | Accept format style (Tutorial, Storytelling, Top 5 List, Deep-dive) |
| **FR-06** | Title Generation | Generate 3-5 catchy YouTube title options |
| **FR-07** | Script Generation | Generate a full script with Hook, Intro, Body, CTA, and Outro |
| **FR-08** | Session Memory | Retain conversation history for follow-up prompts and adjustments |
| **FR-09** | Script Analyzer | Evaluate script hook strength, tone consistency, and visual feasibility |
| **FR-10** | Script Improver | Rewrite or refine script sections based on feedback or AI analysis |
| **FR-11** | Scene Breakdown | Generate table of Visuals, Audio Cue, Text Overlay per scene |
| **FR-12** | YouTube Description | Generate SEO-optimized video description |
| **FR-13** | Keywords & Tags | Generate copyable YouTube tag list |
| **FR-14** | Hashtags | Generate top relevant hashtags |
| **FR-15** | Call To Action | Generate high-converting CTA prompts |
| **FR-16** | Export Functionality | Download final package in TXT, PDF, or DOCX formats |
| **FR-17** | Input Validation | Handle empty/invalid user inputs gracefully |
| **FR-18** | Error Handling | Display clear warning/error toasts for API or network issues |

---

## 10. Non-Functional Requirements (NFR)

- **Usability**: Intuitive UI with sidebar controls and formatted output tabs/cards.
- **Performance**: Asynchronous/streamed LLM responses with minimal visual delay.
- **Reliability**: Graceful error handling for rate limits, API key failures, and timeout errors.
- **Security**: Environment variable configuration (`.env`) ensuring zero API key exposure.
- **Maintainability**: Modular Python architecture adhering to clean single-responsibility modules.
- **Scalability**: Decoupled LLM layer allowing seamless swapping between model providers (OpenAI, Gemini, Groq, Anthropic).

---

## 11. Technology Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Frontend Framework** | Streamlit |
| **AI Orchestration Framework** | LangChain (`langchain-core`, `langchain-community`) |
| **LLM Provider** | OpenAI (GPT-4o/GPT-4o-mini) OR Google Gemini (Gemini 1.5/2.0) OR Groq (Llama 3.3) |
| **Prompt Engineering** | LangChain `PromptTemplate` & `ChatPromptTemplate` |
| **Session Memory** | Streamlit `st.session_state` & LangChain Memory abstractions |
| **Configuration** | `python-dotenv` |
| **Export Engines** | `python-docx` (DOCX), `fpdf2` or `reportlab` (PDF) |
| **IDE / Version Control** | VS Code, Git, GitHub |

---

## 12. System Architecture

```text
                    ┌───────────────────┐
                    │      USER         │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   STREAMLIT UI    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ USER PREFERENCES  │
                    │ - Topic           │
                    │ - Target Audience │
                    │ - Tone            │
                    │ - Video Length    │
                    │ - Content Style   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ PROMPT TEMPLATES  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     LANGCHAIN     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      LLM API      │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
    TITLE & SCRIPT      SCRIPT ANALYZER     CONTENT PACKAGE
         │                    │                    │
         ▼                    ▼                    ▼
    IMPROVEMENT          ANALYSIS REPORT     DESCRIPTION & TAGS
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌───────────────────┐
                    │  SCENE BREAKDOWN  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ EXPORT ENGINE     │
                    │ (TXT, PDF, DOCX)  │
                    └───────────────────┘
```

---

## 13. Team Division & Task Allocation

### Member 1: AI / Backend Lead
- **LLM Setup & Integration**: Configuring LangChain chains and API connections.
- **Prompt Engineering**: Designing system templates for titles, scripts, analysis, and metadata.
- **Core Logic Modules**: Writing `llm.py`, `script_generator.py`, `script_analyzer.py`, `script_improver.py`, `scene_generator.py`, `content_generator.py`.
- **Memory & State Logic**: Managing prompt context and history logic.

### Member 2: UI / Frontend & Integration Lead
- **Streamlit Layout**: Creating sidebar controls, tabbed views, script cards, and control buttons.
- **Export Engine**: Implementing `exporter.py` for TXT, PDF, and DOCX format building.
- **State Integration**: Wiring Streamlit `session_state` to LLM output modules.
- **Testing & UX**: Performing edge-case testing, error formatting, and user experience polish.

### Joint Responsibilities
- Requirement analysis & architecture validation
- System testing & debugging
- Documentation & presentation slides
- Final viva preparation

---

## 14. Project Folder Structure

```text
youtube-script-assistant/
│
├── app.py                      # Main Streamlit application entry point
│
├── modules/                    # Core business logic modules
│   ├── __init__.py
│   ├── llm.py                  # LLM provider initialization & setup
│   ├── prompts.py              # Prompt templates collection
│   ├── script_generator.py     # Title & script generation chains
│   ├── script_analyzer.py      # AI script analysis chain
│   ├── script_improver.py      # AI script improvement chain
│   ├── scene_generator.py      # Scene-wise breakdown chain
│   ├── content_generator.py    # Description, tags, hashtags, CTA generator
│   └── exporter.py             # Export to TXT, PDF, DOCX utilities
│
├── utils/                      # Helper & state management functions
│   ├── __init__.py
│   └── helpers.py              # UI helpers, formatting functions
│
├── docs/                       # Project documentation
│   └── project_requirements.md # Comprehensive Week 1 requirements doc
│
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # Project summary and setup guide
```
