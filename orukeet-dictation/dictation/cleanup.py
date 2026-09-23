# [[file:../orukeet-dictation.org::*Spoken words, written sentence][Spoken words, written sentence:1]]
"""Turn a speech transcript into a written sentence, without paraphrasing it."""

from __future__ import annotations

import re

DEFAULT_MODEL = "mlx-community/Qwen3.5-0.8B-4bit-OptiQ"

SYSTEM = (
    "Turn the speech transcript into one written sentence. "
    "Remove filler words such as um, uh, and erm. "
    "Remove false starts and immediate repetitions. "
    "Add punctuation and capitalization. "
    "Keep the speaker's words. "
    "Do not summarize. Do not add words. Do not substitute synonyms. "
    "Reply with the written sentence only."
)

# Spoken forms the model may expand. The guard treats the expansion as the same words.
SPOKEN = {
    "gonna": ("going", "to"),
    "wanna": ("want", "to"),
    "kinda": ("kind", "of"),
    "gotta": ("got", "to"),
    "yeah": ("yes",),
    "yep": ("yes",),
    "nope": ("no",),
}
FILLERS = {"um", "uh", "uhh", "erm", "hmm", "ah", "eh", "mm"}


def apply_cleanup(original: str, model_output: str) -> str:
    cleaned = _model_line(model_output)
    if cleaned and _faithful(original, cleaned):
        return cleaned
    return original.strip()


def _model_line(raw: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip().strip('"').strip("'")
    for prefix in ("written:", "cleaned:", "output:", "transcript:"):
        if text.lower().startswith(prefix):
            text = text[len(prefix):].strip()
    line = next((part.strip() for part in text.splitlines() if part.strip()), "")
    return line.strip('"').strip()


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _spoken_words(text: str) -> list[str]:
    words: list[str] = []
    for token in _tokens(text):
        if token in FILLERS:
            continue
        words.extend(SPOKEN.get(token, (token,)))
    return words


def _faithful(original: str, cleaned: str) -> bool:
    source = _spoken_words(original)
    written = _tokens(cleaned)
    if not source or not written:
        return False
    if any(word not in source for word in written):
        return False
    if _lcs_length(source, written) != len(written):
        return False
    return len(written) >= max(1, int(0.5 * len(source)))


def _lcs_length(left: list[str], right: list[str]) -> int:
    previous = [0] * (len(right) + 1)
    for word in left:
        current = [0]
        for index, other in enumerate(right):
            if word == other:
                current.append(previous[index] + 1)
            else:
                current.append(max(previous[index + 1], current[-1]))
        previous = current
    return previous[-1]


class Cleaner:
    def __init__(self, model_id: str = DEFAULT_MODEL) -> None:
        self.model_id = model_id
        self._model = None
        self._tokenizer = None

    def load(self) -> None:
        from mlx_lm import load

        self._model, self._tokenizer = load(self.model_id)

    def clean(self, transcript: str) -> str:
        if self._model is None or not transcript.strip():
            return transcript.strip()
        try:
            rewritten = self._generate(transcript.strip())
        except Exception:
            return transcript.strip()
        return apply_cleanup(transcript, rewritten)

    def _generate(self, transcript: str) -> str:
        from mlx_lm import generate

        tokenizer = self._tokenizer
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": transcript},
        ]
        if getattr(tokenizer, "chat_template", None):
            try:
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
            except TypeError:
                prompt = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
        else:
            prompt = f"{SYSTEM}\n\nTranscript:\n{transcript}\n\nWritten:\n"
        max_tokens = max(32, min(128, 2 * len(_tokens(transcript)) + 16))
        return generate(
            self._model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False,
        )
# Spoken words, written sentence:1 ends here
