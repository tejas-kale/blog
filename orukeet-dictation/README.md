# Orukeet dictation

The program is [`orukeet-dictation.org`](orukeet-dictation.org). That file explains each module and tangles it into the Python files next to it.

In Emacs, open the org file and press `C-c C-v t`. From a shell, `./scripts/tangle.sh`.

On the Mac:

```bash
./scripts/install-orukeet.sh
./scripts/run.sh
```

Hold Right Option in any text field, speak, and release. The tests, which do not need a Mac:

```bash
python3 -m unittest discover -s tests -v
```

Orukeet weights are CC BY-SA 4.0. See the [model card](https://huggingface.co/oruk/orukeet).
