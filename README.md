# Site Tools

A desktop app that converts Word documents to HTML, manages a static site with sidebar navigation, and publishes to GitHub Pages.

## Quick Start

1. Download the `SiteTools` executable (or build from source).
2. Place it in any directory (it will create a template, CSS, and config on first run).
3. Run `./SiteTools`.
4. Open the **Setup** tab — enter your site title, git remote URL, and Supabase details (optional, for comments).
5. Open the **Owner** tab — set your name, bio, and avatar.
6. Click **Generate & Push** on the Setup tab.

Your site is live at `https://your-username.github.io/your-repo/`.

## Tabs

- **Setup** — Site title, git, Supabase, and "Generate & Push" (starts here)
- **Owner** — Your name, bio, avatar, and contact links
- **Docx to HTML** — Convert .docx files to web pages
- **Management** — Add/edit HTML files and sidebar entries
- **Theme** — Pick colors and fonts
- **Comments** — Moderate reader comments (requires Supabase)
- **Help & Guide** — Full documentation

## Building from Source

```bash
python3 build.py
```

Requires Python 3.10+ and creates a standalone executable bundled with PyQt5, mammoth, and a static git binary.
