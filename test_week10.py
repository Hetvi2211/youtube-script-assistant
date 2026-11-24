"""Unit tests for the Week 10 YouTube Content Package and Exporter workflow."""

import unittest
from langchain_core.runnables import RunnableLambda

from modules.content_generator import (
    ContentPackageError,
    generate_content_package,
    format_package_as_text,
    parse_metadata_sections,
    package_is_current,
    script_fingerprint,
)
from modules.exporter import (
    export_to_txt,
    export_to_docx,
    export_to_pdf,
)


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, desc_content=None, meta_content=None, error=None):
        self.desc_content = desc_content or "An engaging description of the video."
        self.meta_content = meta_content or ""
        self.error = error
        self.call_count = 0

    def invoke(self, prompt):
        if self.error:
            raise self.error
        self.call_count += 1
        # First call is description, second is metadata
        if self.call_count == 1:
            return FakeResponse(self.desc_content)
        return FakeResponse(self.meta_content)


SAMPLE_SCRIPT = """
[TITLE SUGGESTION]
5 Essential Daily Habits for High Productivity

[HOOK]
What if 10 minutes every morning could completely transform your day?

[INTRODUCTION]
Welcome back! Today we are looking at 5 simple habits that build massive momentum.

[MAIN CONTENT]
First, prepare your top priority the night before.
Second, drink 500ml of water immediately upon waking.
[Visual: B-roll of morning routine]

[CONCLUSION & RECAP]
Small consistent habits compound into lifelong achievement.

[CALL-TO-ACTION & OUTRO]
If you found this valuable, subscribe to the channel and drop a comment below!
"""

SAMPLE_METADATA_OUTPUT = """
1. KEYWORDS
daily habits, morning routine, productivity tips, personal growth, focus, habits for success, self improvement, morning habits, daily routine, high performance

2. YOUTUBE TAGS
habits, morning routine, productivity, self improvement, personal development, daily habits, life hacks, success habits, morning motivation, time management, routines, discipline, habits 2026, daily focus, focus

3. HASHTAGS
#Productivity #MorningRoutine #Habits #SelfImprovement #PersonalGrowth #Success #Focus #LifeHacks #Motivation #DailyHabits

4. CALL-TO-ACTION (CTA) VARIATIONS
- "Subscribe for weekly productivity frameworks that actually work."
- "Drop your favorite morning habit in the comments below!"
- "Hit the like button if you're committing to building better habits this week."
"""


class ContentPackageTests(unittest.TestCase):
    def test_parse_metadata_sections_standard(self):
        parsed = parse_metadata_sections(SAMPLE_METADATA_OUTPUT, fallback_title="Habits Video")
        self.assertTrue(len(parsed["keywords"]) >= 5)
        self.assertIn("daily habits", parsed["keywords"])
        self.assertTrue(len(parsed["tags"]) >= 5)
        self.assertIn("productivity", parsed["tags"])
        self.assertTrue(len(parsed["hashtags"]) >= 5)
        self.assertTrue(any("#Productivity" in h for h in parsed["hashtags"]))
        self.assertTrue(len(parsed["call_to_action"]) > 0)

    def test_parse_metadata_sections_json(self):
        json_text = """
        ```json
        {
            "title": "Habits Masterclass",
            "description": "Learn top habits.",
            "keywords": ["habit", "routine"],
            "tags": ["habits", "success"],
            "hashtags": ["#Habits", "#Life"],
            "call_to_action": "Subscribe now!"
        }
        ```
        """
        parsed = parse_metadata_sections(json_text)
        self.assertEqual(parsed["title"], "Habits Masterclass")
        self.assertEqual(parsed["keywords"], ["habit", "routine"])
        self.assertEqual(parsed["tags"], ["habits", "success"])
        self.assertEqual(parsed["hashtags"], ["#Habits", "#Life"])
        self.assertEqual(parsed["call_to_action"], "Subscribe now!")

    def test_generate_content_package_end_to_end(self):
        fake_llm = FakeLLM(
            desc_content="Detailed SEO description with timestamps and links.",
            meta_content=SAMPLE_METADATA_OUTPUT,
        )
        package = generate_content_package(
            topic="Daily Productivity Habits",
            title="5 Essential Daily Habits",
            script=SAMPLE_SCRIPT,
            audience="Students & Professionals",
            llm=fake_llm,
        )

        self.assertEqual(package["title"], "5 Essential Daily Habits")
        self.assertIn("What if 10 minutes", package["hook"])
        self.assertEqual(package["script"], SAMPLE_SCRIPT.strip())
        self.assertIn("Detailed SEO description", package["description"])
        self.assertTrue(len(package["keywords"]) > 0)
        self.assertTrue(len(package["tags"]) > 0)
        self.assertTrue(len(package["hashtags"]) > 0)
        self.assertTrue(len(package["call_to_action"]) > 0)

    def test_empty_script_or_topic_raises_error(self):
        with self.assertRaises(ValueError):
            generate_content_package(topic="Habits", title="Habits", script="")
        with self.assertRaises(ValueError):
            generate_content_package(topic="", title="Habits", script="Some script text")

    def test_llm_failure_raises_content_package_error(self):
        fake_llm = FakeLLM(error=RuntimeError("API quota exceeded"))
        with self.assertRaises(ContentPackageError):
            generate_content_package(
                topic="AI",
                title="AI Video",
                script=SAMPLE_SCRIPT,
                llm=fake_llm,
            )

    def test_format_package_as_text(self):
        package = {
            "title": "Test Title",
            "hook": "Hook sentence",
            "script": "Script content",
            "description": "Video description",
            "keywords": ["kw1", "kw2"],
            "tags": ["tag1", "tag2"],
            "hashtags": ["#h1", "#h2"],
            "call_to_action": "Subscribe CTA",
        }
        text = format_package_as_text(package)
        self.assertIn("TITLE:\nTest Title", text)
        self.assertIn("HOOK:\nHook sentence", text)
        self.assertIn("SCRIPT:\nScript content", text)
        self.assertIn("DESCRIPTION:\nVideo description", text)
        self.assertIn("KEYWORDS:\nkw1, kw2", text)
        self.assertIn("TAGS:\ntag1, tag2", text)
        self.assertIn("HASHTAGS:\n#h1 #h2", text)
        self.assertIn("CALL-TO-ACTION (CTA):\nSubscribe CTA", text)

    def test_package_is_current(self):
        script = "Sample script"
        h = script_fingerprint(script)
        package = {"title": "Title"}
        self.assertTrue(package_is_current(package, h, script))
        self.assertFalse(package_is_current(package, h, "Modified script"))
        self.assertFalse(package_is_current(None, h, script))


class ExporterTests(unittest.TestCase):
    def setUp(self):
        self.package_text = format_package_as_text({
            "title": "5 Essential Daily Habits",
            "hook": "What if 10 minutes could change your life?",
            "script": "Full script body...",
            "description": "Detailed video description...",
            "keywords": ["habit", "routine"],
            "tags": ["habit", "daily routine"],
            "hashtags": ["#Habits", "#Life"],
            "call_to_action": "Please subscribe!",
        })

    def test_export_to_txt(self):
        txt_bytes = export_to_txt(self.package_text)
        self.assertIsInstance(txt_bytes, bytes)
        decoded = txt_bytes.decode("utf-8")
        self.assertIn("5 Essential Daily Habits", decoded)
        self.assertIn("KEYWORDS", decoded)

    def test_export_to_docx(self):
        docx_bytes = export_to_docx(self.package_text, title="YouTube Content Package")
        self.assertIsInstance(docx_bytes, bytes)
        self.assertTrue(len(docx_bytes) > 1000)
        # Verify it can be opened back by docx
        import io
        from docx import Document
        doc = Document(io.BytesIO(docx_bytes))
        paragraphs = [p.text for p in doc.paragraphs]
        self.assertTrue(any("YouTube Content Package" in p for p in paragraphs))

    def test_export_to_pdf(self):
        pdf_bytes = export_to_pdf(self.package_text, title="YouTube Content Package")
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 500)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
