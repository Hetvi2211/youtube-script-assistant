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
# 4. Script Analyzer Prompt
# ==========================================
ANALYZER_PROMPT_TEMPLATE = """You are a senior YouTube content consultant and retention analyst.

Thoroughly analyze the following YouTube video script:

=== SCRIPT START ===
{script}
=== SCRIPT END ===

Evaluate the script across 8 core metrics:
1. Hook Quality (Does it grab attention in the first 10 seconds?)
2. Structure & Pacing (Does the flow logical without drag?)
3. Audience Fit (Is the vocabulary and depth suited for the intended viewer?)
4. Tone Consistency (Is the tone steady throughout?)
5. Clarity & Understandability (Are complex ideas explained simply?)
6. Engagement & Visual Variety (Are visual/audio cues used effectively?)
7. Repetition & Fluff Check (Is there unnecessary filler?)
8. Call-to-Action (CTA) Strength (Is the ending action clear and compelling?)

Output Format:
- Provide a summary table with Ratings for each metric (Poor / Fair / Good / Excellent) and a 1-sentence rationale.
- List 3 major Strengths of the script.
- List 5 actionable, high-impact Improvement Recommendations.
"""

ANALYZER_PROMPT = PromptTemplate(
    input_variables=["script"],
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
