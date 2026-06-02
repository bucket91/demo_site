# Site Tools

A desktop app that creates, manages, and publishes static sites to GitHub Pages — no coding required. Comes with a built-in WYSIWYG editor (CKEditor 5), theme customization, hover animations, and optional Supabase-powered comments.

## Download & Run

1. Go to **Actions** → select the latest green run → scroll down to **Artifacts**.
2. Download `SiteTools-Windows` or `SiteTools-Linux`.
3. Extract the zip. Place `SiteTools.exe` (or `SiteTools`) in an **empty folder** and run it.
4. On first launch, a wizard asks for your GitHub repo URL + token (and optional Supabase credentials). Fill it in or skip — you can configure everything later.
5. The app auto-creates a `site/` folder and a default page. You're ready to go.

> **Important**: Keep the exe in its own folder. It creates a `site/` subdirectory with all your files.

## Tabs at a Glance

| Tab | What it does |
|-----|-------------|
| **Design** | Site title, owner info (name, bio, avatar, contacts), UI font size, theme (preset or custom colors), font picker & custom font import, language (33 languages) + LTR/RTL direction |
| **Content** | Page tree with drag reorder, rename, delete, toggle comments. Import from Google Docs (.zip), MS Word (.mht), or scan for unregistered HTML files. Generate the static site |
| **CKEditor** | Full WYSIWYG rich text editor. Paste from Word/Google Docs, import .zip/.mht/.html, edit freely, save back to your site |
| **Preview** | Live preview with Desktop/Tablet/Mobile presets, zoom controls (30%–300%), and refresh to rebuild |
| **Advanced** | Hover animations (cards, buttons, links, images), page-load entrance effects, shadows, rounded corners, video/image backgrounds |
| **Publishing** | Git remote URL + token, Supabase URL + publishable key, force push toggle, Publish button, Visit Page link, side-by-side status and output logs |
| **Comments** | View, edit, and delete Supabase-powered comments. Refresh, edit selected, delete selected. One-time SQL setup required (see Comments help page) |
| **Help** | Detailed documentation for every tab, including Supabase SQL setup instructions |

## First-Time Setup

1. **Design tab** → Set your site title, owner name, and pick a theme.
2. **Content tab** → Click **New Page** to create pages, or import from Word/Google Docs.
3. **Publishing tab** → Enter your GitHub repo URL and token, then click **Publish**.

Your site is live at `https://your-username.github.io/your-repo/`.

## Features

- **WYSIWYG Editor** — CKEditor 5 with Paste from Word/Google Docs. Import .zip (Google Docs), .mht (MS Word), or .html files. Font stacks for CJK, Arabic, Devanagari, Bengali, Hebrew, Thai, Tamil, Urdu.
- **GitHub Pages Publishing** — Bundled git binary (no system git needed). One-click publish with automatic git init, commit, and push. Force push option for overwriting remote.
- **Theme System** — Preset color themes or fully custom colors. Import custom .ttf/.woff/.woff2/.otf font files. Bengali fonts bundled.
- **Hover Effects & Animations** — Page-load entrance animations, card/button/link/image hover effects, shadows, rounded corners, video/image backgrounds.
- **Supabase Comments** — Optional comment system. One-time SQL setup. Manage comments from the app.
- **Self-Contained** — Single executable bundles Python, PyQt6, QtWebEngine, git, CKEditor 5, and Bengali fonts.

## Building from Source

```bash
python3 build.py
```

Requires Python 3.10+. The script creates a venv, installs dependencies (PyInstaller, PyQt6, PyQt6-WebEngine), downloads git + FFmpeg + CKEditor + fonts, and produces a standalone executable.
