"""Unit tests for the Week 9 scene breakdown workflow."""

import json
import unittest

from langchain_core.runnables import RunnableLambda

from modules.scene_generator import (
    SceneBreakdownError,
    breakdown_is_current,
    generate_scene_breakdown,
    parse_duration_seconds,
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


def scene_payload(count=2):
    return {
        "scenes": [
            {
                "scene_number": 99,
                "start_time": "9:00",
                "end_time": "9:30",
                "duration_seconds": 30,
                "voiceover": f"Scene {index} narration with useful context.",
                "visual_suggestion": "Show relevant B-roll or a clear demonstration.",
                "on_screen_text": f"Key point {index}",
            }
            for index in range(1, count + 1)
        ],
        "total_duration_seconds": 999,
        "total_scenes": 999,
    }


class SceneGeneratorTests(unittest.TestCase):
    def test_normal_script_is_normalized_to_sequential_timeline(self):
        script = "A hook introduces the topic. The main section explains it. Subscribe for more."
        result = generate_scene_breakdown(
            script,
            video_length="Short (< 3 mins)",
            llm=RunnableLambda(FakeLLM(json.dumps(scene_payload())).invoke),
        )
        self.assertEqual([scene["scene_number"] for scene in result["scenes"]], [1, 2])
        self.assertEqual(result["total_duration_seconds"], 180)
        self.assertEqual(result["scenes"][0]["start_time"], "0:00")
        self.assertEqual(result["scenes"][0]["end_time"], result["scenes"][1]["start_time"])
        self.assertEqual(result["scenes"][-1]["end_time"], "3:00")

    def test_short_hook_and_cta_are_preserved_in_voiceover(self):
        payload = scene_payload(2)
        payload["scenes"][0]["voiceover"] = "What if this changes everything?"
        payload["scenes"][1]["voiceover"] = "Subscribe and comment with your question."
        result = generate_scene_breakdown(
            "Hook. Explanation. CTA.",
            video_length="1 minute",
            llm=RunnableLambda(FakeLLM(json.dumps(payload)).invoke),
        )
        self.assertIn("changes everything", result["scenes"][0]["voiceover"])
        self.assertIn("Subscribe", result["scenes"][1]["voiceover"])

    def test_long_script_supports_many_sections(self):
        result = generate_scene_breakdown(
            " ".join(["section"] * 500),
            llm=RunnableLambda(FakeLLM(json.dumps(scene_payload(8))).invoke),
        )
        self.assertEqual(result["total_scenes"], 8)
        self.assertTrue(all(scene["duration_seconds"] > 0 for scene in result["scenes"]))

    def test_empty_script_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_scene_breakdown("", llm=FakeLLM())

    def test_missing_fields_and_malformed_json_are_rejected(self):
        invalid = scene_payload(1)
        del invalid["scenes"][0]["visual_suggestion"]
        with self.assertRaises(SceneBreakdownError):
            generate_scene_breakdown("A script", llm=RunnableLambda(FakeLLM(json.dumps(invalid)).invoke))
        invalid_number = scene_payload(1)
        invalid_number["scenes"][0]["scene_number"] = "one"
        with self.assertRaises(SceneBreakdownError):
            generate_scene_breakdown(
                "A script", llm=RunnableLambda(FakeLLM(json.dumps(invalid_number)).invoke)
            )
        with self.assertRaises(SceneBreakdownError):
            generate_scene_breakdown("A script", llm=RunnableLambda(FakeLLM("not json").invoke))

    def test_llm_error_is_reported(self):
        with self.assertRaises(SceneBreakdownError):
            generate_scene_breakdown(
                "A script",
                llm=RunnableLambda(FakeLLM(error=ConnectionError("offline")).invoke),
            )

    def test_timing_and_script_association_are_deterministic(self):
        script = "Original script."
        result = generate_scene_breakdown(
            script,
            video_length="2 minutes",
            llm=RunnableLambda(FakeLLM(json.dumps(scene_payload(3))).invoke),
        )
        cursor = 0
        for scene in result["scenes"]:
            self.assertEqual(scene["start_time"], f"{cursor // 60}:{cursor % 60:02d}")
            cursor += scene["duration_seconds"]
        self.assertEqual(cursor, result["total_duration_seconds"])
        self.assertTrue(breakdown_is_current(result, script_fingerprint(script), script))
        self.assertFalse(breakdown_is_current(result, script_fingerprint(script), "Changed script."))

    def test_duration_labels_are_parsed(self):
        self.assertEqual(parse_duration_seconds("Medium (5 - 10 mins)"), 450)
        self.assertEqual(parse_duration_seconds("2 minutes"), 120)
        self.assertIsNone(parse_duration_seconds("Not specified"))


if __name__ == "__main__":
    unittest.main()
