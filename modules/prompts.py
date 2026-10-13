"""
prompts.py
LangChain Prompt Templates for YouTube Content Generation Pipeline.
Contains prompt definitions for Titles, Hooks, Scripts, Analysis,
Script Improvements, Scene Breakdowns, Descriptions, and SEO Metadata.
"""

from langchain_core.prompts import PromptTemplate

# ==========================================
# 1. YouTube Title Generator Prompt
# ==========================================
TITLE_PROMPT_TEMPLATE = """You are an expert YouTube content strategist and viral headline designer.

Generate 5 high-converting, click-worthy YouTube video titles based on the following requirements:

Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Content Style: {style}

Requirements:
- Make the titles highly relevant to the topic and tailored to the target audience.
- Use proven hook patterns (curiosity gaps, high stakes, clear value, numbers, or questions).
- Avoid misleading clickbait; keep titles honest to the content.
- Keep titles punchy and within 70 characters for YouTube display.

Output Format:
Return a numbered list of 5 titles. Under each title, add a 1-sentence explanation of why it will perform well.
"""

TITLE_PROMPT = PromptTemplate(
    input_variables=["topic", "audience", "tone", "style"],
    template=TITLE_PROMPT_TEMPLATE
)


# ==========================================
# 2. Hook Generator Prompt
# ==========================================
HOOK_PROMPT_TEMPLATE = """You are an expert YouTube script writer specializing in viewer retention and video openings.

Generate 5 distinct YouTube video hooks (the first 15-30 seconds of the video) for:
Topic: {topic}
Target Audience: {audience}
Tone: {tone}

Create 5 different hook styles:
1. Question Hook (Asks a thought-provoking question)
2. Curiosity Hook (Teases a surprising secret or revelation)
3. Story Hook (Starts with a short, captivating anecdote)
4. Surprising Fact / Stat Hook (Leads with a shocking data point or reality)
5. Problem-based Hook (Directly addresses a major pain point of the audience)

Requirements:
- Keep each hook concise (30-60 words max).
- Write in natural, spoken conversational English.
- Provide clear visual/delivery instructions in brackets [like this].
"""

HOOK_PROMPT = PromptTemplate(
    input_variables=["topic", "audience", "tone"],
    template=HOOK_PROMPT_TEMPLATE
)


# ==========================================
# 3. Full YouTube Script Generator Prompt
# ==========================================
SCRIPT_PROMPT_TEMPLATE = """You are a world-class YouTube content creator and scriptwriter.

Write a complete, high-retention YouTube video script based on the following requirements:

Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Video Length: {length}
Content Style: {style}

Speaking Time & Word Count Guide:
- Short (< 3 mins): ~350 - 450 words
- Medium (5 - 10 mins): ~700 - 1100 words
- Long (10 - 15+ mins): ~1300 - 1800 words
Target word count range for this request: Adjust word density to fit {length}.

Structure the script cleanly with the following section headers:
1. [TITLE SUGGESTION]
2. [HOOK] (0:00 - 0:30)
3. [INTRODUCTION] (Set expectations & channel branding hint)
4. [MAIN CONTENT] (Divided into clear sub-points with visual cues in brackets [Visual: ...])
5. [PRACTICAL EXAMPLES / DEMO]
6. [CONCLUSION & RECAP]
7. [CALL-TO-ACTION & OUTRO]

Requirements:
- Match the requested tone ({tone}) and engage the specific target audience ({audience}).
- Include spoken dialogue along with production notes in brackets like [Visual: ...], [Sound Effect: ...], [On-screen text: ...].
- Ensure smooth transitions between key points to maximize viewer retention.
- Avoid repetitive fluff or artificial filler text.
"""

SCRIPT_PROMPT = PromptTemplate(
    input_variables=["topic", "audience", "tone", "length", "style"],
    template=SCRIPT_PROMPT_TEMPLATE
)


# ==========================================
# 4. Script Analyzer Prompt (Week 7)
# ==========================================
ANALYZER_PROMPT_TEMPLATE = """You are a senior YouTube content consultant and retention analyst.

Analyze only the supplied script. Do not rewrite it and do not use a sample script.

Context:
- Topic: {topic}
- Target audience: {audience}
- Requested tone: {tone}
- Requested video length: {video_length}
- Content style: {content_style}
- Python-calculated word count: {word_count}
- Python-calculated estimated reading time in minutes: {estimated_reading_time_minutes}

=== SCRIPT START ===
{script}
=== SCRIPT END ===

Evaluate exactly these nine criteria:
1. Hook Quality
2. Script Structure
3. Audience Suitability
4. Tone Consistency
5. Repetition
6. Engagement
7. Call-to-Action (CTA)
8. Clarity
9. Approximate Reading Time

Return ONLY one valid JSON object. Do not wrap it in Markdown fences. Use this exact shape:
{{
  "overall_score": 0,
  "overall_summary": "concise assessment",
  "criteria": [
    {{
      "criterion": "Hook Quality",
      "score": 0,
      "rating": "Poor",
      "explanation": "evidence from this script",
      "suggestion": "specific action for this script"
    }}
  ],
  "strengths": ["specific strength"],
  "improvement_suggestions": ["highest-priority actionable suggestion"],
  "missing_elements": ["important element absent from this script"]
}}

Use a 0-10 score for every criterion and a rating such as Poor, Fair, Good, or Excellent.
The application calculates word count, reading time, and the overall score in Python.
Mention a missing CTA in missing_elements only when this script truly lacks a CTA.
Recommendations must refer to evidence in the supplied script, not generic advice.
"""

ANALYZER_PROMPT = PromptTemplate(
    input_variables=[
        "script",
        "topic",
        "audience",
        "tone",
        "video_length",
        "content_style",
        "word_count",
        "estimated_reading_time_minutes",
    ],
    template=ANALYZER_PROMPT_TEMPLATE
)


# ==========================================
# 5. Script Improvement Prompt
# ==========================================
IMPROVEMENT_PROMPT_TEMPLATE = """You are a master YouTube script editor.

Revise and polish the original YouTube script using the provided AI analysis report and improvement suggestions.

Original Script:
=== SCRIPT START ===
{script}
=== SCRIPT END ===

Analysis & Improvement Suggestions:
=== ANALYSIS START ===
{analysis}
=== ANALYSIS END ===

User Custom Feedback / Directives (if any):
{user_feedback}

Requirements:
- Preserve the core topic, valuable insights, and structural intent.
- Fix all identified weaknesses (strengthen the hook, remove fluff, smooth out transitions, sharpen CTA).
- Enhance visual and audio production cues in brackets [Visual: ...].
- Maintain spoken conversational delivery suitable for video.
- Return the full, newly improved and ready-to-record YouTube script.
"""

IMPROVEMENT_PROMPT = PromptTemplate(
    input_variables=["script", "analysis", "user_feedback"],
    template=IMPROVEMENT_PROMPT_TEMPLATE
)


# ==========================================
# 6. Scene-wise Breakdown Prompt
# ==========================================
SCENE_PROMPT_TEMPLATE = """You are a professional video production assistant and director.

Convert the following YouTube video script into a detailed, scene-by-scene production shot list table.

=== SCRIPT START ===
{script}
=== SCRIPT END ===

Output Requirements:
Break down the script sequentially into scenes. Format as a clean markdown table with these columns:
- Scene #
- Timecode (Approx. MM:SS - MM:SS)
- Voiceover / Spoken Script
- Visual Suggestion (Camera shot, B-roll, animation, stock footage)
- On-Screen Text / Graphics
- Audio & SFX Cues

Ensure the scene count logically covers the entire script from start to finish.
"""

SCENE_PROMPT = PromptTemplate(
    input_variables=["script"],
    template=SCENE_PROMPT_TEMPLATE
)


# ==========================================
# 7. YouTube Description Generator Prompt
# ==========================================
DESCRIPTION_PROMPT_TEMPLATE = """You are a YouTube SEO specialist and copywriter.

Write a high-converting, SEO-optimized YouTube video description based on:

Video Title: {title}
Target Audience: {audience}
Script Summary / Content:
=== SCRIPT ===
{script}
=== END SCRIPT ===

Structure the description as follows:
1. [ABOVE THE FOLD SUMMARY] (First 2 lines: compelling summary with primary target keyword included naturally for search previews)
2. [VIDEO TIMESTAMPS / CHAPTERS] (Estimated 3-6 chapter markers based on script sections)
3. [KEY TAKEAWAYS] (3-4 bullet points summarizing what viewers will learn)
4. [RESOURCES & LINKS PLACEHOLDERS]
5. [CALL TO ACTION] (Encourage subscribe, like, comment, and newsletter/social check)

Keep language natural, professional, and SEO-friendly without keyword stuffing.
"""

DESCRIPTION_PROMPT = PromptTemplate(
    input_variables=["title", "audience", "script"],
    template=DESCRIPTION_PROMPT_TEMPLATE
)


# ==========================================
# 8. Keywords, Tags & Hashtags Generator Prompt
# ==========================================
METADATA_PROMPT_TEMPLATE = """You are a YouTube Metadata & SEO Optimizer.

Generate a comprehensive metadata package (Keywords, Tags, Hashtags, CTA Copy) based on:

Topic: {topic}
Video Title: {title}
Script Content:
=== SCRIPT ===
{script}
=== END SCRIPT ===

Format the output strictly into 4 distinct sections:

1. KEYWORDS (10 High-intent search terms / phrases)
2. YOUTUBE TAGS (15 comma-separated tags formatted ready to copy-paste into YouTube Studio tag box)
3. HASHTAGS (10 relevant hashtags starting with #)
4. CALL-TO-ACTION (CTA) VARIATIONS (3 high-converting spoken/on-screen CTA scripts for subscribers & engagement)
"""

METADATA_PROMPT = PromptTemplate(
    input_variables=["topic", "title", "script"],
    template=METADATA_PROMPT_TEMPLATE
)


# ==========================================
# 9. Context-Aware Conversational Refinement Prompt (Week 6)
# ==========================================
CONTEXT_REFINEMENT_PROMPT_TEMPLATE = """You are an expert YouTube script writing assistant and video producer.

You are collaborating interactively with a content creator to refine and improve their YouTube video script.

CURRENT ACTIVE SCRIPT:
=== SCRIPT START ===
{current_script}
=== SCRIPT END ===

PREVIOUS CONVERSATION HISTORY:
{conversation_history}

USER REVISION REQUEST:
"{user_instruction}"

ADDITIONAL CONTEXT / PREFERENCES:
- Topic: {topic}
- Target Audience: {audience}
- Tone: {tone}

INSTRUCTIONS:
1. Carefully analyze what the user is asking to modify (e.g., make intro punchier, shorten section, add humor, add examples, explain a concept differently, etc.).
2. Apply the requested changes contextually while preserving the overall continuity and valuable insights of the script.
3. Keep spoken dialogue conversational and retain visual/audio cues like [Visual: ...] or [Sound Effect: ...].
4. Return:
   - A brief 1-2 sentence summary of what was updated.
   - Followed by the updated script (or the specifically requested revised section, or full script if comprehensive changes were requested) clearly delimited.
"""

CONTEXT_REFINEMENT_PROMPT = PromptTemplate(
    input_variables=["current_script", "conversation_history", "user_instruction", "topic", "audience", "tone"],
    template=CONTEXT_REFINEMENT_PROMPT_TEMPLATE
)


# ==========================================
# 10. Regenerate Full Script Prompt (Week 6)
# ==========================================
REGENERATE_SCRIPT_PROMPT_TEMPLATE = """You are a top-tier YouTube scriptwriter.

The user wants a completely fresh, alternative take on their YouTube video script.
Explore a different creative angle, fresh hook, and unique examples while keeping the core preferences:

Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Video Length: {length}
Content Style: {style}

Structure the script cleanly:
1. [TITLE SUGGESTION]
2. [HOOK] (0:00 - 0:30)
3. [INTRODUCTION]
4. [MAIN CONTENT] (With [Visual: ...] cues)
5. [PRACTICAL EXAMPLES / DEMO]
6. [CONCLUSION & RECAP]
7. [CALL-TO-ACTION & OUTRO]

Requirements:
- Ensure this is a distinct, fresh creative perspective from common clichés.
- High retention, punchy delivery, natural spoken cadence.
"""

REGENERATE_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["topic", "audience", "tone", "length", "style"],
    template=REGENERATE_SCRIPT_PROMPT_TEMPLATE
)


# ==========================================
# 11. Quick Modification: Shorten Script Prompt (Week 6)
# ==========================================
SHORTEN_SCRIPT_PROMPT_TEMPLATE = """You are an expert YouTube editor specializing in fast pacing and retention.

Shorten and condense the following YouTube script:

=== CURRENT SCRIPT ===
{script}
=== END SCRIPT ===

Requirements:
- Reduce the word count by approximately 25-35%.
- Remove all fluff, unnecessary repetition, and slow explanations.
- Keep the hook sharp and retain the core takeaways and CTA.
- Keep the spoken delivery fast, punchy, and engaging.
- Return the full revised, condensed script with production cues.
"""

SHORTEN_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["script"],
    template=SHORTEN_SCRIPT_PROMPT_TEMPLATE
)


# ==========================================
# 12. Quick Modification: Expand Script Prompt (Week 6)
# ==========================================
EXPAND_SCRIPT_PROMPT_TEMPLATE = """You are an expert YouTube scriptwriter specializing in deep-dive educational content.

Expand and elaborate on the following YouTube script:

=== CURRENT SCRIPT ===
{script}
=== END SCRIPT ===

Requirements:
- Add more depth, richer explanations, analogies, and detailed points.
- Increase the depth of the main content points without adding empty filler.
- Include additional production/visual cues [Visual: ...] to maintain visual interest across the longer video.
- Return the full expanded script.
"""

EXPAND_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["script"],
    template=EXPAND_SCRIPT_PROMPT_TEMPLATE
)


# ==========================================
# 13. Quick Modification: Change Tone Prompt (Week 6)
# ==========================================
CHANGE_TONE_PROMPT_TEMPLATE = """You are a versatile YouTube scriptwriter.

Rewrite the following YouTube script to adopt a new tone:
TARGET TONE: {target_tone}

=== CURRENT SCRIPT ===
{script}
=== END SCRIPT ===

Requirements:
- Adapt the vocabulary, sentence cadence, humor level, and energy to authentically match the target tone: {target_tone}.
- Keep all factual information, core structure, and main points intact.
- Return the complete rewritten script in the new tone.
"""

CHANGE_TONE_PROMPT = PromptTemplate(
    input_variables=["script", "target_tone"],
    template=CHANGE_TONE_PROMPT_TEMPLATE
)


# ==========================================
# 14. Quick Modification: Improve Hook & Intro Prompt (Week 6)
# ==========================================
IMPROVE_INTRO_PROMPT_TEMPLATE = """You are an elite YouTube retention specialist.

The first 30 seconds of a YouTube video make or break viewer retention.
Rewrite and supercharge the [HOOK] and [INTRODUCTION] of the following script:

=== CURRENT SCRIPT ===
{script}
=== END SCRIPT ===

Requirements:
- Create an irresistible opening hook (curiosity gap, high-stakes question, or shocking fact).
- Set clear payoff expectations in the introduction within 15-20 seconds.
- Provide vivid visual & sound effect cues in brackets [Visual: ...], [SFX: ...].
- Output the full script with the newly enhanced Hook and Introduction integrated seamlessly.
"""

IMPROVE_INTRO_PROMPT = PromptTemplate(
    input_variables=["script"],
    template=IMPROVE_INTRO_PROMPT_TEMPLATE
)


# ==========================================
# 15. Quick Modification: Add Examples Prompt (Week 6)
# ==========================================
ADD_EXAMPLES_PROMPT_TEMPLATE = """You are an expert YouTube content creator.

Enhance the following YouTube script by adding concrete, relatable real-world examples, case studies, or step-by-step demonstrations:

=== CURRENT SCRIPT ===
{script}
=== END SCRIPT ===

Requirements:
- Weave in 2-3 specific, illustrative real-world examples or scenarios into the main content.
- Ensure the examples make abstract concepts immediately understandable and interesting to viewers.
- Return the full updated script with the new examples seamlessly integrated.
"""

ADD_EXAMPLES_PROMPT = PromptTemplate(
    input_variables=["script"],
    template=ADD_EXAMPLES_PROMPT_TEMPLATE
)
