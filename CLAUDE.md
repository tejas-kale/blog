# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal blog built with Hugo and deployed to GitHub Pages. The site uses the hugo-paper theme (v6.30) as a Git submodule for a clean, minimal design.

**Live site**: https://tejas-kale.github.io/blog/

## Development Commands

### Local Development
```bash
# Start local development server
hugo server

# Start with drafts enabled
hugo server -D

# Build the site locally
hugo --gc --minify
```

### Content Management
```bash
# Create a new blog post
hugo new posts/post-title.md

# Create a new page
hugo new about.md
```

### Theme and Submodule Management
```bash
# Update the paper theme submodule
git submodule update --remote themes/paper

# Initialize submodules (for fresh clone)
git submodule update --init --recursive
```

## Architecture

### Hugo Configuration
- **Config file**: `hugo.toml`
- **Base URL**: https://tejas-kale.github.io/blog/
- **Theme**: hugo-paper (installed as Git submodule at `themes/paper/`)
- **Main navigation**: About and Posts pages

### Theme Configuration
The hugo-paper theme is installed as a Git submodule at `themes/paper/`. The `hugo.toml` uses `theme = 'paper'` to reference the theme. Note that the submodule contains a nested theme structure, but Hugo uses the root level of the submodule.

### Content Structure
- `content/posts/` - Blog posts
- `content/about.md` - About page
- `static/` - Static assets (images, etc.)
- `layouts/` - Custom layout overrides (currently empty)

### Git Submodules
Two themes are installed as submodules:
- `themes/paper/` - hugo-paper theme (currently used)
- `themes/ananke/` - Ananke theme (fallback)

## Deployment

### GitHub Actions
Automated deployment via `.github/workflows/hugo.yaml`:
- **Trigger**: Push to main branch or manual dispatch
- **Hugo version**: 0.150.0 (extended)
- **Node.js version**: 22.18.0
- **Go version**: 1.25.1
- **Output**: `public/` directory deployed to GitHub Pages

### Build Process
The CI/CD pipeline:
1. Checks out code with recursive submodules
2. Sets up Hugo, Node.js, Go, and Dart Sass
3. Builds with `hugo --gc --minify --baseURL <pages-url>`
4. Deploys to GitHub Pages

## Local Environment Requirements

- **Hugo**: v0.150.0+ (extended version for Sass support)
- **Git**: For submodule management
- **Node.js**: Optional, for theme development

## Theme Customization

The hugo-paper theme supports extensive customization via `hugo.toml` params:
- Color schemes (linen, wheat, gray, light)
- Social media icons (GitHub, Twitter, LinkedIn, etc.)
- Profile configuration (avatar, name, bio)
- Comment systems (Disqus, Giscus, Graph Comment)
- Math typesetting (KaTeX)
- Dark mode toggle

Refer to `themes/paper/README.md` for complete configuration options.