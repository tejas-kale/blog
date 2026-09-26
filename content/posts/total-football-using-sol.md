---
title: "Making a Total Football video with GPT-6 Sol"
date: "2026-09-26"
draft: false
description: "An experiment in using GPT-6 Sol and Codex to create an animated explainer on Total Football."
---

Earlier today, my brother shared a [Reddit post](https://www.reddit.com/r/ClaudeAI/comments/1wogab3/made_entirely_with_opus_55_321_of_openrouter_api/) in which Opus 5.5 created a minute-long animated video about the meaning of life with OpenRouter models. The video is fun and well-made, if light on detail. It inspired me to create a video of my own with GPT-6 Sol (a model similar to Opus), because I have a paid ChatGPT Plus subscription rather than Claude.

Having recently finished listening to a [four-part podcast series on Total Football](https://shows.acast.com/it-was-what-it-was/episodes/total-football-where-did-the-revolution-really-begin-part-on), I chose it as the subject of my video. To help ensure accuracy, I provided the podcast transcripts as reference material to the model.

Next, I decided to run the model in Codex CLI's YOLO mode inside a GitHub Codespace, and asked Codex CLI on my laptop to set it up. It began by using the `gh` CLI to create a Codespace. When it found that it lacked permissions to manage Codespaces, it gave me the command to grant those permissions. It then gave me the command to add the OpenRouter API key as a GitHub Codespaces secret, so the Codespace could access it as an environment variable.

Using a Dockerfile and `devcontainer.json`, it configured the installation of Codex CLI, `chromium`, `ffmpeg`, `imagemagick`, `fonts-dejavu-core`, `fonts-liberation`, and OpenSSH during container provisioning. Once the Codespace was running, it installed `playwright-core`. The original Reddit prompt inspired this setup:

{{< details summary="Original Reddit prompt" >}}

> Create a pure javascript animation. 30s-60s whimsical hand drawn collage style with appropriate audio on the topic what is the purpose of life ?
>
> Entire video should be as high of a production value as possible. Please spend your time on this, it's very important.
>
> Use high quality text-to-speech model for generation. You can find open router API key in .env file
>
> You can use any tools you can find access to and resources on the internet. You create the script, the assets, the animation, concept, everything.
>
> I have to go away from my computer so please work autonomously until done. Quality is paramount. Production value should be on professional level.
>
> One more thing: max OpenRouter spend is $10

{{< /details >}}

To run the experiment in a GitHub Codespace, I gave local Codex CLI these additional requirements:

> - It should be executed in Codex configured on a GH Codespace.
> - I will provide some podcast transcripts on which the animation should be based.
>
> I want you to help me with this setup. Create the Codespace, configure Codex on it, and set up the API key.

Finally, I configured my ChatGPT account in the Codespace by transferring the local Codex authentication session file to the container with `gh codespace cp`.

Before running the Total Football prompt, I refined it with Matt Pocock's [grilling skill](https://github.com/mattpocock/skills/blob/main/docs/productivity/grilling.md). It helped me tailor the prompt to the intended audience, narrow its emphasis, and set the presentation's visual tone. Having completed the grilling session, I asked the local Codex CLI to start a session inside the Codespace with the following prompt:

> Create a 30–60 second pure JavaScript animation that answers: “What is Total Football?” Make it a whimsical, hand-drawn collage with appropriate music, sound design, and a high-quality generated voiceover. Aim for professional production value. Spend the time needed on the concept, script, assets, animation, edit, audio mix, and visual and audio review.
>
> Use the four podcast transcripts and the PDF in `resources/` as the primary factual basis. Focus on chapters 10–14 of *Inverting the Pyramid* (PDF pages 197–302), especially chapter 12, “Total Football”. Read these sources first; build the explanation around what they support, and record source references in production notes. Use internet resources for additional research and assets where useful, respecting licences and attribution. Keep the visual animation authored in JavaScript; use Chromium and FFmpeg to render and finish it.
>
> Use the `OPENROUTER_API_KEY` Codespaces secret for a high-quality text-to-speech model and any other useful generation. You may spend up to $8 through OpenRouter. Keep the key out of code, logs, and commits.
>
> Work autonomously until the deliverable is a finished film ready to publish. Watch the complete final render with sound at its intended resolution. Fix visible or audible defects in drawing, typography, motion, pacing, narration, music balance, sound effects, synchronisation, opening, and ending. Verify the final video's duration, resolution, audio, and playback, then watch it once more after the last change. Commit the code, original assets, production notes, and final video to this GitHub repository. Do not commit private credentials or source material without redistribution rights. Report the final video path, duration, source basis, and OpenRouter spend.

Codex then worked for nearly 35 minutes, using my entire ChatGPT Plus five-hour token limit and 27 cents of OpenRouter credits, to create the following video:

{{< youtube id="XClikZa2u7k" title="First GPT-6 Sol video explaining Total Football" >}}

After watching it, I gave Codex the following feedback:

> Pretty good. The pronunciation of Ajax is wrong. The video presentation looks like a Powerpoint presentation which is not too pleasing to look. The pitch representation and movements are good but not completely coherent. For example, Ajax players are shown to move but not the opposition. The background music does not suit the video. The video is not sharp enough.

It took the feedback to heart and worked for another 80 minutes. It again used my entire five-hour token limit, along with 10 cents of OpenRouter credits, to create the improved video below:

{{< youtube id="zf-FuDlj35A" title="Improved GPT-6 Sol video explaining Total Football" >}}

For a reference point, I recommend [Tifo Football's video](https://www.youtube.com/watch?v=RNMeMa2OuI0) on the subject. It is longer, covers more than the philosophy's technical aspects, and has sophisticated, clean animation which is particularly impressive given that it was made nearly a decade ago.

Although setting up the experiment took about an hour, including the time I spent waiting while Codex worked, I was amazed by the quality of the generated video. The script was coherent and captured the key technical details of Total Football correctly. In particular, the video accurately explained the exchange of positions on one side of the pitch. The animations complemented the script, and the voice-over was pleasant to listen to.

The video was not perfect, though. The script had loose ends: coaches such as Jack Reynolds and Vic Buckingham were introduced but then forgotten. It explained the concept of Total Football correctly, but skipped its significance to the game. The voice-over had awkward pauses and sentence endings, and the background music did not suit the video's theme.

Nevertheless, this experiment suggests that GPT-6 Sol, used through Codex with strong source material and human review, can substantively augment the work of both subject-matter and creative experts. A football expert can now use this technology to make explanatory videos, but will need either to consult a creative expert or develop taste through numerous trials and errors to reach true production quality.

Similarly, a creative expert can use it to iterate quickly on ideas and attempt complex concepts that were previously impractical. To be useful beyond programming enthusiasts, though, these capabilities need to be packaged in an intuitive product for people with different skills.
