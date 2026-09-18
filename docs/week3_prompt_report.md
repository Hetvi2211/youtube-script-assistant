# 🎯 Week 3: Prompt Engineering & Prompt Template Report

---

## 1. Executive Summary

In Week 3, we developed a modular **8-stage LangChain Prompt System** for the YouTube Script Writing Assistant. Rather than relying on a single monolithic prompt, the system separates responsibility into specialized prompts:
1. **Title Generator Prompt**
2. **Hook Generator Prompt**
3. **Full Script Generator Prompt**
4. **Script Analyzer Prompt**
5. **Script Improver Prompt**
6. **Scene-wise Production Breakdown Prompt**
7. **YouTube Description Generator Prompt**
8. **SEO Metadata (Keywords, Tags, Hashtags, CTA) Prompt**

---

## 2. Core User Input Parameters

Every prompt chain dynamically accepts 5 standardized user input variables:

| Input Variable | Example Value | Function |
|---|---|---|
| `{topic}` | Artificial Intelligence in Healthcare | Primary domain/theme |
| `{audience}` | Medical Students & Tech Enthusiasts | Vocabulary and depth tuner |
| `{tone}` | Informative & Engaging | Emotional resonance and delivery style |
| `{length}` | Medium (5 - 10 mins) | Word density target (~700 - 1100 words) |
| `{style}` | Step-by-Step Tutorial | Narrative structure & format |

---

## 3. Prompt Architecture & Modular Design

```text
                           USER INPUTS
        (Topic, Target Audience, Tone, Length, Content Style)
                                │
                                ▼
                       modules/prompts.py
  (8 Specialized LangChain PromptTemplates / ChatPromptTemplates)
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
[Title & Hook Chains]   [Script Generator]      [Script Analyzer]
  (script_generator)     (script_generator)      (script_analyzer)
       │                        │                        │
       ▼                        ▼                        ▼
Titles & 5 Hook Types    Full Raw Script       Retention Matrix & Ratings
                                │                        │
                                └────────────┬───────────┘
                                             ▼
                                   [Script Improver]
                                   (script_improver)
                                             │
                                             ▼
                                  Polished Final Script
                                             │
       ┌─────────────────────────────────────┼─────────────────────────────────────┐
       ▼                                     ▼                                     ▼
[Scene Breakdown Chain]           [Description Generator]                [Metadata Package Chain]
   (scene_generator)                (content_generator)                     (content_generator)
       │                                     │                                     │
       ▼                                     ▼                                     ▼
Scene-by-Scene Shot Table           SEO Description & Chapters            Keywords, Tags & Hashtags
```

---

## 4. Summary of the 8 Prompt Templates

### Prompt 1: Title Generator (`TITLE_PROMPT`)
- **Inputs**: `topic`, `audience`, `tone`, `style`
- **Output**: 5 click-worthy, sub-70 character YouTube titles with performance rationales.

### Prompt 2: Hook Generator (`HOOK_PROMPT`)
- **Inputs**: `topic`, `audience`, `tone`
- **Output**: 5 retention-focused hook variations (Question, Curiosity, Story, Surprising Stat, Problem-focused).

### Prompt 3: Full Script Generator (`SCRIPT_PROMPT`)
- **Inputs**: `topic`, `audience`, `tone`, `length`, `style`
- **Output**: Complete script structured into Title, Hook, Intro, Main Body, Practical Demo, Conclusion, and CTA, with spoken dialogue and embedded `[Visual: ...]` / `[Sound Effect: ...]` cues.

### Prompt 4: Script Retention Analyzer (`ANALYZER_PROMPT`)
- **Inputs**: `script`
- **Output**: Evaluation matrix rating 8 key metrics (Hook Quality, Structure, Audience Fit, Tone, Clarity, Engagement, Fluff Check, CTA Strength) + 5 actionable recommendations.

### Prompt 5: Script Improver (`IMPROVEMENT_PROMPT`)
- **Inputs**: `script`, `analysis`, `user_feedback`
- **Output**: Fully rewritten, high-retention script fixing identified flaws while preserving core insights.

### Prompt 6: Scene-wise Production Breakdown (`SCENE_PROMPT`)
- **Inputs**: `script`
- **Output**: Sequential production markdown shot list table (Scene #, Timecode, Voiceover, Visual Suggestion, On-Screen Text, SFX).

### Prompt 7: YouTube Description Generator (`DESCRIPTION_PROMPT`)
- **Inputs**: `title`, `audience`, `script`
- **Output**: SEO-optimized description featuring an above-the-fold summary, estimated chapter markers, key takeaways, and CTAs.

### Prompt 8: Keywords, Tags & Hashtags Package (`METADATA_PROMPT`)
- **Inputs**: `topic`, `title`, `script`
- **Output**: 10 High-intent Keywords, 15 copyable YouTube Tags, 10 Hashtags, and 3 Spoken CTA variations.

---

## 5. Prompt Evaluation & Quality Matrix

| Prompt Module | Test Topic | Audience | Observed Quality | Key Strengths & Observations |
|---|---|---|---|---|
| **Title Generator** | AI in Healthcare | Medical Students | Excellent | Punchy titles under 70 chars; strong curiosity angles. |
| **Hook Generator** | Python for Beginners | College Students | Excellent | Clearly distinct hook styles (Question vs. Surprising Stat). |
| **Script Generator** | Web Dev with AI | Developers | Good | Good word count density; embedded visual cues are clear. |
| **Script Analyzer** | AI in Healthcare | General Audience | Excellent | Pinpoints missing CTAs and pacing drag with actionable fixes. |
| **Script Improver** | AI in Healthcare | Medical Students | Excellent | Successfully integrates analysis feedback into polished script. |
| **Scene Breakdown** | Machine Learning Bugs | Junior Devs | Good | Converts paragraphs into clean production shot lists. |
| **Description** | Python Beginners | Students | Good | Generates accurate chapter markers and SEO summary. |
| **Metadata Package**| AI in Healthcare | Medical Students | Excellent | Produces copy-paste ready tags and high-intent hashtags. |

---

## 6. Code Architecture Checklist

- [x] All 8 prompt templates encapsulated in `modules/prompts.py`
- [x] Title & Script chains built in `modules/script_generator.py`
- [x] Script retention analyzer chain built in `modules/script_analyzer.py`
- [x] Script improver chain built in `modules/script_improver.py`
- [x] Scene production plan chain built in `modules/scene_generator.py`
- [x] Description & SEO package chains built in `modules/content_generator.py`
- [x] Full integration verification script created (`test_week3.py`)
