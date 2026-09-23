# [[file:../orukeet-dictation.org::*Spoken words, written sentence][Spoken words, written sentence:2]]
"""Rules, then a guard. The GGUF stays unloaded."""

from __future__ import annotations

import unittest

from dictation.cleanup import (
    DEFAULT_FILE,
    DEFAULT_REPO,
    SYSTEM,
    apply_cleanup,
    apply_rules,
    cleanup_result,
    segment_texts,
)


class RulesTests(unittest.TestCase):
    def test_drops_fillers_and_a_repeated_word(self) -> None:
        self.assertEqual(apply_rules("um I want the the report"), "I want the report")

    def test_leaves_like_and_number_words(self) -> None:
        self.assertEqual(apply_rules("I like this"), "I like this")
        self.assertEqual(apply_rules("three things"), "three things")

    def test_leaves_an_unpunctuated_retraction(self) -> None:
        self.assertEqual(apply_rules("Thursday no Friday"), "Thursday no Friday")

    def test_turns_a_spoken_paragraph_break_into_a_break(self) -> None:
        original = "Thanks for the update. New paragraph. I'll review it tonight."
        self.assertEqual(
            apply_rules(original),
            "Thanks for the update.\n\nI'll review it tonight.",
        )


class GuardTests(unittest.TestCase):
    def test_keeps_a_retraction_and_an_email(self) -> None:
        self.assertEqual(
            apply_cleanup("Let's ship it Thursday, no, Friday.", "Let's ship it Friday."),
            "Let's ship it Friday.",
        )
        self.assertEqual(
            apply_cleanup(
                "Email me at sam at example dot com",
                "Email me at sam@example.com",
            ),
            "Email me at sam@example.com",
        )

    def test_rejects_a_chatbot_answer_and_an_empty_reply(self) -> None:
        original = "Should I send the report"
        answered = "Sure! You should send it tomorrow, and here is why it matters."
        self.assertEqual(apply_cleanup(original, answered), original)
        self.assertEqual(apply_cleanup(original, "   "), original)

    def test_rejects_a_reply_that_runs_away(self) -> None:
        original = "Send it."
        runaway = "word " * 80
        self.assertEqual(apply_cleanup(original, runaway), original)

    def test_ignores_a_thinking_preamble(self) -> None:
        output = "<think>drop the filler</think>\nSend the file."
        self.assertEqual(apply_cleanup("Send the file.", output), "Send the file.")

    def test_default_file_is_the_q4_speakoflow_build(self) -> None:
        self.assertEqual(DEFAULT_REPO, "SpeakoFlow/speakoflow-mini")
        self.assertEqual(DEFAULT_FILE, "SpeakoFlow-Mini-0.8B-Q4_K_M.gguf")
        self.assertTrue(SYSTEM.startswith("You clean up SpeakoFlow dictation."))


class _Upper:
    def clean(self, text: str) -> str:
        return text.upper()


class SegmentTests(unittest.TestCase):
    def test_one_segment_stays_one_piece(self) -> None:
        result = {"text": "alpha beta", "segments": [{"text": "alpha beta"}]}
        self.assertEqual(segment_texts(result), ["alpha beta"])

    def test_several_segments_are_cleaned_apart(self) -> None:
        result = {
            "text": "alpha beta",
            "segments": [{"text": "alpha"}, {"text": "beta"}],
        }
        self.assertEqual(segment_texts(result), ["alpha", "beta"])
        self.assertEqual(cleanup_result(result, "model", _Upper()), "ALPHA BETA")
        self.assertEqual(cleanup_result(result, "off", _Upper()), "alpha beta")
        heard = {"text": "um hello", "segments": []}
        self.assertEqual(cleanup_result(heard, "rules", None), "hello")


if __name__ == "__main__":
    unittest.main()
# Spoken words, written sentence:2 ends here
