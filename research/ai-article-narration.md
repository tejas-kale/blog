# How publishers get article narration right (and why paste-into-TTS fails)

Publications that sound good in article audio rarely send raw web HTML to a general-purpose TTS API. They combine **CMS-integrated extraction**, **text normalization and SSML**, **chunked synthesis with stitching**, **brand voice selection**, and—where it matters most—**human narration or human review**. The Economist is an outlier in still relying heavily on **professional human broadcasters** for its weekly audio edition, using AI only as a temporary bridge for some breaking-news pieces. Outlets such as TIME, The Washington Post, and (per ElevenLabs) The New Yorker and The Atlantic embed vendor tooling (especially ElevenLabs **Audio Native**) that regenerates narration when article text changes. Naive flows—pasting a URL into ElevenReader or sending full page markup to Gemini or ElevenLabs—skip most of that stack, which explains gibberish tokens, misread numbers, and volume drops on long generations.

---

## Findings with citations

### The Economist

**Human narration remains the default.** The weekly audio edition is “read by professional broadcasters” in the app ([Audio edition help](https://myaccount.economist.com/s/article/Audio-edition), undated; [queue help](https://myaccount.economist.com/s/article/How-do-I-build-a-queue-in-the-app), Jul 22, 2026). Only human-narrated articles can be queued; AI-narrated pieces are excluded until replaced ([queue help](https://myaccount.economist.com/s/article/How-do-I-build-a-queue-in-the-app)).

**AI article narration is explicit, temporary, and unreviewed.** A minority of articles—especially breaking news—use “a third-party text-to-speech AI service.” The audio “has not been reviewed prior to publication,” is labeled AI-narrated, and is “automatically updated with the full human recording around 9 pm GMT on Thursdays” ([TTS policy](https://myaccount.economist.com/s/article/What-is-our-text-to-speech-policy), Jun 5, 2026). The vendor is **not named**.

**AI Audio Briefings use an in-house multi-model pipeline, not verbatim article reading.** Briefings draw on multiple articles; “a large language model processes the articles and generates a script,” other LLMs check accuracy, and “a speech model then turns the script into an audio file, producing a conversation between AI-generated personae.” Curated briefings get editor article selection and script review; personalized briefings are fully automatic and may contain “factual inaccuracies and mispronunciations” ([How we make AI Audio briefings](https://myaccount.economist.com/s/article/How-we-make-AI-Audio-briefings)). The Economist AI Lab is “refining prompts and calibrating models” to reduce errors.

**Corporate stance.** The 2026 annual report notes AI text-to-speech narration among experiments to make journalism “more accessible” ([TEG Annual Report 2026 PDF](https://assets.ctfassets.net/2h5kbjx7tvqe/5Sj00z0ZbrZ7bqdg4ShJRN/13ecb0226dc4c4c4a0f666af3298b215/TEG_Annual_Report_2026.pdf)). The AI content page states people produce journalism and AI “can extend the reach of our journalism by distributing it in new formats,” including “audio narration of articles” ([How are we using AI?](https://myaccount.economist.com/s/article/How-we-handle-AI-generated-content), Jul 9, 2026).

**Vendor for article TTS: unconfirmed.** No Economist primary source names Speechify, BeyondWords, ElevenLabs, Polly, or Google.

---

### The New Yorker / Condé Nast

**ElevenLabs lists The New Yorker as a publishing customer** alongside TIME, The Washington Post, The Atlantic, and HarperCollins ([ElevenLabs Series C announcement](https://elevenlabs.io/blog/series-c), Jan 30, 2025). There is **no** Condé Nast or New Yorker press release equivalent to TIME’s partnership post.

**The New Yorker treats audio as a first-class product surface.** The app’s Audio tab collects “narrated articles and podcasts” spanning “reporting, criticism, fiction, and more” ([A New Home for Audio in the New Yorker App](https://www.newyorker.com/news/news-desk/a-new-home-for-audio-in-the-new-yorker-app)—page updated after initial publication; fetched Sep 2026).

**AI vs human policy (partial).** Fiction is handled separately via **The Writer’s Voice** podcast, where authors read their own stories ([The Writer’s Voice](https://www.newyorker.com/podcast/the-writers-voice)). **No New Yorker primary page** states which nonfiction articles use automated vs human narration. Secondary journalism (Columbia Journalism Review, 2026) quotes deputy editorial director Monica Racic: The New Yorker “does not use AI to narrate its fiction” because readings are treated as performance; ~20% of subscribers listen to narrated stories. Treat vendor/partnership details from CJR as **unconfirmed** until corroborated by Condé Nast or ElevenLabs case study.

**Vanity Fair** appears in the same CJR survey as using automated TTS; **no primary Condé Nast source** naming a vendor was found.

---

### The New York Times

**Automated voice is official and disclosed.** “The majority of our articles” can be listened to “as soon as they’re published” via “an automated voice, which may result in occasional errors in pronunciation, tone, or sentiment” ([NYT Help: Articles Read by an Automated Voice](https://help.nytimes.com/hc/en-us/articles/24318293692180-Articles-Read-by-an-Automated-Voice)).

**Product launch.** The June 7, 2024 press release introduced a Listen tab and “articles read by an automated voice… read verbatim by an automated voice” across supported stories ([NYTCo press release](https://www.nytco.com/press/the-new-york-times-adds-listen-mode-and-more-personalization-to-news-app/)).

**Vendor: undisclosed.** NYT executives told Axios the narrated voice was “built in partnership with a generative artificial intelligence company” but “declined to say which firm” (Axios via [WWSG recap](https://wwsg.com/speaker-news/exclusive-nyt-to-soon-offer-most-articles-via-automated-voice/), 2024). A Times spokesperson told CJR they would not name the provider ([CJR](https://www.cjr.org/analysis/all-the-news-while-doing-the-dishes-ai-narration-artificial-mediation-relationship-writing-new-yorker-new-york-times-singer-remnick-elevenlabs-staniszewski.php), 2026)—secondary.

**Historical context.** The Times previously owned **Audm**, a human-narration platform for long-form journalism (not automated TTS).

---

### The Washington Post

**Current vendor (likely): ElevenLabs.** ElevenLabs’ publishing page displays The Washington Post logo ([elevenlabs.io/publishing](https://elevenlabs.io/publishing)) and lists the Post under publishing customers ([Series C blog](https://elevenlabs.io/blog/series-c), Jan 30, 2025). Digiday (May 20, 2024) quotes audio director Renita Jablonski: newsletter and article audio use “the same technology… thanks to a partnership with AI voice generating software company Eleven Labs,” with cross-team quality checks—**secondary until WaPo confirms**.

**Historical vendor: Amazon Polly.** In 2021 the Post integrated Polly so that when the text CMS publishes an article it “simultaneously sends the text to the audio CMS, where the article text is processed by Amazon Polly to produce an audio recording… delivered as an mp3” ([AWS ML blog](https://aws.amazon.com/blogs/machine-learning/the-washington-post-website-launches-audio-articles-voiced-by-amazon-polly/), 2021). Ryan Luu cited user satisfaction with Polly voices and workflow consistency.

**Migration note.** Polly (2021) → ElevenLabs (listed 2025, Digiday 2024) is plausible but **not officially documented** as a migration path.

---

### The Atlantic

**ElevenLabs lists The Atlantic** as a publishing customer ([Series C blog](https://elevenlabs.io/blog/series-c), Jan 30, 2025). The Atlantic published deep reporting *about* ElevenLabs ([May 2024 feature](https://www.theatlantic.com/technology/archive/2024/05/elevenlabs-ai-voice-cloning-deepfakes/678288/)) but **no Atlantic press release** naming Audio Native or a TTS vendor was found.

---

### Wall Street Journal

**Microsoft partnership (secondary).** CJR quotes a Journal spokesperson: “Read to Me” was “developed through a partnership with Microsoft that began in 2020,” used ~5 million times in the past year with 65% completion ([CJR](https://www.cjr.org/analysis/all-the-news-while-doing-the-dishes-ai-narration-artificial-mediation-relationship-writing-new-yorker-new-york-times-singer-remnick-elevenlabs-staniszewski.php)). **No WSJ or Microsoft primary announcement** specifically for WSJ Read to Me was found; treat Azure TTS as **likely but unconfirmed** for current WSJ article audio.

---

### Financial Times

**Early experiment: Amazon Polly.** FT Labs used Polly voice “Amy” to convert text articles to audio in ~1–3 seconds per piece (Digiday, Oct 2, 2017)—secondary. FT help pages describe listening via speaker icon in the Digital Edition app ([FAQ](https://help.ft.com/faq/digital-edition-app/How-do-I-listen-to-an-article-in-the-FT-Digital-Edition-app/)) but **do not state current TTS vendor or AI vs human**.

**AI policy.** FT commits to “human-led journalism” and will not allow AI to “compromise the integrity of our journalism” ([FT AI standards](https://aboutus.ft.com/company/our-standards/ai)). Podcast pages carry a note: “The FT does not use generative AI to voice its podcasts” (e.g. [FT News Briefing episode page](https://www.ft.com/content/595bf639-17be-43bb-acc2-780f619fedee)). **Current article-listen vendor: unconfirmed.**

---

### TIME (comparable publisher with confirmed pipeline)

**Confirmed ElevenLabs Audio Native partnership.** TIME integrated “automated voiceovers on TIME.com” via Audio Native; CTO Burhan Hamid connected with ElevenLabs in March 2023 ([TIME + ElevenLabs](https://elevenlabs.io/blog/time), Jun 27, 2024). Audio Native embeds a player that “creates automated voiceovers for news articles and blogs” and regenerates when text changes ([ElevenLabs publishing overview](https://elevenlabs.io/blog/the-state-of-ai-audio-in-publishing-and-news), updated Aug 26, 2026).

---

### Other vendors and publisher relationships (confirmed where linked)

| Vendor / product | Confirmed publisher use | Primary source |
|---|---|---|
| **ElevenLabs Audio Native** | TIME (detailed); WaPo, New Yorker, Atlantic (customer list) | [TIME blog](https://elevenlabs.io/blog/time); [Series C](https://elevenlabs.io/blog/series-c); [Audio Native docs](https://elevenlabs.io/docs/eleven-creative/audio-tools/audio-native) |
| **Amazon Polly** | Washington Post (2021); FT experiment (2017, secondary) | [AWS WaPo blog](https://aws.amazon.com/blogs/machine-learning/the-washington-post-website-launches-audio-articles-voiced-by-amazon-polly/) |
| **Microsoft Azure TTS** | USA TODAY / Gannett “Hear This Story” | [Microsoft customer story](https://www.microsoft.com/en/customers/story/1533257729461246933-usa-today-media-entertainment-azure), Aug 4, 2022 |
| **BeyondWords** | Ringier / Blick.ch (voice clone of editor Steffi Buchli) | [BeyondWords–Ringier blog](https://beyondwords.io/blog/beyondwords-partners-with-ringier-media-switzerland/), Oct 22, 2024 |
| **Speechify** | Medium Listen button for members | [Speechify–Medium](https://speechify.com/medium/) |
| **Speechify enterprise API** | Unnamed “enterprise publishers and online newspapers” | [Speechify publishers blog](https://speechify.com/blog/accessible-publishing-speechify-what-to-consider-for-publishers/) |

**No primary publisher relationship found** for: Speechmatics, Audioburst, Wondercraft, or Descript in **article narration** (Wondercraft and Speechki market audiobook/ad/education workflows on their own sites).

---

### How professional pipelines preprocess journalism

**BeyondWords (vendor documentation—representative of publisher-grade preprocessing):**

- Automatically converts HTML or plain text to **SSML** before synthesis ([Why TTS sounds better on BeyondWords](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/)).
- NLP resolves homographs (e.g. *read* past vs present), dates, ordinals vs cardinals, and domain-specific abbreviations.
- Strips non-spoken HTML (e.g. image captions); can fetch and clean embedded tweets from blockquotes.
- **Pronunciation rules**: substitution, acronym spelling, IPA—scoped to org, project, or article ([pronunciation rules blog](https://beyondwords.io/blog/enhancing-ai-generated-audio-articles-with-pronunciation-rules-2/)).
- **AI preprocessing** (public beta, Aug 2025): context-aware expansion of “YoY”, “3Q”, “422M”, currency symbols, foreign names with language detection ([AI preprocessing launch](https://beyondwords.io/blog/cleaner-audio-at-scale-introducing-ai-preprocessing-2/)).

**Amazon Polly (used by WaPo 2021, FT 2017):**

- **Newscaster** speaking style via `<amazon:domain name="news">` on neural voices Matthew, Joanna, Lupe, Amy ([Polly newscaster docs](https://docs.aws.amazon.com/polly/latest/dg/newscaster-voices.html)).
- SSML: `<phoneme>`, `<w role="…">` for homographs, `<sub alias="…">` for acronyms, `<break>`, `<say-as>` ([Polly SSML docs](https://docs.aws.amazon.com/polly/latest/dg/phoneme-tag.html)).
- **Custom lexicons** (PLS format) for W3C-style pronunciation overrides at synthesis time ([Managing lexicons](https://docs.aws.amazon.com/polly/latest/dg/managing-lexicons.html)).

**ElevenLabs Audio Native / API:**

- Accepts structured **HTML** uploads with guidance: `'<html><body><div><p>Your content</p>…</div></body></html>'` ([Audio Native create API](https://elevenlabs.io/docs/api-reference/audio-native/create)).
- **`apply_text_normalization`**: `auto`, `on`, `apply_english`—controls number/date expansion ([Audio Native API](https://elevenlabs.io/docs/api-reference/audio-native/create); [models doc](https://elevenlabs.io/docs/overview/models)).
- **Long-form**: split on sentence boundaries; **request stitching** via `previous_request_ids` to preserve prosody across chunks ([request stitching guide](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching)).
- Per-model character limits (e.g. Multilingual v2: 10,000 chars ≈ 10 min; Flash v2.5: 40,000 chars ≈ 40 min) ([models doc](https://elevenlabs.io/docs/overview/models)).

**Washington Post architecture (2021, Polly era):** dual CMS—text publish triggers parallel audio CMS → Polly → MP3 publish ([AWS blog](https://aws.amazon.com/blogs/machine-learning/the-washington-post-website-launches-audio-articles-voiced-by-amazon-polly/)). USA TODAY: article text at publish → Azure TTS → file to CDN; workflow via Teams/Power Automate ([Microsoft story](https://www.microsoft.com/en/customers/story/1533257729461246933-usa-today-media-entertainment-azure)).

**Quality control patterns:**

- **Economist:** human broadcasters for weekly edition; AI breaking-news audio explicitly **not** pre-reviewed ([TTS policy](https://myaccount.economist.com/s/article/What-is-our-text-to-speech-policy)).
- **Economist briefings:** human editor review for curated scripts only ([briefings page](https://myaccount.economist.com/s/article/How-we-make-AI-Audio-briefings)).
- **Washington Post (2024, secondary):** Jablonski meets “media engineering and product colleagues” to quality-check AI audio ([Digiday](https://digiday.com/media/the-washington-post-adds-ai-generated-audio-to-three-newsletters/)).
- **Speechki (audiobooks, not news):** “human being listens to every audiobook proof” after AI narration ([Speechki–BookBaby PR](https://www.prweb.com/releases/bookbaby-and-speechki-aim-to-disrupt-audiobook-market-for-self-published-authors-862545327.html), Nov 15, 2022)—illustrates human-in-the-loop QC pattern.

**Not found in primary sources for major newsrooms:** EBU R128 loudness mastering, background music beds on article narration, or systematic multi-voice casting for inline quotes in daily articles.

---

### Why naive Gemini / ElevenLabs Reader usage fails

**Gemini TTS limits ([Gemini API speech generation](https://ai.google.dev/gemini-api/docs/speech-generation); [Cloud Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)):**

- Input token limit **8,192**; output **16,384** tokens per request ([Gemini 2.5 Flash TTS model card](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-preview-tts)).
- Cloud API: text field ≤ **4,000 bytes**, prompt ≤ **4,000 bytes**, combined ≤ **8,000 bytes**; output truncated at ~**655 seconds** ([Gemini-TTS limits table](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)).
- “Speech quality and consistency may begin to drift with generated outputs that are longer than a few minutes. We recommend splitting your transcripts into smaller chunks.”
- TTS accepts **text-only** input—no HTML/SSML markup channel like Polly/BeyondWords.
- Occasional **500 errors** when model returns text tokens instead of audio; Google recommends retry logic.
- Streaming truncation bugs reported on long SSE streams ([python-genai issue #922](https://github.com/googleapis/python-genai/issues/922))—community report, not official spec.

**ElevenLabs API / Reader ([help center](https://help.elevenlabs.io/hc/en-us/articles/14312847889297-What-characters-are-accepted-when-generating-audio); [troubleshooting docs](https://elevenlabs.io/docs/eleven-creative/troubleshooting)):**

- Characters like `{`, `}`, `<`, `>`, `[`, `]` “will usually result in low quality speech” — typical in HTML/Markdown/JSON pasted from pages.
- Numbers, dates, symbols, acronyms often mispronounced unless written out or **`apply_text_normalization`** enabled ([help article](https://help.elevenlabs.io/hc/en-us/articles/14888917355409-Why-are-numbers-dates-symbols-and-acronyms-not-properly-pronounced-or-spoken-in-the-correct-language)).
- **Volume drops / whispering / distortion** on long generations: “stability issue or a voice issue”; ElevenLabs recommends **Studio** for anything “longer than a few hundred characters” and breaking text into segments **under 800 characters** to reduce degradation ([help](https://help.elevenlabs.io/hc/en-us/articles/13416095176977-Why-does-my-voice-start-whispering-change-accent-change-tone-or-break); [troubleshooting](https://elevenlabs.io/docs/eleven-creative/troubleshooting)).
- **Flash v2.5** disables normalization by default for latency; Multilingual v2 handles numbers better ([models doc](https://elevenlabs.io/docs/overview/models)).

**ElevenReader vs publisher Audio Native:**

- ElevenReader converts URLs, PDFs, pasted text, or full-page HTML—including paywalled pages when logged in via Chrome extension ([ElevenReader help](https://help.elevenlabs.io/hc/en-us/articles/26197672002833-What-is-ElevenReader); [Chrome extension help](https://help.elevenlabs.io/hc/en-us/articles/41076873230097-How-does-the-ElevenReader-Chrome-extension-work)).
- It optimizes for **personal consumption**, not publisher CMS cleanliness: no org-wide pronunciation rules, no editorial SSML layer, no guaranteed stripping of nav/ads/related links unless the page DOM happens to be clean.
- Audio Native is configured once per site with allowlisted domains, chosen voice/model, and optional HTML upload with normalization flags ([Audio Native docs](https://elevenlabs.io/docs/eleven-creative/audio-tools/audio-native)).

**Common failure mode:** sending **page chrome** (bylines duplicated in header/footer, “Subscribe”, photo captions, stock tickers, URLs, social embeds, pull-quote attributions, table markup) causes models to speak punctuation, URLs, or nonsense tokens—exactly the content publisher pipelines strip or never send.

---

## How publications likely differ from “paste into Gemini/ElevenLabs”

1. **Clean text extraction at publish time** from the article body field—not “View Source” or Reader URL import ([WaPo dual-CMS architecture](https://aws.amazon.com/blogs/machine-learning/the-washington-post-website-launches-audio-articles-voiced-by-amazon-polly/); [BeyondWords HTML handling](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/)).
2. **Normalization layer** for numbers, currencies, abbreviations, sports scores, and foreign names ([BeyondWords AI preprocessing](https://beyondwords.io/blog/cleaner-audio-at-scale-introducing-ai-preprocessing-2/); [ElevenLabs normalization](https://help.elevenlabs.io/hc/en-us/articles/14888917355409-Why-are-numbers-dates-symbols-and-acronyms-not-properly-pronounced-or-spoken-in-the-correct-language)).
3. **SSML or equivalent** for breaks, emphasis, and pronunciation ([BeyondWords](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/); [Polly lexicons](https://docs.aws.amazon.com/polly/latest/dg/managing-lexicons.html)).
4. **Chunking + stitching** for long features instead of one-shot generation ([ElevenLabs stitching](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching); [Gemini “split into smaller chunks”](https://ai.google.dev/gemini-api/docs/speech-generation)).
5. **Consistent brand voice** chosen once (Audio Native settings, Polly newscaster voice, etc.).
6. **Regeneration on edit** when copy changes ([Audio Native](https://elevenlabs.io/docs/eleven-creative/audio-tools/audio-native)).
7. **Human narration or hybrid strategy**—Economist weekly human audio; NYT still plans 15–20% “reporter reads” for personal stories (Axios/WWSG, secondary); New Yorker fiction via author reads ([Writer’s Voice](https://www.newyorker.com/podcast/the-writers-voice)).
8. **Selective coverage**—WaPo excludes recipes; Economist limits AI to gap-filling before Thursday human drop ([Economist TTS policy](https://myaccount.economist.com/s/article/What-is-our-text-to-speech-policy)).
9. **Optional human QC loops** (WaPo teams per Digiday; Economist editors on curated briefings only).

---

## Open questions / unconfirmed items

| Item | Status |
|---|---|
| Economist third-party TTS vendor for article narration | **Unconfirmed** |
| NYT automated-voice vendor (ElevenLabs rumored in trade press) | **Unconfirmed**—NYT declines to name partner |
| New Yorker / Atlantic **formal** ElevenLabs partnership terms | **Partial**—customer list only; no case study like TIME |
| WSJ current TTS stack (Microsoft Azure assumed from 2020) | **Unconfirmed** at primary level |
| FT current article-listen vendor and AI vs human mix | **Unconfirmed** |
| WaPo official confirmation of ElevenLabs migration from Polly | **Unconfirmed** |
| Condé Nast-wide audio policy (Vanity Fair, etc.) | **Unconfirmed** |
| Loudness mastering (EBU R128), music beds, multi-voice quotes in news article TTS | **No primary evidence** for major publishers |
| Whether Economist AI breaking-news TTS uses same vendor as AI Audio Briefings speech model | **Unconfirmed** |

---

## Source list

### Publishers
- The Economist — [TTS policy](https://myaccount.economist.com/s/article/What-is-our-text-to-speech-policy) (Jun 5, 2026); [AI briefings](https://myaccount.economist.com/s/article/How-we-make-AI-Audio-briefings); [AI usage](https://myaccount.economist.com/s/article/How-we-handle-AI-generated-content) (Jul 9, 2026); [Audio edition](https://myaccount.economist.com/s/article/Audio-edition); [Queue help](https://myaccount.economist.com/s/article/How-do-I-build-a-queue-in-the-app) (Jul 22, 2026); [Annual Report 2026 PDF](https://assets.ctfassets.net/2h5kbjx7tvqe/5Sj00z0ZbrZ7bqdg4ShJRN/13ecb0226dc4c4c4a0f666af3298b215/TEG_Annual_Report_2026.pdf)
- The New Yorker — [Audio in app](https://www.newyorker.com/news/news-desk/a-new-home-for-audio-in-the-new-yorker-app); [The Writer’s Voice](https://www.newyorker.com/podcast/the-writers-voice)
- NYT — [Help: automated voice](https://help.nytimes.com/hc/en-us/articles/24318293692180-Articles-Read-by-an-Automated-Voice); [Press: Listen mode](https://www.nytco.com/press/the-new-york-times-adds-listen-mode-and-more-personalization-to-news-app/) (Jun 7, 2024)
- FT — [AI standards](https://aboutus.ft.com/company/our-standards/ai); [Digital Edition listen FAQ](https://help.ft.com/faq/digital-edition-app/How-do-I-listen-to-an-article-in-the-FT-Digital-Edition-app/)

### Vendors
- ElevenLabs — [Series C / customer list](https://elevenlabs.io/blog/series-c) (Jan 30, 2025); [TIME partnership](https://elevenlabs.io/blog/time) (Jun 27, 2024); [Publishing overview](https://elevenlabs.io/blog/the-state-of-ai-audio-in-publishing-and-news) (updated Aug 26, 2026); [Audio Native docs](https://elevenlabs.io/docs/eleven-creative/audio-tools/audio-native); [API create](https://elevenlabs.io/docs/api-reference/audio-native/create); [Models / limits](https://elevenlabs.io/docs/overview/models); [Request stitching](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching); [Troubleshooting](https://elevenlabs.io/docs/eleven-creative/troubleshooting); [Publishing page](https://elevenlabs.io/publishing)
- ElevenLabs Help — [Accepted characters](https://help.elevenlabs.io/hc/en-us/articles/14312847889297-What-characters-are-accepted-when-generating-audio); [Numbers/dates](https://help.elevenlabs.io/hc/en-us/articles/14888917355409-Why-are-numbers-dates-symbols-and-acronyms-not-properly-pronounced-or-spoken-in-the-correct-language); [Volume/whispering](https://help.elevenlabs.io/hc/en-us/articles/13416095176977-Why-does-my-voice-start-whispering-change-accent-change-tone-or-break); [ElevenReader](https://help.elevenlabs.io/hc/en-us/articles/26197672002833-What-is-ElevenReader); [Chrome extension](https://help.elevenlabs.io/hc/en-us/articles/41076873230097-How-does-the-ElevenReader-Chrome-extension-work)
- BeyondWords — [SSML/NLP](https://beyondwords.io/blog/why-text-to-speech-voices-sound-better-on-beyondwords/); [Pronunciation rules](https://beyondwords.io/blog/enhancing-ai-generated-audio-articles-with-pronunciation-rules-2/); [AI preprocessing](https://beyondwords.io/blog/cleaner-audio-at-scale-introducing-ai-preprocessing-2/); [Ringier partnership](https://beyondwords.io/blog/beyondwords-partners-with-ringier-media-switzerland/) (Oct 22, 2024)
- Amazon / AWS — [WaPo + Polly](https://aws.amazon.com/blogs/machine-learning/the-washington-post-website-launches-audio-articles-voiced-by-amazon-polly/); [Polly newscaster](https://docs.aws.amazon.com/polly/latest/dg/newscaster-voices.html); [Lexicons](https://docs.aws.amazon.com/polly/latest/dg/managing-lexicons.html); [phoneme SSML](https://docs.aws.amazon.com/polly/latest/dg/phoneme-tag.html)
- Microsoft — [USA TODAY + Azure TTS](https://www.microsoft.com/en/customers/story/1533257729461246933-usa-today-media-entertainment-azure) (Aug 4, 2022)
- Speechify — [Medium partnership](https://speechify.com/medium/); [Publishers / enterprise API](https://speechify.com/blog/accessible-publishing-speechify-what-to-consider-for-publishers/)
- Google — [Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation); [Gemini 2.5 Flash TTS model](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-preview-tts); [Cloud Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)

### Secondary (cited only where primary is missing; not used for vendor confirmation)
- Columbia Journalism Review — [AI narration survey](https://www.cjr.org/analysis/all-the-news-while-doing-the-dishes-ai-narration-artificial-mediation-relationship-writing-new-yorker-new-york-times-singer-remnick-elevenlabs-staniszewski.php) (2026)
- Digiday — [WaPo newsletter audio / ElevenLabs](https://digiday.com/media/the-washington-post-adds-ai-generated-audio-to-three-newsletters/) (May 20, 2024); [FT Polly experiment](https://digiday.com/media/financial-times-converting-text-articles-audio/) (Oct 2, 2017)
- Axios recap — [NYT vendor undisclosed](https://wwsg.com/speaker-news/exclusive-nyt-to-soon-offer-most-articles-via-automated-voice/) (2024)

---

*Research compiled from primary sources, September 2026. Secondary sources flagged where publisher or vendor confirmation is absent.*
