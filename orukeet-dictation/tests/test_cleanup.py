# [[file:../orukeet-dictation.org::*Spoken words, written sentence][Spoken words, written sentence:2]]
"""The cleanup guard keeps the speaker's words."""

from __future__ import annotations

import unittest

from dictation.cleanup import DEFAULT_MODEL, apply_cleanup


class CleanupTests(unittest.TestCase):
    def test_drops_fillers_and_a_false_start(self) -> None:
        original = "um I want to I want the report"
        self.assertEqual(
            apply_cleanup(original, "I want the report."),
            "I want the report.",
        )

    def test_allows_gonna_to_become_going_to(self) -> None:
        self.assertEqual(
            apply_cleanup("I'm gonna go now", "I'm going to go now."),
            "I'm going to go now.",
        )

    def test_rejects_a_paraphrase(self) -> None:
        original = "I want the report"
        self.assertEqual(
            apply_cleanup(original, "I need the document."),
            original,
        )

    def test_rejects_a_summary_and_an_empty_reply(self) -> None:
        original = "I want the report about the budget for next year and the hiring plan"
        self.assertEqual(apply_cleanup(original, "I want a budget report."), original)
        self.assertEqual(apply_cleanup(original, "   "), original)

    def test_strips_a_label_the_model_added(self) -> None:
        self.assertEqual(
            apply_cleanup("uh send the file", "Written: Send the file."),
            "Send the file.",
        )

    def test_default_model_is_the_half_billion_mlx_build(self) -> None:
        self.assertEqual(DEFAULT_MODEL, "mlx-community/Qwen2.5-0.5B-Instruct-4bit")


if __name__ == "__main__":
    unittest.main()
# Spoken words, written sentence:2 ends here
