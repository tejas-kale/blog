# Orukeet dictation for macOS

Headless, on-device dictation for any app: hold a key, speak, release, and the transcript is pasted at the caret. Same push-to-talk pattern as Wispr Flow, using [Orukeet](https://huggingface.co/oruk/orukeet) instead of a hosted recognizer.

The Swift agent has no windows and no menu bar (`LSUIElement`). Recognition is a persistent local Python worker, as in [Sacha Chua’s Orukeet notes](https://sachachua.com/blog/2026/09/experimenting-with-orukeet-for-speech-recognition/): load the model once, then transcribe each clip without reloading.

## 8 GB M1 MacBook Air

Use the **native Q8** install with `--device auto` (Metal on Apple silicon). That weight file is about **714 MB**. Do not install the 2.5 GB NeMo checkpoint or the 1.3 GB F16 GGUF on this machine.

Expect roughly 1.5–2.5 GB unified memory for the worker once it is warm. Close heavy browsers before the first load. Keep **one** worker; a second copy will thrash swap. Recordings are capped at 60 seconds.

Orukeet’s positional Metal cache covers clips up to about 41 seconds. Longer utterances still transcribe, but they skip that cache.

## Install

On the Air, with Python 3.12+ and Xcode Command Line Tools:

```bash
cd orukeet-dictation
chmod +x scripts/*.sh
./scripts/install-orukeet.sh
./scripts/run.sh
```

`install-orukeet.sh` creates `.venv`, installs [Orukeet 0.1.1](https://github.com/Oruk-AI/orukeet/releases/download/v0.1.1/orukeet-0.1.1-py3-none-any.whl), and writes `installation.json` with absolute paths to the Q8 model and runtime.

First run will ask for **Microphone** and **Accessibility**. Accessibility is required so the agent can see the hotkey while another app is focused and so synthetic ⌘V can land in that app.

Optional app bundle (still no UI):

```bash
./scripts/package-app.sh
open dist/OrukeetDictation.app
```

Grant permissions to that bundle, not only to Terminal, if you launch it that way.

## Use

1. Click a text field in Mail, Notes, a browser, or an editor.
2. Hold **Right Option** (default). Speak.
3. Release. After Orukeet returns text, the agent pastes it and restores the previous clipboard.

Change the hotkey with `ORUKEET_HOTKEY`:

| Value | Key |
| --- | --- |
| `right-option` (default) | Right Option |
| `globe` or `fn` | Globe / Fn |
| `right-shift` | Right Shift |
| `f5` | F5 |
| a numeric key code | any other key |

Wispr Flow defaults to Fn. On a MacBook Air, Right Option is more predictable than Globe/Fn.

## Layout

- `Sources/OrukeetDictation` — macOS agent: hotkey, mic, paste
- `Sources/OrukeetDictationCore` — WAV encoder, HTTP client, config
- `server/orukeet_server.py` — localhost worker (`POST /transcribe`, `GET /health`)
- `launchd/` — optional Login Item plist (edit the absolute path first)

The worker listens on `127.0.0.1:8765` only. Audio never leaves the machine.

## Tests

```bash
python3 -m unittest tests/test_orukeet_server.py
# on a Mac with Swift:
swift test
```

Stub mode (`ORUKEET_STUB=1`) exercises the HTTP contract without downloading weights.

## License

Agent code is MIT-licensed. Orukeet weights are CC BY-SA 4.0 with NVIDIA’s foundation attribution; see the [model card](https://huggingface.co/oruk/orukeet).
