---
title: AI and Developer Productivity
date: 2026-03-21
draft: true
---

## Introduction
In a recent blog post by Answer.ai titled [So where are all the AI apps?](https://www.answer.ai/posts/2026-03-12-so-where-are-all-the-ai-apps.html), the authors looked for evidence of enhanced productivity since the launch of ChatGPT in November, 2022 in the count of package releases and updates on PyPi. Their key takeaways were as follows:
1. The growth of new packages does not show an inflection on or after ChatGPT's release. In other words, the rate of increase of new packages available on PyPi is following the pattern it already exhibited pre-ChatGPT.
2. Looking at the 15,000 most downloaded packages in December, 2025, the number of yearly updates continue the downward trend from the first year onwards. Packages published prior to 2019 averaged 6 updates in their first year which increased to 10 in 2019 (attributable to broader adoption of CI tools like GitHub Actions) and to 13 in 2023 which can be attributed to the launch of AI coding agents.
3. Digging further into the packages mentioned in the point above, packages that are AI-related made nearly 2x more updates in their first year than their non-AI peers.
4. AI-related popular packages explained the 2x updates better i.e. the popular AI packages made nearly 26 updates in their first year compared to 14 by the not-so-popular packages with the latter number closer to the non-AI packages.

Since the increase in release frequency of popular AI packages can be due to increased developer productivity or more developers working on the package, the authors conclude that no evidence is available to confirm that modern AI tools improve developer productivity. In addition, since they only look at the count of updates which is a *volume* metric, there is no information about the quality of these updates. In other words, do the frequent updates to packages represent useful features adopted by the community or are they incremental, speculative features that have reduced value?

In this blog post, I will attempt to test the following null hypothesis:

> H0: Using downstream signals of value like download growth and adoption as dependency, the 2x productivity bump for popular AI packages reverses or disappears.

## Uses