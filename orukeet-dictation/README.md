# Orukeet dictation for macOS

Hold a key, speak, release. The transcript is pasted into whatever app you were typing in. Same idea as Wispr Flow, using [Orukeet](https://huggingface.co/oruk/orukeet) on your machine. There is no window.

Everything you run is Python. The model stays loaded in one local worker, which is the setup from [Sacha Chua’s Orukeet notes](https://sachachua.com/blog/2026/09/experimenting-with-orukeet-for-speech-recognition/).

## What happens when you hold the key

1. `dictation/hotkey.py` sees Right Option go down, even if Mail or a browser is in front.
2. `dictation/record.py` turns the microphone on and writes a WAV.
3. You release the key. `dictation/client.py` sends that WAV to `http://127.0.0.1:8765`.
4. `server/orukeet_server.py` already has Orukeet in memory and returns the text.
5. `dictation/paste.py` copies the text, presses Command-V, then puts your old clipboard back.

`dictation/agent.py` is the short file that ties those steps together.

Watching keys in other apps and pressing Command-V are macOS system calls. Python reaches them through [PyObjC](https://pyobjc.readthedocs.io/). That is the only non-Python piece, and it is a library rather than a second app.

## 8 GB M1 MacBook Air

Install the **native Q8** model with `--device auto` (Metal on Apple silicon). The weight file is about **714 MB**. Skip the 2.5 GB NeMo checkpoint and the 1.3 GB F16 file.

Once warm, the worker wants roughly 1.5–2.5 GB of unified memory. Close heavy browsers before the first load. Run one worker. A second copy will thrash swap. Recordings stop at 60 seconds.

Orukeet’s positional Metal cache covers clips up to about 41 seconds. Longer clips still transcribe; they skip that cache.

## Install

On the Air, with Python 3.12+:

```bash
cd orukeet-dictation
chmod +x scripts/*.sh
./scripts/install-orukeet.sh
./scripts/run.sh
```

`install-orukeet.sh` creates `.venv`, installs [Orukeet 0.1.1](https://github.com/Oruk-AI/orukeet/releases/download/v0.1.1/orukeet-0.1.1-py3-none-any.whl), installs PyObjC, and writes `installation.json`.

The first launch asks for **Microphone** and **Accessibility**. Both are granted to the terminal you launched from (Terminal or iTerm), because that is the app macOS sees. Accessibility is what lets the hotkey work while another app is focused, and what lets Command-V land in that app.

## Use

1. Click a text field.
2. Hold **Right Option**. Speak.
3. Release. The transcript is pasted, and the previous clipboard contents come back.

`ORUKEET_HOTKEY` changes the key:

| Value | Key |
| --- | --- |
| `right-option` (default) | Right Option |
| `globe` or `fn` | Globe / Fn |
| `right-shift` | Right Shift |
| `f5` | F5 |
| a number | that macOS key code |

## Files

- `dictation/agent.py` — start here
- `dictation/hotkey.py` — hold-to-talk
- `dictation/record.py` — microphone to WAV
- `dictation/paste.py` — Command-V into the focused app
- `dictation/client.py` — HTTP call to the worker
- `server/orukeet_server.py` — keeps Orukeet loaded
- `launchd/` — optional login item; edit the absolute path first

Audio stays on `127.0.0.1`. To try the worker without the model, set `ORUKEET_STUB=1`.

## Tests

```bash
python3 -m unittest tests.test_dictation tests.test_orukeet_server
```

These cover config, the HTTP client, and the worker. They do not press keys or open the microphone.

## License

This code is MIT. Orukeet weights are CC BY-SA 4.0 with NVIDIA’s foundation attribution. See the [model card](https://huggingface.co/oruk/orukeet).
