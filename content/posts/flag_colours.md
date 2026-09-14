---
title: "How many colours are in each flag?"
date: "2026-09-13"
draft: false
description: "Most national flags use two to four colours. Gemini counted them for 56 cents."
---

A fun question popped into my head the other day: how many colours are in each flag of a country? To answer it, I thought using LLMs would be a good choice.

So, with the use of [R](https://github.com/tejas-kale/blog/blob/main/notebooks/flag_colours/flag_colours.Rmd) and the `tidyverse` libraries, I first fetched a list of countries from Wikipedia and then their flags from Wikimedia. Next, using the `ellmer` library, I asked Gemini 3.5 Flash Lite (via the OpenRouter API) to count and name the colours in each flag. I then used the Qwen3-VL-235B-A22B-Instruct and Gemini 3.6 Flash models to judge the Lite model's work. These models are larger than the Lite one so I expected them to be better judges. I checked their disagreements manually. The Qwen model is nearly a year older than the Lite model so its size advantage might be negated by its age.

The Lite model performed quite well with the agreement/disagreement [results]({{< relURL "flag_colours/results.html" >}}) as follows:

| Judge | Agree | Mostly agree | Disagree |
| --- | ---: | ---: | ---: |
| Qwen3-VL-235B-A22B-Instruct | 80.5% | 10.8% | 8.7% |
| Gemini 3.6 Flash | 88.7% | 5.6% | 5.6% |

The whole exercise cost me 56 cents.

As can be seen in the chart below, most flags have 2-4 colours. I was surprised to find no unicolour flag in this dataset. Also, when a flag contains a crest or a coat of arms, its colour count is often 6 or more. The Mexican flag contains 11 colours!

![Distribution of colours in national flags]({{< relURL "flag_colours/flag-colours.png" >}})
