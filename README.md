# Tejas Kale's Personal Blog

A minimalist personal blog built with Hugo and the PaperMod theme, similar to Simon Willison's blog but customized for my needs.

![Blog Homepage](https://github.com/user-attachments/assets/1cbfd1fa-067d-47de-94ec-778c4431efe1)

## Features

- **Minimalist Design**: Clean, readable layout using the PaperMod theme
- **About Me Page**: Personal introduction and background
- **Category System**: Posts organized by categories (Programming, Data Science, Machine Learning, etc.)
- **Tag System**: Easy filtering and discovery of related content
- **Responsive**: Works great on desktop and mobile devices
- **RSS Feeds**: Stay updated with automatic RSS generation
- **Search Functionality**: Built-in search capabilities
- **Dark/Light Theme**: Toggle between themes

## Getting Started

### Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) v0.146.0 or later
- Git

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tejas-kale/blog.git
   cd blog
   ```

2. **Initialize the theme submodule** (if not already done):
   ```bash
   git submodule update --init --recursive
   ```

3. **Start the development server**:
   ```bash
   hugo server --buildDrafts
   ```

4. **Open your browser** and visit `http://localhost:1313/blog/`

### Creating New Content

#### Creating a New Blog Post

```bash
hugo new content posts/your-post-title.md
```

This creates a new post with the proper front matter template. Make sure to:
- Set `draft = false` when ready to publish
- Add appropriate `categories` and `tags`
- Include a descriptive `description` for SEO

#### Example Post Front Matter

```toml
+++
title = "Your Post Title"
date = 2025-09-17T10:00:00Z
draft = false
categories = ['Programming', 'Tutorial']
tags = ['python', 'tutorial', 'beginner']
author = 'Tejas Kale'
description = 'A brief description of your post for SEO and social sharing'
+++
```

### Site Configuration

The main configuration is in `hugo.toml`. Key sections:

- **Basic Settings**: Site title, author, description
- **Menu Configuration**: Navigation menu items
- **Theme Settings**: PaperMod-specific configurations
- **Social Links**: GitHub, LinkedIn, etc.
- **Taxonomies**: Categories and tags setup

### Building for Production

```bash
hugo --minify
```

This generates the static site in the `public/` directory.

## Deployment

### GitHub Pages

1. **Configure the base URL** in `hugo.toml`:
   ```toml
   baseURL = 'https://yourusername.github.io/blog/'
   ```

2. **Set up GitHub Actions** (create `.github/workflows/hugo.yml`):
   ```yaml
   name: Deploy Hugo site to Pages

   on:
     push:
       branches: ["main"]
     workflow_dispatch:

   permissions:
     contents: read
     pages: write
     id-token: write

   concurrency:
     group: "pages"
     cancel-in-progress: false

   defaults:
     run:
       shell: bash

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout
           uses: actions/checkout@v4
           with:
             submodules: recursive

         - name: Setup Hugo
           uses: peaceiris/actions-hugo@v3
           with:
             hugo-version: 'latest'
             extended: true

         - name: Build with Hugo
           run: hugo --minify

         - name: Upload artifact
           uses: actions/upload-pages-artifact@v3
           with:
             path: ./public

     deploy:
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       runs-on: ubuntu-latest
       needs: build
       steps:
         - name: Deploy to GitHub Pages
           id: deployment
           uses: actions/deploy-pages@v4
   ```

3. **Enable GitHub Pages** in your repository settings and select "GitHub Actions" as the source.

### Other Hosting Options

- **Netlify**: Connect your GitHub repo and set build command to `hugo --minify`
- **Vercel**: Similar to Netlify with automatic Hugo detection
- **Firebase Hosting**: Build locally and deploy the `public/` folder

## Customization

### Adding Social Links

Edit the `[[params.socialIcons]]` sections in `hugo.toml`:

```toml
[[params.socialIcons]]
name = "platform-name"
url = "your-profile-url"
```

### Customizing the Theme

The PaperMod theme is highly customizable. Check the [PaperMod documentation](https://github.com/adityatelange/hugo-PaperMod) for all available options.

### Adding Custom CSS/JS

Create files in:
- `assets/css/extended/` for custom CSS
- `assets/js/` for custom JavaScript

## Content Organization

### Categories vs Tags

- **Categories**: Broad topics (Programming, Data Science, Personal)
- **Tags**: Specific topics (python, machine-learning, tutorial, beginner)

### File Structure

```
content/
├── about.md           # About page
├── posts/             # Blog posts
│   ├── post-1.md
│   ├── post-2.md
│   └── ...
└── _index.md          # Homepage content (optional)
```

## Contributing

Feel free to suggest improvements or report issues. This is a personal blog, but I welcome feedback on the technical setup.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- [Hugo](https://gohugo.io/) - The world's fastest framework for building websites
- [PaperMod Theme](https://github.com/adityatelange/hugo-PaperMod) - A fast, clean, responsive Hugo theme
- Inspired by [Simon Willison's blog](https://simonwillison.net/) for the concept and approach