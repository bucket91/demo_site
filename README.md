# Site Tools

A desktop app that creates, manages, and publishes static sites to GitHub Pages with a built-in WYSIWYG editor, theme customization, and Supabase-powered comments.

## Quick Start

1. Download the `SiteTools` executable from [GitHub Actions](https://github.com/bucket91/demo_site/actions) (select the latest run → download the artifact for your OS).
2. Place it in any empty directory and run it.
3. The **first-run wizard** will ask for your GitHub repo URL + token and optional Supabase credentials.
4. Open the **Settings** tab → click **Initialize** → **Generate** to build and publish.
5. Open the **Design** tab → set your site title, owner info, theme, and font.
6. Open the **Content** tab → click **New Page** to create pages with the WYSIWYG editor (paste from Word, Google Docs, etc.).
7. Use **Help** tab for detailed per-tab documentation.

Your site is live at `https://your-username.github.io/your-repo/`.

## Tabs

- **Design** — Site title, preview buttons, owner fields (name, title, bio, contacts, avatar), UI font size, theme selector & color swatches, font picker & custom font import
- **Content** — Create and edit pages with the built-in WYSIWYG editor (supports Paste from Word), manage page tree (categories, drag reorder, rename, delete, toggle comments), discover unregistered HTML files
- **Settings** — GitHub remote URL + token, Supabase URL + anon key, initialize git, generate & push
- **Comments** — View, edit, search, and delete Supabase-powered comments (requires one-time SQL setup)
- **Help** — Detailed documentation for each tab, Supabase SQL setup instructions, contact support

## Features

- **WYSIWYG Editor** — CKEditor 5 with Paste from Word support. Create and edit pages directly in the app.
- **GitHub Pages Publishing** — Bundled git binary, no system git required. Initialize, generate, and push with one click.
- **Theme System** — Preset color themes or fully customizable colors and fonts. Import custom `.ttf`/`.woff`/`.otf` font files.
- **Supabase Comments** — Optional comment system on every page. One-time SQL setup, manage comments from the app.
- **Self-Contained** — Single executable with everything bundled (Python, PyQt5, PyQtWebEngine, git, CKEditor).

## Building from Source

```bash
python3 build.py
```

Requires Python 3.10+. The script creates a venv, installs dependencies, and produces a standalone executable.
