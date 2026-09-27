#!/usr/bin/env python3
"""Offline regression and manifest checks for issue 25."""

import csv
import sys
import unittest
from pathlib import Path

from quality_checks import (
    MAX_SEAM_DELTA_LU,
    MAX_WER,
    add_seam_metrics,
    check_loudness_fixture,
    duration_metrics,
    word_error_rate,
)

HERE = Path(__file__).resolve().parent
QUALITY_FIELDS = {
    "duration_seconds", "expected_min_duration_seconds", "duration_flag",
    "loudness_lufs", "seam_delta_lu", "seam_flag", "wer", "wer_flag",
    "transcript_file", "word_diff_file", "sent_text_file", "audio_sha256", "asr_model",
}


class QualityChecks(unittest.TestCase):
    def test_word_error_rate_and_empty_reference(self):
        self.assertEqual(word_error_rate("Hello, WORLD!", "hello world"), 0)
        self.assertAlmostEqual(word_error_rate("one two three", "one missing three"), 1 / 3)
        self.assertEqual(word_error_rate("", ""), 0)
        self.assertEqual(word_error_rate("", "invented"), 1)

    def test_duration_flags_truncation_at_360_words_per_minute(self):
        self.assertTrue(duration_metrics("one two three", 0.4)["duration_flag"])
        self.assertFalse(duration_metrics("one two three", 1.0)["duration_flag"])

    def test_seam_delta_is_recorded_and_flagged_above_threshold(self):
        rows = [{"loudness_lufs": -20.0}, {"loudness_lufs": -24.0}]
        add_seam_metrics(rows)
        self.assertEqual(rows[0]["seam_delta_lu"], 4.0)
        self.assertTrue(rows[0]["seam_flag"])
        self.assertEqual(rows[1]["seam_delta_lu"], "")
        self.assertFalse(rows[1]["seam_flag"])
        self.assertEqual(MAX_SEAM_DELTA_LU, 3.0)

    def test_thresholds_are_explicit(self):
        self.assertEqual(MAX_WER, 0.02)


def verify_manifest(path: Path = HERE / "renders.csv") -> int:
    if not path.exists():
        print(f"No render manifest found at {path}", file=sys.stderr)
        return 1
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or ())
        missing = QUALITY_FIELDS - fields
        if missing:
            print(f"Manifest lacks quality fields: {', '.join(sorted(missing))}", file=sys.stderr)
            return 1
        rows = list(reader)
    keys = [(row.get("article"), row.get("passage"), row.get("condition"),
             row.get("model"), row.get("chunk_size"), row.get("filename")) for row in rows]
    if len(keys) != len(set(keys)):
        print("Manifest contains duplicate render keys", file=sys.stderr)
        return 1
    missing_metrics = [row.get("filename", "(unknown)") for row in rows
                       if any(not row.get(field, "").strip() for field in QUALITY_FIELDS - {"seam_delta_lu"})]
    if missing_metrics:
        print("Manifest rows missing quality metrics: " + ", ".join(missing_metrics), file=sys.stderr)
        return 1
    for row in rows:
        if row["asr_model"] != "mlx-community/whisper-tiny":
            print(f"Unexpected ASR model for {row['filename']}: {row['asr_model']}", file=sys.stderr)
            return 1
        if bool(row["wer_flag"] == "True") != (float(row["wer"]) > MAX_WER):
            print(f"WER flag does not match threshold for {row['filename']}", file=sys.stderr)
            return 1
        if row["seam_delta_lu"] and bool(row["seam_flag"] == "True") != (float(row["seam_delta_lu"]) > MAX_SEAM_DELTA_LU):
            print(f"Seam flag does not match threshold for {row['filename']}", file=sys.stderr)
            return 1
        if bool(row["duration_flag"] == "True") != (
            float(row["duration_seconds"]) < float(row["expected_min_duration_seconds"])
        ):
            print(f"Duration flag does not match expected speaking rate for {row['filename']}", file=sys.stderr)
            return 1
        for field in ("transcript_file", "word_diff_file", "sent_text_file"):
            if not (HERE / row[field]).is_file():
                print(f"Missing {field} for {row['filename']}: {row[field]}", file=sys.stderr)
                return 1
    print(f"Manifest quality fields present for {len(rows)} unique renders")
    return 0


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QualityChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    fixture = check_loudness_fixture()
    print(f"Known-level loudness fixture: {fixture:.2f} LUFS (target -23.00 LUFS)")
    return verify_manifest()


if __name__ == "__main__":
    raise SystemExit(main())
