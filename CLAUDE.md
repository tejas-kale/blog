# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal blog built with Hugo and deployed to GitHub Pages. Theme: hugo-paper, imported as a Hugo module.

**Live site**: https://tejas-kale.github.io/blog/

## Development Commands

```bash
hugo server          # local preview
hugo server -D       # include drafts
hugo --gc --minify   # production build
hugo new posts/post-title.md
hugo mod get -u && hugo mod tidy
```

## Layout

- `content/posts/` — every article, including unpublished ones. `draft: true` in front matter is enough; do not add a `content/drafts/` section.
- `content/about.md` — About page. Home is the post list; do not add a Posts nav item.
- `notebooks/<post-file-stem>/` — source notebooks, caches, and unpublished charts for that post.
- `static/<post-file-stem>/` — files the site serves for that post (charts, audio, images). Site-wide files (`tejas_kale_cv.pdf`) stay at `static/` root.
- `assets/custom.css` — site chrome only. Hugo's `assets/` directory is the CSS pipeline, not per-post material.
- `layouts/` — `list.html`, a thin `single.html` and `head.html` (hugo-paper still references removed `.Site.Author`), and shortcodes. Do not copy the theme's comment widgets.

## Post front matter

```yaml
title: "..."
date: "YYYY-MM-DD"
draft: false
description: "One line for the homepage. Never omit this; the list does not auto-summarise."
note: true   # optional. Lab notes only. Essays omit this field.
```

Link notebooks on GitHub. Do not publish knitted HTML or review tables under `static/`.

## Agent skills

### Issue tracker

Issues for this repo live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout. See `docs/agents/domain.md`.
