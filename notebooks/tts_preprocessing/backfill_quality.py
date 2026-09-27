#!/usr/bin/env python3
"""Attach issue 25 evidence to renders already present in the manifest."""

import csv
import hashlib
import re
import tempfile
from pathlib import Path

import pysbd

from quality_checks import add_seam_metrics, analyse_render

ROOT = Path(__file__).resolve().parent
SEGMENTER = pysbd.Segmenter(language="en", clean=False, char_span=True)


def make_chunks(text: str, word_limit: int = 350, char_limit: int = 1900) -> list[str]:
    paragraphs = re.split(r"(\n{2,})", text)
    chunks, current = [], ""
    for index in range(0, len(paragraphs), 2):
        paragraph = paragraphs[index]
        separator = paragraphs[index + 1] if index + 1 < len(paragraphs) else ""
        unit = paragraph + separator
        if len(unit.split()) <= word_limit and len(unit) <= char_limit:
            if current and (len((current + unit).split()) > word_limit or len(current + unit) > char_limit):
                chunks.append(current)
                current = unit
            else:
                current += unit
            continue
        spans = SEGMENTER.segment(unit)
        sentences = [unit[span.start:span.end] for span in spans]
        if "".join(sentences) != unit:
            raise ValueError("Sentence spans did not preserve the source text")
        for sentence in sentences:
            candidate = current + sentence
            if len(sentence) > char_limit or len(sentence.split()) > word_limit:
                raise ValueError("A single sentence exceeds a chunk budget")
            if current and (len(candidate.split()) > word_limit or len(candidate) > char_limit):
                chunks.append(current)
                current = sentence
            else:
                current = candidate
    if current:
        chunks.append(current)
    if "".join(chunks) != text:
        raise AssertionError("Chunking changed the source text")
    return chunks


def main() -> None:
    manifest = ROOT / "renders.csv"
    with manifest.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0])
    by_article: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_article.setdefault(row["article"], []).append(row)

    for article, article_rows in by_article.items():
        excerpt = (ROOT / "inputs" / f"excerpt-{article}.txt").read_text(encoding="utf-8")
        chunks = make_chunks(excerpt)
        grouped: dict[tuple[str, ...], list[dict[str, str]]] = {}
        for row in article_rows:
            sent_path = (ROOT / row["sent_text_file"] if row.get("sent_text_file") else
                         ROOT / "inputs" / "sent" / f"{Path(row['filename']).stem}.txt")
            if sent_path.is_file():
                chunk = sent_path.read_text(encoding="utf-8")
            else:
                number = int(Path(row["filename"]).stem.rsplit("-", 1)[1]) - 1
                chunk = chunks[number]
                sent_path.parent.mkdir(parents=True, exist_ok=True)
                sent_path.write_text(chunk, encoding="utf-8")
            digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            if digest != row["input_sha256"]:
                raise ValueError(f"Text hash does not match manifest for {row['filename']}")
            stem = Path(row["filename"]).stem
            row["sent_text_file"] = str(sent_path.relative_to(ROOT))
            transcript_path = ROOT / "transcripts" / f"{stem}.txt"
            audio_path = ROOT / row["filename"]
            audio_digest = hashlib.sha256(audio_path.read_bytes()).hexdigest()
            cached_transcript = None
            if (row.get("audio_sha256") == audio_digest
                    and row.get("asr_model") == "mlx-community/whisper-tiny"
                    and transcript_path.is_file()):
                cached_transcript = transcript_path.read_text(encoding="utf-8").strip()
            if not cached_transcript:
                raise RuntimeError(
                    f"No verified transcript cache for {row['filename']}; "
                    "run the render analysis block before verify.sh"
                )
            row.update(analyse_render(
                audio_path, chunk, transcript_path,
                ROOT / "diffs" / f"{stem}.diff",
                cached_transcript=cached_transcript,
            ))
            group_key = tuple(row.get(field, "") for field in
                              ("passage", "condition", "model", "chunk_size"))
            grouped.setdefault(group_key, []).append(row)
        for grouped_rows in grouped.values():
            grouped_rows.sort(key=lambda row: int(Path(row["filename"]).stem.rsplit("-", 1)[1]))
            add_seam_metrics(grouped_rows)

    for field in dict.fromkeys(field for row in rows for field in row):
        if field not in fields:
            fields.append(field)
    with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=ROOT, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(manifest)
    print(f"Added quality evidence for {len(rows)} renders to {manifest.name}")


if __name__ == "__main__":
    main()
