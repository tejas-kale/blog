# Publisher-grade TTS preprocessing pipeline (operational reference)

Operational follow-up to [ai-article-narration.md](./ai-article-narration.md). Focus: **what to do, in what order**, with **libraries/APIs**, and **what each engine accepts**. Primary sources only; unconfirmed items flagged.

*Research compiled from primary sources, September 2026.*

---

## 1. Article extraction (not TTS)

Goal: produce a **clean article body** (HTML or Markdown). Extraction is separate from synthesis; paywalled pages cannot be reliably extracted without legitimate access to the article text.

### Paywalled pages

| What works | What does not |
|---|---|
| Paste or import **clean body HTML/Markdown** you already have rights to (CMS export, Readability view while logged in, saved HTML) | Automated circumvention of paywalls |
| `trafilatura.fetch_url()` on URLs your session can fetch | Expecting URL-only extraction to succeed on hard paywalls without auth cookies |

**Operational rule:** treat **clean body text as a required input artifact**. If you only have a paywalled URL, obtain the body through your normal reading workflow first; do not build the CLI around paywall bypass.

### Mozilla Readability (`mozilla/readability`, `go-shiori/go-readability`)

Readability scores DOM nodes, removes low-value sections, and returns `{ title, content, textContent, … }`. It is **not TTS-aware**.

**Removed / deprioritized** ([Readability.js source](https://github.com/mozilla/readability/blob/master/Readability.js); [go-readability README](https://github.com/go-shiori/go-readability/blob/master/README.md)):

- Scripts, styles, `noscript`, presentational attributes
- Elements matching `unlikelyCandidates` regex: `banner`, `complementary`, `foot`, `footer`, `footnote`, `masthead`, `media`, `outbrain`, `promo`, `related`, `share`, `sidebar`, `sponsor`, `tags`, `tool`, `widget`, etc.
- Navigation roles: `menu`, `menubar`, `navigation`, `dialog`, …
- High link-density blocks, image-heavy non-article blocks, share widgets
- Empty `div`/`section`/`header` shells

**Kept (if inside winning candidate block):**

- Paragraphs, headings, blockquotes, lists, `pre`, **`table`**, **`img`** (images remain in HTML; `textContent` may include `alt` text depending on DOM)
- Pull quotes inside the article body (no special “pull quote” filter—they stay if the block scores as content)
- **`figure` / caption text** if not pruned by heuristics — **not explicitly dropped** by Readability; captions often survive in body HTML

**Not documented:** explicit footnote/endnote handling. Footnote sections with class/id matching `footnote` in `unlikelyCandidates` may be removed; inline footnote markers may remain as superscript numbers.

**Go port:** line-by-line port of Readability.js ([go-readability README](https://github.com/go-shiori/go-readability/blob/master/README.md)). v2 maintained at [codeberg.org/readeck/go-readability/v2](https://codeberg.org/readeck/go-readability).

### trafilatura

Library for discovery, extraction, and text processing ([trafilatura docs](https://trafilatura.readthedocs.io/en/latest/)).

**Removed by default:** navigation, headers, footers, sidebars, ads (boilerplate outside main content zone).

**Optional via `extract()` flags** ([usage-python](https://trafilatura.readthedocs.io/en/latest/usage-python.html)):

| Flag | Default | Effect |
|---|---|---|
| `include_comments` | `True` | Comment sections at article bottom |
| `include_tables` | `True` | Table cell text |
| `include_links` | `False` | Keep `href` targets |
| `include_images` | `False` | Keep `img` alt/src/title |
| `include_formatting` | `False` | Bold/italic structure |

**For TTS prep:** use `include_comments=False`, `include_tables=False`, `include_images=False`, `include_links=False`, `output_format='markdown'` or `'txt'`.

**Captions / footnotes:** no dedicated caption filter. Image captions in `<figcaption>` stay if inside extracted body. Footnotes depend on HTML structure; use `prune_xpath` for site-specific removal ([core module](https://trafilatura.readthedocs.io/en/latest/_modules/trafilatura/core.html)).

**Fallback:** `html2txt()` extracts **all** visible text including footers ([usage-python](https://trafilatura.readthedocs.io/en/latest/usage-python.html)).

### Comparison for narration pipelines

| Tool | Best for | Captions | Footnotes | Tables | Pull quotes |
|---|---|---|---|---|---|
| **trafilatura** | Batch URL corpus, metadata | Kept unless pruned | Site-dependent; use `prune_xpath` | Optional (`include_tables`) | Kept in body |
| **Readability** | Browser/Go CLI extraction | Heuristic; often kept | `footnote` class likely dropped | Kept in candidate | Kept in body |
| **go-readability** | Same as Readability in Go | Same | Same | Same | Same |

**Publisher pattern** (from [BeyondWords](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/)): strip image captions and non-spoken HTML **after** extraction, before TTS.

---

## 2. Text cleaning before synthesis (ordered pipeline)

Apply stages **in this order**. Tag each technique: **TN** = spoken-form expansion (write out “twenty-three percent”), **SSML** = markup tags, **PLS** = W3C lexicon, **IPA** = inline phonemes.

### Stage A — Structural strip (must)

1. Remove bylines duplicated in header/footer, “Subscribe”, nav crumbs, related links, social embeds, stock tickers, photo credits **unless** you want them spoken.
2. Drop `<script>`, `<style>`, `<iframe>`, ad containers.
3. **Markdown links** `[text](url)` → speak **`text` only**; drop bare URLs and `[text](url)` URL portion.
4. **Image alts:** drop for narration (BeyondWords strips captions/ non-spoken elements — [blog](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/)). *Should for v0.*
5. **Code blocks:** replace with “Code block omitted” or skip section (*skip for v0* unless technical blog).
6. **Tables:** flatten to prose or omit (*omit for v0*; enable when sports/finance articles are common).

Libraries: custom regex + [markdown-it](https://github.com/markdown-it/markdown-it) or Python `markdown` AST walk. No single vendor owns this step.

### Stage B — Unicode normalization (must)

1. NFC normalize ([Unicode TR #15](https://unicode.org/reports/tr15/)) — Python `unicodedata.normalize('NFC', text)`.
2. Replace typographic punctuation with ASCII equivalents for TN compatibility:
   - `"` `"` → `"`; `'` `'` → `'`
   - `—` `–` → `, ` or `. ` (em-dash → clause break for news pacing)
   - `…` → `.`
   - `\u00a0` (NBSP) → regular space
3. Strip zero-width and combining junk; remove control chars except `\n`.

### Stage C — Spoken-form text normalization / TN (must for plain-text engines)

Convert written forms to speakable prose **before** SSML:

| Pattern | TN output example | Tool |
|---|---|---|
| `$123` / `€50` | “one hundred twenty-three dollars” | [NeMo Text Processing](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/nlp/text_normalization/wfst/wfst_text_normalization.html) / [NeMo-text-processing repo](https://github.com/NVIDIA/NeMo-text-processing) |
| `23%` | “twenty-three percent” | NeMo TN; [Amazon Polly `<say-as interpret-as="unit">`](https://docs.aws.amazon.com/polly/latest/dg/say-as-tag.html) |
| `2019–2023` | “twenty nineteen to twenty twenty-three” | Pre-expand ranges with “to” ([Cartesia normalization docs](https://docs.cartesia.ai/build-with-cartesia/capability-guides/text-normalization) — hyphenated year ranges not auto-normalized) |
| `Mr.` / `U.S.` / `NATO` | context-dependent | NeMo context-aware TN ([docs](https://docs.nvidia.com/nemo-framework/user-guide/25.09/nemotoolkit/nlp/text_normalization/nn_text_normalization.html)); Polly `<say-as interpret-as="characters">` for spell-out |
| `3Q` / `YoY` / `422M` | domain expansions | [BeyondWords AI preprocessing](https://beyondwords.io/blog/cleaner-audio-at-scale-introducing-ai-preprocessing-2/) (vendor); manual rules for CLI |
| Ordinals `23rd` | “twenty-third” | NeMo TN |
| Scores `40–0` | “forty love” (tennis) | BeyondWords AI preprocessing (contextual) |
| Homographs `read`/`read` | disambiguated spoken form | BeyondWords NLP + Polly `<w role="amazon:VB">` ([Polly homograph docs](https://docs.aws.amazon.com/polly/latest/dg/phoneme-tag.html)) |

**WeTextProcessing** ([GitHub](https://github.com/pengzhendong/wetext)): FST-based TN/ITN for **zh/en/ja**; `--operator tn` CLI. Good lightweight alternative to full NeMo install.

**NeMo `Normalizer`** example ([TTS configs](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tts/configs.html.md)):

```python
from nemo_text_processing.text_normalization.normalize import Normalizer
normalizer = Normalizer(lang="en", input_case="cased")
spoken = normalizer.normalize(text, punct_pre_process=True, punct_post_process=True)
```

**Classification of techniques:**

| Technique | Type | When |
|---|---|---|
| NeMo / WeTextProcessing / Cartesia `normalization: auto` | **TN** | Always for plain-text models |
| Polly `<say-as>`, `<sub alias>` | **SSML** | Polly/Azure neural |
| Polly / Google `<phoneme alphabet="ipa">` | **SSML + IPA** | Fixed pronunciation |
| PLS lexicon files | **PLS** | Polly ([managing lexicons](https://docs.aws.amazon.com/polly/latest/dg/managing-lexicons.html)), Google Cloud custom pronunciations, ElevenLabs `.pls` dictionaries ([docs](https://elevenlabs.io/docs/eleven-agents/customization/voice/pronunciation-dictionary)) |
| BeyondWords substitution / IPA rules | **Alias / IPA** (dashboard, not raw SSML file) | Publisher CMS |
| Gemini `[long pause]` / Eleven `[whispers]` | **Inline tags** (not SSML) | Prompt-controlled TTS |

### Stage D — Abbreviation & entity rules (should)

Maintain CSV/JSON alias table: `NATO` → “N A T O” or “North Atlantic Treaty Organization” per house style. Merge at runtime into TN whitelist ([NeMo whitelist TSV](https://docs.nvidia.com/nemo-framework/user-guide/24.12/nemotoolkit/nlp/text_normalization/wfst/wfst_text_normalization.html)) or PLS `<alias>`.

### Stage E — SSML / prosody layer (engine-dependent; skip for v0 on plain-text-only engines)

- **Breaks:** `<break time="500ms"/>` — [W3C SSML 1.1 `break`](http://www.w3.org/TR/speech-synthesis/)
- **Lexicon hook:** `<lexicon uri="…" type="application/pls+xml"/>` — [W3C SSML lexicon](http://www.w3.org/TR/speech-synthesis/#S3.1.5)
- **Polly newscaster:** `<amazon:domain name="news">` — [Polly newscaster](https://docs.aws.amazon.com/polly/latest/dg/newscaster-voices.html)

Only generate SSML if target engine accepts it (see §3).

---

## 3. SSML vs plain text by engine

**Legend:** SSML support = **none** / **partial** / **full** (per vendor docs). Do not assume cross-vendor SSML compatibility.

| Engine | SSML | Phoneme alphabet | Max input / request | Recommended chunk | Stitching / context | Long-form stability notes |
|---|---|---|---|---|---|---|
| **ElevenLabs** Multilingual v2 | **Partial** — `<break>`, phoneme on Flash v2; v3 uses audio tags not SSML breaks ([help](https://help.elevenlabs.io/hc/en-us/articles/24352686926609), [best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)) | CMU Arpabet, IPA (Flash v2); IPA native on v3 | 10,000 chars (Multilingual v2); 40,000 (Flash v2.5) ([models](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)) | ≤800 chars for quality ([troubleshooting](https://elevenlabs.io/docs/eleven-creative/troubleshooting)) | `previous_request_ids` / `previous_text` ([stitching guide](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching)); **not on eleven_v3** | Volume drift, whispering on long gens ([help](https://help.elevenlabs.io/hc/en-us/articles/13416095176977)); `{ } < > [ ]` hurt quality |
| **Google Gemini TTS** | **None** (plain text + optional style prompt / audio tags) ([Gemini speech gen](https://ai.google.dev/gemini-api/docs/speech-generation), [Cloud Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)) | Inline `[whispers]` etc., not IPA SSML | 8,192 input tokens; Cloud: ≤4,000 bytes text + ≤4,000 bytes prompt; ~655 s output cap | Split at paragraph; Google recommends smaller chunks for quality | No request stitching; manual concat | Quality drifts after few minutes ([Gemini API](https://ai.google.dev/gemini-api/docs/speech-generation)); occasional 500 text-token responses |
| **Amazon Polly** Neural | **Full** subset ([supported tags](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html)) | IPA, X-SAMPA; ja yomigana ([phoneme tag](https://docs.aws.amazon.com/polly/latest/dg/phoneme-tag.html)) | 100,000 billable chars (S0 SSML file); 10 min audio max ([quotas](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits)) | 3,000–5,000 chars plain SSML body | Lexicon + consistent voice; no prosody stitching API | Newscaster `<amazon:domain name="news">` for news voice |
| **Azure Neural / MAI-Voice-2** | **Partial** — SSML used internally; OpenRouter exposes plain params + `style` ([OpenRouter TTS](https://openrouter.ai/docs/guides/overview/multimodal/tts)) | Via Azure SSML when using Azure directly; abstracted on OpenRouter | 100,000 billable chars (S0); 10 min audio ([Azure quotas](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits)) | 2,000–4,000 chars | `style`/`styledegree` provider options | Max 5 `<voice>` elements per SSML on Azure ([community report](https://techcommunity.microsoft.com/discussions/azure-ai-foundry-discussions/microsoft-azure-tts-cognitive-service-voice-limit-issue/1147673)) |
| **OpenAI TTS / gpt-4o-mini-tts** | **None** — use `instructions` instead ([OpenAPI spec](https://platform.openai.com/docs/static/api-definition.yaml)) | No phoneme tags | **4,096 chars** input; instructions also ≤4,096 | ~3,000–4,000 chars | Repeat same `instructions` each chunk; manual concat | No SSML; style via instructions only |
| **Cartesia Sonic 3.5** | **None** — `transcript` plain text + `normalization` ([text normalization](https://docs.cartesia.ai/build-with-cartesia/capability-guides/text-normalization)) | Pronunciation **dictionaries** (IPA/sounds-like), not SSML | **Unconfirmed** hard cap in public docs; chunk at ~4k for safety | 2,000–4,000 chars | Client-side PCM concat ([normalizer examples](https://docs.cartesia.ai/build-with-cartesia/capability-guides/text-normalization)) | Built-in TN; heteronyms without preprocessing per [Sonic 3.5 page](https://docs.cartesia.ai/build-with-cartesia/tts-models/latest) |
| **Kokoro 82M** (local / OpenRouter) | **None** | G2P via [misaki](https://github.com/hexgrad/misaki) internally | 4,096 tokens on OpenRouter ([model page](https://openrouter.ai/hexgrad/kokoro-82m)) | 500–1,000 chars | Manual concat; optional crossfade | Lightweight; [model card](https://huggingface.co/hexgrad/Kokoro-82M) claims quality comparable to larger models |
| **Piper** (local) | **None** | Built-in G2P (CMUdict + rules) per [CrispASR tts.md](https://github.com/CrispStrobe/CrispASR/blob/main/docs/tts.md) | Limited by sentence length / ONNX model | Sentence-level | Manual | 22 kHz; CPU-friendly; **conversational** not newscaster |
| **Chatterbox** (local) | **None** | Voice clone via GGUF | Model-dependent | Sentence | Manual | Flow-matching; expressive ([CrispASR docs](https://github.com/CrispStrobe/CrispASR/blob/main/docs/tts.md)) |
| **StyleTTS2** | **None** (research codebase) | Phoneme pipeline in training | N/A API | N/A | N/A | Architecture paper ([arXiv:2306.07691](https://arxiv.org/abs/2306.07691)); Kokoro builds on it |
| **Fish Speech / Fish Audio S1/S2** | **None** — parenthetical emotion controls ([OpenRouter s1](https://openrouter.ai/fish-audio/s1)) | Voice cloning via `input_references` on OpenRouter | Priced per UTF-8 byte | 1,000–2,000 chars | Manual | Expressive narration; multilingual |
| **Qwen TTS** (DashScope via OpenRouter) | **Unconfirmed** SSML on OpenRouter path | **Unconfirmed** | **Unconfirmed** max chars on OpenRouter ([flash model](https://openrouter.ai/qwen/qwen-audio-3.0-tts-flash)) | 2,000 chars assumed | Manual | Alibaba DashScope backend |
| **Coqui / XTTS** | **None** in inference API | Reference audio cloning | Model card / local VRAM bound | Sentence | Manual | [coqui-ai/TTS](https://github.com/coqui-ai/TTS) — community repo; no hosted SSML |
| **Orpheus 3B** (Canopy Labs / OpenRouter) | **None** | Preset voices | 4,096 context ([OpenRouter](https://openrouter.ai/canopylabs/orpheus-3b-0.1-ft)) | 800–1,500 chars | Manual | Narration-oriented; [Canopy Labs](https://canopylabs.ai/models/orpheus) cites 1M+ downloads |

### Google Cloud TTS (non-Gemini) — for comparison

Classic Cloud TTS: **SSML partial** ([Cloud SSML docs](https://cloud.google.com/text-to-speech/docs/ssml)); input ≤ **5,000 bytes** ([API reference](https://googleapis.github.io/google-api-python-client/docs/dyn/texttospeech_v1.text.html)).

---

## 4. Chunking & audio assembly

### Split strategy

1. **Primary boundary:** sentence ends (`.?!` + closing quote). Use **regex + abbreviation guard** (`Mr.`, `Mrs.`, `U.S.`, `e.g.`, `i.e.`, `Dr.`, `vs.`, `St.`) — do not split on those periods.
2. **Secondary:** paragraph boundaries when approaching char limit.
3. **Hard cap:** stay **10–15% below** engine max (e.g. 3,500 chars for OpenAI 4,096).
4. **Never:** mid-word or mid-number.

Libraries: `pysbd` (rule-based sentence boundary) or spaCy `sentencizer` with abbreviation overrides.

### Cross-chunk prosody

| Engine | Mechanism |
|---|---|
| ElevenLabs | `previous_request_ids` (IDs <2 h old) or `previous_text`/`next_text` ([stitching](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching)) |
| OpenAI | Same `instructions` string every chunk |
| Gemini | Split + accept drift; optional repeated style preamble |
| **No native stitching** (Kokoro, Orpheus, OpenRouter models) | **Overlap trick:** include last sentence of chunk N as first sentence of chunk N+1, trim in assembly — *unconfirmed quality benefit; flag as heuristic* |

### Audio concat & loudness

1. Synthesize chunks to **WAV/PCM** (same sample rate, e.g. 24 kHz or 48 kHz).
2. **Crossfade:** 20–50 ms linear crossfade at chunk joins (ffmpeg `acrossfade`) — reduces clicks; *publisher primary sources silent on this*.
3. **Loudness normalize final master:**
   - **EBU R128** target: integrated **−16 LUFS** for podcast/article audio (streaming convention); **−23 LUFS** is broadcast EBU default ([EBU R128 via ffmpeg loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)).
   - **Two-pass** `loudnorm` with `print_format=json` then `linear=true` ([ffmpeg loudnorm filter](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)).

```bash
# Pass 1 — measure
ffmpeg -i chunk.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -

# Pass 2 — apply measured_* values from JSON
ffmpeg -i joined.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=...:linear=true" -ar 48000 article.wav
```

4. Verify with `ebur128` filter or `ffmpeg-normalize` ([EBU mode](https://github.com/slhck/ffmpeg-normalize)).

---

## 5. Pronunciation memory for iteration (1–2 week CLI loop)

### Storage formats

| Format | Use | Spec |
|---|---|---|
| **PLS XML** | Polly, Google, ElevenLabs (partial) | [W3C PLS 1.0](http://www.w3.org/TR/pronunciation-lexicon/) — `<lexeme><grapheme>…</grapheme><alias>…</alias></lexeme>` or `<phoneme>` |
| **CSV alias table** | Engine-agnostic TN | `written,spoken,category,scope` |
| **IPA inline** | Single-word fixes | SSML `<phoneme>` where supported |

### Human correction workflow

1. **Listen** to rendered MP3; note **wall-clock timestamp** (ffprobe / player).
2. **Map timestamp → chunk + sentence** using cumulative duration metadata stored at synthesis time (`chunk_index`, `char_offset`, `duration_ms` per chunk).
3. **Record correction** in `pronunciations.csv`:
   ```csv
   grapheme,spoken_form,type,added_at
   Zelenskyy,Zelensky,alias,2026-09-04
   F-16,eff sixteen,alias,2026-09-04
   ```
4. **Re-run pipeline** from Stage C (TN) with merged lexicon; regenerate **only affected chunks** if chunk hash changed.
5. Optional: export accumulated rules to PLS for Polly/Azure if you migrate engines.

BeyondWords equivalent: dashboard pronunciation rules ([blog](https://beyondwords.io/blog/enhancing-ai-generated-audio-articles-with-pronunciation-rules-2/)) — substitute, spell-out, IPA.

---

## 6. Cheaper well-regarded models (quality vs $)

### Hosted / API (September 2026 primary pricing)

| Model | Price | Evidence of quality | News / narration fit | Preprocessing burden |
|---|---|---|---|---|
| **OpenRouter Kokoro 82M** | **$0.62/M chars** ([page](https://openrouter.ai/hexgrad/kokoro-82m)) | HF model card: comparable to larger models ([Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)); TTS Arena #52 ([OpenRouter benchmarks](https://openrouter.ai/hexgrad/kokoro-82m)) | Neutral/audiobook; not newscaster | **High** — full TN required |
| **OpenRouter Orpheus 3B** | **$7/M chars** ([page](https://openrouter.ai/canopylabs/orpheus-3b-0.1-ft)) | Canopy Labs: 1M+ downloads ([site](https://canopylabs.ai/models/orpheus)); “narration” on OR page | Expressive narration | **High** |
| **OpenRouter MAI-Voice-2** | **$22/M chars** ([page](https://openrouter.ai/microsoft/mai-voice-2)) | Design Arena Top 100% TTS ([page](https://openrouter.ai/microsoft/mai-voice-2)); “media narration, long-form” | **Best OpenRouter news fit** | **Medium** — Azure TN partial via backend; still expand numbers |
| **OpenRouter MAI-Voice-2-Flash** | **$15/M chars** ([page](https://openrouter.ai/microsoft/mai-voice-2-flash)) | Same family; lower latency | Interactive/narration | Medium |
| **OpenRouter Deepgram Flux (free)** | **Free** ([page](https://openrouter.ai/deepgram/flux-tts:free)) | Deepgram voice catalog; no arena rank | English conversational | High |
| **Amazon Polly Neural** | **~$16/M chars** (AWS pricing) | WaPo 2021 production use ([AWS blog](https://aws.amazon.com/blogs/machine-learning/the-washington-post-website-launches-audio-articles-voiced-by-amazon-polly/)); newscaster voices | **Newscaster** `<amazon:domain name="news">` | **Low** with SSML+lexicon |
| **Google Cloud Neural2** | **~$16/M chars** ([Cloud pricing](https://cloud.google.com/text-to-speech/pricing)) | Industry default | SSML + news voices | Low–medium |
| **Cartesia Sonic 3.5** | **~1 credit/char** ([pricing](https://docs.cartesia.ai/pricing)) | Vendor: “#1 naturalness” ([Sonic page](https://docs.cartesia.ai/build-with-cartesia/tts-models/latest)) | Conversational / agent | **Low** — built-in TN |
| **ElevenLabs Multilingual v2** | **~$0.12–0.30/1k chars** (plan-dependent) ([pricing](https://elevenlabs.io/pricing)) | TIME Audio Native partnership ([blog](https://elevenlabs.io/blog/time)) | Editorial; long-form drift issues | Medium + `apply_text_normalization` |
| **Gemini 2.5/3.1 Flash TTS** | Token-priced ([Cloud Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)) | Google official; long-form drift documented | Prompt-controlled | **High** (plain text only) |

### Local / free (hardware)

| Model | License | Hardware | Quality evidence | Style |
|---|---|---|---|---|
| **Kokoro 82M** | Apache-2.0 ([HF](https://huggingface.co/hexgrad/Kokoro-82M)) | CPU ok; GPU faster | HF card + [StyleTTS2 paper](https://arxiv.org/abs/2306.07691) | Neutral narration |
| **Piper** | GPL ([rhasspy/piper](https://github.com/rhasspy/piper)) | **Raspberry Pi / CPU**; ~30 MB/voice ([CrispASR](https://github.com/CrispStrobe/CrispASR/blob/main/docs/tts.md)) | Community standard for local | Robotic–acceptable |
| **Chatterbox** | Model-dependent | ~880 MB GPU ([CrispASR](https://github.com/CrispStrobe/CrispASR/blob/main/docs/tts.md)) | Voice clone demos | Expressive |
| **Coqui XTTS** | CPML ([GitHub](https://github.com/coqui-ai/TTS)) | GPU 4–8 GB+ typical | Widely forked | Clone-based |
| **Orpheus 3B** (self-host) | Check model license on HF | GPU | Canopy Labs adoption stats | Conversational narration |

---

## 7. OpenRouter TTS catalog (September 2026)

OpenRouter exposes **real audio-out models** via `POST /api/v1/audio/speech` returning **raw audio bytes** (not chat wrappers). Discovery: `GET /api/v1/models?output_modalities=speech` ([TTS guide](https://openrouter.ai/docs/guides/overview/multimodal/tts), [create speech API](https://openrouter.ai/docs/api/api-reference/tts/create-speech)).

**Catalog size:** **18 models** (queried 2026-09-04). All listed slugs verified against live API.

**Not in catalog (despite docs examples):** `openai/gpt-4o-mini-tts-2025-12-15` appears in [OpenRouter TTS docs examples](https://openrouter.ai/docs/guides/overview/multimodal/tts) but **was not returned** by `output_modalities=speech` — **unconfirmed if temporarily delisted**.

### Full model table

| Slug | Provider | Pricing | Input | SSML | Streaming | Max input / context | Notes |
|---|---|---|---|---|---|---|---|
| `deepgram/flux-tts:free` | Deepgram | **Free** | Plain text | **None** | Response stream | **Unconfirmed** char cap | 36 English voices ([page](https://openrouter.ai/deepgram/flux-tts:free)) |
| `deepgram/aura-2` | Deepgram | **$30/M chars** | Plain | **None** | Stream | **Unconfirmed** | 90 multilingual voices ([page](https://openrouter.ai/deepgram/aura-2)) |
| `fish-audio/s1` | Fish Audio | **$15/M UTF-8 bytes** | Plain + `(emotion)` tags | **None** | Stream | **Unconfirmed** | Parenthetical style controls ([page](https://openrouter.ai/fish-audio/s1)) |
| `fish-audio/s2-pro` | Fish Audio | **$15/M bytes** | Plain | **None** | Stream | **Unconfirmed** | Multi-speaker ([API listing](https://openrouter.ai/api/v1/models?output_modalities=speech)) |
| `fish-audio/s2.1-pro` | Fish Audio | **$15/M bytes** | Plain | **None** | Stream | **Unconfirmed** | Voice clone via `input_references` ([TTS guide](https://openrouter.ai/docs/guides/overview/multimodal/tts)) |
| `fish-audio/s2.1-pro-free:free` | Fish Audio | **Free** | Plain | **None** | Stream | **Unconfirmed** | Prototype tier; non-production SLA ([API listing](https://openrouter.ai/api/v1/models?output_modalities=speech)) |
| `microsoft/mai-voice-2` | Microsoft/Azure | **$22/M chars** | Plain | **Partial** (Azure SSML internal; OR exposes `style`/`styledegree`) | Stream | **Unconfirmed** per-request char cap; 10 min audio on Azure direct ([quotas](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits)) | **Media narration**; Design Arena top tier ([page](https://openrouter.ai/microsoft/mai-voice-2)) |
| `microsoft/mai-voice-2-flash` | Microsoft/Azure | **$15/M chars** | Plain | **Partial** | Stream | Same as above | Low-latency variant ([page](https://openrouter.ai/microsoft/mai-voice-2-flash)) |
| `google/gemini-3.1-flash-tts-preview` | Google Vertex | **$1/M input tokens + $20/M output tokens** | Plain + audio tags | **None** | **Unconfirmed** on OR | **32,768** context ([page](https://openrouter.ai/google/gemini-3.1-flash-tts-preview)); Cloud 655 s output cap ([Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)) | Long-form drift per Google ([Gemini API](https://ai.google.dev/gemini-api/docs/speech-generation)) |
| `hexgrad/kokoro-82m` | DeepInfra/Together | **$0.62/M chars** | Plain | **None** | Stream | **4,096** context ([page](https://openrouter.ai/hexgrad/kokoro-82m)) | 54 voices; 8 languages |
| `mistralai/voxtral-mini-tts-2603` | Mistral | **$16/M chars** | Plain | **None** | Stream | **4,096** context ([page](https://openrouter.ai/mistralai/voxtral-mini-tts-2603)) | 30 voices; zero-shot clone **Unconfirmed** on OR |
| `canopylabs/orpheus-3b-0.1-ft` | DeepInfra/Together | **$7/M chars** | Plain | **None** | Stream | **4,096** context ([page](https://openrouter.ai/canopylabs/orpheus-3b-0.1-ft)) | 7 voices; narration |
| `sesame/csm-1b` | DeepInfra | **$7/M chars** | Plain | **None** | Stream | **4,096** context ([page](https://openrouter.ai/sesame/csm-1b)) | Conversational |
| `x-ai/grok-voice-tts-1.0` | SpaceXAI | **$15/M chars** | Plain + inline speech tags | **None** | Stream | **15,000 chars**/request ([page](https://openrouter.ai/x-ai/grok-voice-tts-1.0)) | 5 voices; TTS Arena #27 |
| `qwen/qwen-audio-3.0-tts-flash` | Alibaba/DashScope | **$15/M chars** | Plain | **Unconfirmed** | Stream | **Unconfirmed** | 2 voices ([API listing](https://openrouter.ai/api/v1/models?output_modalities=speech)) |
| `qwen/qwen-audio-3.0-tts-plus` | Alibaba/DashScope | **$20/M chars** | Plain | **Unconfirmed** | Stream | **Unconfirmed** | Higher quality tier |
| `minimax/speech-2.8-turbo` | MiniMax | **$60/M chars** | Plain | **None** | Stream | **Unconfirmed** | 45 voices ([page](https://openrouter.ai/minimax/speech-2.8-turbo)) |
| `minimax/speech-2.8-hd` | MiniMax | **$100/M chars** | Plain | **None** | Stream | **Unconfirmed** | HD tier ([API listing](https://openrouter.ai/api/v1/models?output_modalities=speech)) |

Common OpenRouter request shape ([create speech](https://openrouter.ai/docs/api/api-reference/tts/create-speech)):

```json
{
  "model": "canopylabs/orpheus-3b-0.1-ft",
  "input": "Normalized article chunk text.",
  "voice": "tara",
  "response_format": "mp3"
}
```

Response: **raw audio** (`audio/mpeg` or `audio/pcm`); `X-Generation-Id` header for tracking.

### Recommended OpenRouter model for this CLI

**Pick: `microsoft/mai-voice-2`** (voice: `en-US-Harper:MAI-Voice-2`, `response_format: mp3`)

**Justification (primary sources only):**

| Criterion | Assessment |
|---|---|
| **Naturalness** | OpenRouter / Design Arena: **Top 100% Text-To-Speech** and **Audiorealism Top 100%** ([MAI-Voice-2 page](https://openrouter.ai/microsoft/mai-voice-2)) |
| **Long-form journalism fit** | Vendor description: “**media narration** … **long-form voice applications**” ([same page](https://openrouter.ai/microsoft/mai-voice-2)) — only OpenRouter slug with explicit publisher-narration positioning |
| **Cost** | **$22/M chars** vs ElevenLabs plan pricing typically **$120–300+/M chars** ([ElevenLabs pricing](https://elevenlabs.io/pricing)) — materially cheaper |
| **Latency** | P50 ~0.91 s on OpenRouter ([MAI-Voice-2 page](https://openrouter.ai/microsoft/mai-voice-2)) |
| **Preprocessing** | OpenRouter path is **plain text**; Azure uses SSML internally but you must still run **Stages A–C** (strip chrome, TN for numbers/acronyms). Optional `provider.options.azure.style` for delivery ([OpenRouter TTS guide](https://openrouter.ai/docs/guides/overview/multimodal/tts)) — not a substitute for TN |
| **Audio vs text wrapper** | Confirmed **audio-out** modality; `output_modalities: ["speech"]` ([API listing](https://openrouter.ai/api/v1/models?output_modalities=speech)) |
| **Stability** | OpenRouter reports **54.91% availability (3d)** on MAI-Voice-2 ([page](https://openrouter.ai/microsoft/mai-voice-2)) — **risk for daily iteration** |

**Fallback when MAI-Voice-2 errors:** `canopylabs/orpheus-3b-0.1-ft` ($7/M, “suited for narration”, 99.63% availability, 4K context — [page](https://openrouter.ai/canopylabs/orpheus-3b-0.1-ft)).

**Budget / local fallback:** `hexgrad/kokoro-82m` on OpenRouter ($0.62/M) or self-hosted Kokoro — requires **full TN pipeline**; TTS Arena rank #52 vs MAI-Voice-2 top tier.

**Do not default to Gemini on OpenRouter for long articles:** Google documents quality drift and recommends chunking ([Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation)); token pricing unpredictable for 10k-word features.

---

## 8. Recommended default pipeline (personal CLI)

| Stage | Action | Priority v0 |
|---|---|---|
| **0** | Obtain **clean body Markdown/HTML** (CMS, saved page, auth fetch you already use) | **Must** |
| **1** | Extract: `trafilatura.extract(..., include_comments=False, include_tables=False, include_images=False, output_format='markdown')` | **Must** |
| **2** | Strip chrome regex: bylines, “Subscribe”, URLs, social embeds | **Must** |
| **3** | Markdown: links → anchor text only; drop code blocks & tables | **Should** |
| **4** | Unicode normalize (NFC, quotes, dashes, NBSP) | **Must** |
| **5** | TN: NeMo `Normalizer(lang='en')` or WeTextProcessing for en/zh | **Must** |
| **6** | Custom CSV/PLS lexicon merge (names, tickers, house style) | **Should** |
| **7** | Sentence chunking ≤3,500 chars with abbreviation guard (`pysbd` + custom list) | **Must** |
| **8** | Synthesize via **OpenRouter** `POST /api/v1/audio/speech` model **`microsoft/mai-voice-2`**, voice **`en-US-Harper:MAI-Voice-2`**; fallback **`canopylabs/orpheus-3b-0.1-ft`** | **Must** |
| **9** | Concat chunks (ffmpeg); 30 ms crossfade optional | **Should** |
| **10** | Two-pass **ffmpeg loudnorm** at **−16 LUFS**, TP **−1.5 dBTP** | **Should** |
| **11** | Store chunk manifest (offsets, durations) for timestamp corrections | **Should** |
| **12** | Human listen → update `pronunciations.csv` → re-run from stage 5 | **Should** (core to 1–2 week iteration) |
| **13** | SSML layer (Polly/Azure direct) | **Skip v0** (using OpenRouter plain-text path) |
| **14** | AI preprocessing (BeyondWords-style LLM pass) | **Skip v0** |

### v0 minimum stack

- Python 3.11+
- `trafilatura`, `nemo_text_processing` *or* `wetextprocessing`
- `pysbd`, `ffmpeg`
- OpenRouter client (`openai` SDK with `base_url=https://openrouter.ai/api/v1`)
- SQLite or JSON for lexicon + chunk manifest

---

## Source list

### Extraction
- [trafilatura docs](https://trafilatura.readthedocs.io/en/latest/)
- [trafilatura usage-python](https://trafilatura.readthedocs.io/en/latest/usage-python.html)
- [Mozilla Readability.js](https://github.com/mozilla/readability/blob/master/Readability.js)
- [go-readability README](https://github.com/go-shiori/go-readability/blob/master/README.md)

### Normalization & SSML
- [NVIDIA NeMo Text Processing](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/nlp/text_normalization/wfst/wfst_text_normalization.html)
- [NeMo-text-processing GitHub](https://github.com/NVIDIA/NeMo-text-processing)
- [WeTextProcessing GitHub](https://github.com/pengzhendong/wetext)
- [BeyondWords SSML/NLP blog](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/)
- [BeyondWords AI preprocessing](https://beyondwords.io/blog/cleaner-audio-at-scale-introducing-ai-preprocessing-2/)
- [Amazon Polly SSML tags](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html)
- [Amazon Polly say-as](https://docs.aws.amazon.com/polly/latest/dg/say-as-tag.html)
- [Amazon Polly lexicons](https://docs.aws.amazon.com/polly/latest/dg/managing-lexicons.html)
- [Google Cloud SSML](https://cloud.google.com/text-to-speech/docs/ssml)
- [W3C SSML 1.1](http://www.w3.org/TR/speech-synthesis/)
- [W3C PLS](http://www.w3.org/TR/pronunciation-lexicon/)
- [Cartesia text normalization](https://docs.cartesia.ai/build-with-cartesia/capability-guides/text-normalization)

### Engines
- [ElevenLabs TTS capabilities](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)
- [ElevenLabs best practices / SSML](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [ElevenLabs request stitching](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching)
- [Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation)
- [Cloud Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)
- [OpenAI API speech schema](https://platform.openai.com/docs/static/api-definition.yaml)
- [Azure Speech quotas](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits)
- [Cartesia pricing](https://docs.cartesia.ai/pricing)
- [Kokoro-82M model card](https://huggingface.co/hexgrad/Kokoro-82M)
- [Piper / local TTS survey (CrispASR)](https://github.com/CrispStrobe/CrispASR/blob/main/docs/tts.md)
- [Canopy Labs Orpheus](https://canopylabs.ai/models/orpheus)

### OpenRouter
- [OpenRouter TTS guide](https://openrouter.ai/docs/guides/overview/multimodal/tts)
- [Create speech API](https://openrouter.ai/docs/api/api-reference/tts/create-speech)
- [Models API `output_modalities=speech`](https://openrouter.ai/api/v1/models?output_modalities=speech)
- Per-model pages linked in §7 table

### Audio post
- [ffmpeg loudnorm filter](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)

---

## Operational summary (12 bullets)

1. **Acquire clean article body** (Markdown/HTML you have legitimate access to)—never rely on paywall URL scraping alone.
2. **Extract** with trafilatura: `include_comments=False`, `include_tables=False`, `include_images=False`, `output_format='markdown'`.
3. **Strip chrome**: nav, subscribe CTAs, bare URLs, social embeds; markdown links → anchor text only.
4. **Unicode-normalize**: NFC, straight quotes, em-dash → clause break, NBSP → space.
5. **Run spoken-form TN** (NeMo or WeTextProcessing): numbers, currency, %, dates, ordinals, ranges as “X to Y”.
6. **Apply CSV/PLS lexicon** for names, tickers, and recurring acronyms (NATO, U.S., house style).
7. **Chunk at sentence boundaries** with abbreviation guard; stay ≤3,500 chars for 4K-context models.
8. **Synthesize on OpenRouter** (`/api/v1/audio/speech`) with **`microsoft/mai-voice-2`** / `en-US-Harper:MAI-Voice-2`; fallback **`canopylabs/orpheus-3b-0.1-ft`**.
9. **No SSML on OpenRouter path**—all disambiguation must happen in plain-text TN before the API call.
10. **Concat chunks** with ffmpeg; optional 30 ms crossfade between segments.
11. **Master with two-pass ffmpeg loudnorm** at −16 LUFS integrated, −1.5 dBTP true peak.
12. **Iterate pronunciations**: listener timestamps → chunk manifest → update lexicon → re-run TN + affected chunks only.
