"""Deterministic Week 7 tests for the validated script analyzer."""

import json
import unittest

from langchain_core.runnables import RunnableLambda

from modules.script_analyzer import (
    CRITERION_NAMES,
    ScriptAnalysisError,
    analysis_is_current,
    analyze_script,
    calculate_script_metrics,
    script_fingerprint,
)


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, content=None, error=None):
        self.content = content
        self.error = error
        self.prompt = ""

    def invoke(self, prompt):
        self.prompt = prompt.to_string() if hasattr(prompt, "to_string") else str(prompt)
        if self.error:
            raise self.error
        return FakeResponse(self.content)


def analysis_payload(scores=None, missing_elements=None):
    scores = scores or [8] * len(CRITERION_NAMES)
    return {
        "overall_score": 99,
        "overall_summary": "The supplied draft has a clear, useful progression.",
        "criteria": [
            {
                "criterion": criterion,
                "score": score,
                "rating": "Good" if score >= 6 else "Poor",
                "explanation": f"Evidence-based evaluation for {criterion}.",
                "suggestion": f"Improve {criterion.lower()} with a concrete revision.",
            }
            for criterion, score in zip(CRITERION_NAMES, scores)
        ],
        "strengths": ["The explanation is easy to follow."],
        "improvement_suggestions": ["Add a more specific example in the main section."],
        "missing_elements": missing_elements or [],
    }


class ScriptAnalyzerTests(unittest.TestCase):
    def analyze(self, script, payload=None, preferences=None):
        fake_llm = FakeLLM(json.dumps(payload or analysis_payload()))
        result = analyze_script(
            script, llm=RunnableLambda(fake_llm.invoke), preferences=preferences
        )
        return result, fake_llm

    def test_well_structured_script_has_python_metrics_and_derived_score(self):
        script = (
            "[HOOK] What if one small change could save you hours every week?\n"
            "[INTRODUCTION] Today we will test that idea.\n"
            "[MAIN CONTENT] First, prepare the workflow. For example, automate the report.\n"
            "[CONCLUSION] Start with one step today.\n"
            "[CALL-TO-ACTION] Subscribe and comment with your result."
        )
        result, _ = self.analyze(script, analysis_payload([9] * 9))
        self.assertEqual(result["word_count"], len(script.split()))
        self.assertEqual(result["estimated_reading_time_minutes"], round(len(script.split()) / 140, 2))
        self.assertEqual(result["overall_score"], 90.0)

    def test_weak_hook_can_be_returned_as_low_criterion_score(self):
        result, _ = self.analyze("Here is a video about productivity.", analysis_payload([2, 6, 6, 6, 7, 4, 6, 7, 8]))
        hook = next(item for item in result["criteria"] if item["criterion"] == "Hook Quality")
        self.assertEqual(hook["score"], 2)

    def test_missing_cta_is_preserved(self):
        result, _ = self.analyze("Today we explain the topic clearly.", analysis_payload([3] * 9, ["Call-to-Action (CTA)"]))
        self.assertIn("Call-to-Action (CTA)", result["missing_elements"])

    def test_cta_present_in_script_is_not_reported_missing(self):
        payload = analysis_payload([8] * 9, ["Call-to-Action (CTA)"])
        result, _ = self.analyze(
            "Here is the explanation. Subscribe and comment with your question.",
            payload,
        )
        self.assertNotIn("Call-to-Action (CTA)", result["missing_elements"])

    def test_repetitive_content_can_have_repetition_suggestion(self):
        payload = analysis_payload([7, 7, 7, 7, 2, 5, 7, 6, 8])
        payload["criteria"][4]["suggestion"] = "Remove the repeated second explanation of the same point."
        result, _ = self.analyze("The same point. " * 20, payload)
        self.assertIn("repeated", result["criteria"][4]["suggestion"])

    def test_empty_script_is_rejected_before_llm_call(self):
        with self.assertRaises(ValueError):
            analyze_script("   ", llm=FakeLLM())

    def test_very_short_script_still_uses_actual_word_count(self):
        result, _ = self.analyze("Hello.", analysis_payload([1] * 9))
        self.assertEqual(result["word_count"], 1)
        self.assertEqual(result["estimated_reading_time_minutes"], 0.01)

    def test_preferences_are_included_in_prompt(self):
        _, fake_llm = self.analyze(
            "A short tutorial for students.",
            preferences={
                "topic": "Python basics",
                "audience": "Students",
                "tone": "Casual/Friendly",
                "length": "Short (< 3 mins)",
                "style": "Step-by-Step Tutorial",
            },
        )
        self.assertIn("Students", fake_llm.prompt)
        self.assertIn("Casual/Friendly", fake_llm.prompt)
        self.assertIn("Python basics", fake_llm.prompt)

    def test_malformed_llm_output_is_rejected(self):
        with self.assertRaises(ScriptAnalysisError):
            analyze_script(
                "A real script.",
                llm=RunnableLambda(FakeLLM("not json").invoke),
            )

    def test_llm_failure_is_reported(self):
        with self.assertRaises(ScriptAnalysisError):
            analyze_script(
                "A real script.",
                llm=RunnableLambda(FakeLLM(error=ConnectionError("offline")).invoke),
            )

    def test_regeneration_does_not_match_old_analysis(self):
        original = "Original script with a clear CTA."
        regenerated = "A completely different regenerated script."
        result, _ = self.analyze(original)
        old_hash = script_fingerprint(original)
        self.assertTrue(analysis_is_current(result, old_hash, 1, original, 1))
        self.assertFalse(analysis_is_current(result, old_hash, 1, regenerated, 2))

    def test_metrics_reject_invalid_speaking_rate(self):
        with self.assertRaises(ValueError):
            calculate_script_metrics("script", speaking_rate_wpm=0)


if __name__ == "__main__":
    unittest.main()
