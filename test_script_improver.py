"""
Deterministic Week 8 unit tests for automatic script improvement module.
Tests analysis formatting, response parsing, metric diff calculations,
and the improve_script LangChain pipeline.
"""

import unittest
from langchain_core.runnables import RunnableLambda

from modules.script_improver import (
    ImprovedScriptResult,
    ScriptImprovementError,
    compare_scripts,
    format_analysis_for_improvement,
    improve_script,
    parse_improvement_response,
)


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, content: str = "", error: Exception = None):
        self.content = content
        self.error = error
        self.last_prompt = ""

    def invoke(self, prompt):
        self.last_prompt = prompt.to_string() if hasattr(prompt, "to_string") else str(prompt)
        if self.error:
            raise self.error
        return FakeResponse(self.content)


class ScriptImproverTests(unittest.TestCase):
    def setUp(self):
        self.sample_script = (
            "[TITLE]: How to Learn AI in 2026\n"
            "[HOOK] Today we will talk about learning artificial intelligence.\n"
            "[INTRODUCTION] Welcome back to the channel. AI is popular.\n"
            "[MAIN CONTENT] Start by learning Python. Then study linear algebra and calculus. "
            "Next, learn machine learning libraries like scikit-learn. "
            "Finally, build projects.\n"
            "[CONCLUSION] That is how you learn AI."
        )

        self.sample_analysis = {
            "overall_score": 62.0,
            "overall_summary": "Good technical roadmap, but the opening lacks hook curiosity and a clear CTA is missing.",
            "criteria": [
                {
                    "criterion": "Hook Quality",
                    "score": 4.0,
                    "rating": "Poor",
                    "explanation": "Opening hook is generic and does not create tension or curiosity.",
                    "suggestion": "Replace with a high-stakes question or surprising stat about AI careers.",
                },
                {
                    "criterion": "Call-to-Action (CTA)",
                    "score": 3.0,
                    "rating": "Poor",
                    "explanation": "The script abruptly ends without inviting subscribers or community comments.",
                    "suggestion": "Add an engaging CTA asking viewers for their current career stage.",
                },
                {
                    "criterion": "Script Structure",
                    "score": 8.0,
                    "rating": "Good",
                    "explanation": "Progression from basics to projects is clear.",
                    "suggestion": "Maintain logical progression.",
                },
            ],
            "strengths": ["Clear roadmap progression from basics to projects."],
            "missing_elements": ["Call-to-Action (CTA)", "Real-world Project Example"],
            "improvement_suggestions": [
                "Supercharge the first 30 seconds with an engaging career-focused hook.",
                "Add an actionable Call-to-Action inviting subscriptions.",
                "Include a concrete project example such as an automated summarizer.",
            ],
        }

    def test_format_analysis_for_improvement_formats_dict_cleanly(self):
        formatted = format_analysis_for_improvement(self.sample_analysis)
        self.assertIn("Overall Quality Score: 62.0/100", formatted)
        self.assertIn("CRITICAL MISSING ELEMENTS:", formatted)
        self.assertIn("Call-to-Action (CTA)", formatted)
        self.assertIn("AREAS NEEDING IMPROVEMENT (Weak Scores):", formatted)
        self.assertIn("Hook Quality", formatted)
        self.assertIn("PRIORITIZED IMPROVEMENT SUGGESTIONS:", formatted)
        self.assertIn("Supercharge the first 30 seconds", formatted)
        self.assertIn("KEY STRENGTHS TO PRESERVE:", formatted)

    def test_format_analysis_for_improvement_preserves_string(self):
        text = "Hook is weak. Please add CTA."
        self.assertEqual(format_analysis_for_improvement(text), text)

    def test_parse_improvement_response_extracts_summary_and_script(self):
        raw = (
            "[SUMMARY OF IMPROVEMENTS]\n"
            "- Replaced weak opening with a high-stakes question.\n"
            "- Added a 3-part subscriber Call-to-Action.\n"
            "- Inserted an example of a sentiment analyzer.\n\n"
            "[IMPROVED SCRIPT]\n"
            "[TITLE]: How to Learn AI in 2026 (Zero to Hired)\n"
            "[HOOK] What if the next 6 months could reshape your entire software career?\n"
            "[MAIN CONTENT] Step 1: Python basics.\n"
            "[CALL-TO-ACTION] Hit subscribe for weekly roadmaps!"
        )
        script, summary = parse_improvement_response(raw)
        self.assertEqual(len(summary), 3)
        self.assertIn("Replaced weak opening", summary[0])
        self.assertTrue(script.startswith("[TITLE]:"))
        self.assertIn("[CALL-TO-ACTION]", script)

    def test_parse_improvement_response_fallback_when_no_headers(self):
        raw = "Just the revised script text without headers."
        script, summary = parse_improvement_response(raw)
        self.assertEqual(script, raw)
        self.assertGreater(len(summary), 0)

    def test_compare_scripts_metrics(self):
        orig = "one two three four five"
        imp = "one two three four five six seven eight nine ten"
        metrics = compare_scripts(orig, imp, speaking_rate_wpm=100)
        self.assertEqual(metrics["original_word_count"], 5)
        self.assertEqual(metrics["improved_word_count"], 10)
        self.assertEqual(metrics["delta_words"], 5)
        self.assertEqual(metrics["delta_percentage"], 100.0)
        self.assertEqual(metrics["original_speaking_time_minutes"], 0.05)
        self.assertEqual(metrics["improved_speaking_time_minutes"], 0.1)

    def test_improved_script_result_behavior(self):
        content = "My improved script"
        res = ImprovedScriptResult(
            content=content,
            summary_of_improvements=["Fixed hook", "Added CTA"],
            diff_metrics={"delta_words": 15},
            original_script="Old script",
            raw_response="Raw",
            improvement_focus="All Suggestions",
        )
        # acts as string
        self.assertIsInstance(res, str)
        self.assertEqual(res, "My improved script")
        self.assertEqual(res[:11], "My improved")
        self.assertEqual(len(res), len(content))

        # exposes attributes
        self.assertEqual(res.summary_of_improvements, ["Fixed hook", "Added CTA"])
        self.assertEqual(res.diff_metrics["delta_words"], 15)
        self.assertEqual(res.original_script, "Old script")

        # exposes dict keys
        self.assertEqual(res["improved_script"], "My improved script")
        self.assertEqual(res["summary_of_improvements"], ["Fixed hook", "Added CTA"])
        self.assertEqual(res["diff_metrics"]["delta_words"], 15)

    def test_improve_script_pipeline_end_to_end(self):
        fake_output = (
            "[SUMMARY OF IMPROVEMENTS]\n"
            "- Created an attention-grabbing career question hook.\n"
            "- Added interactive CTA.\n\n"
            "[IMPROVED SCRIPT]\n"
            "[TITLE]: How to Learn AI in 2026\n"
            "[HOOK] Could 6 months of focused coding change your career?\n"
            "[CALL-TO-ACTION] Subscribe for more!"
        )
        fake_llm = FakeLLM(content=fake_output)
        res = improve_script(
            original_script=self.sample_script,
            analysis=self.sample_analysis,
            user_feedback="Make it punchy",
            improvement_focus="All Analysis Recommendations",
            llm=RunnableLambda(fake_llm.invoke),
        )

        self.assertIn("Could 6 months of focused coding", res.improved_script)
        self.assertEqual(len(res.summary_of_improvements), 2)
        self.assertIn("career question hook", res.summary_of_improvements[0])
        self.assertIn("original_word_count", res.diff_metrics)
        self.assertIn("improved_word_count", res.diff_metrics)
        self.assertIn("PRIMARY IMPROVEMENT FOCUS", fake_llm.last_prompt)

    def test_improve_script_raises_on_empty_script(self):
        with self.assertRaises(ScriptImprovementError):
            improve_script("", self.sample_analysis)

    def test_improve_script_raises_on_empty_analysis(self):
        with self.assertRaises(ScriptImprovementError):
            improve_script(self.sample_script, {})


if __name__ == "__main__":
    unittest.main()
