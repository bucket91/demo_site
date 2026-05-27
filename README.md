# Site Tools

A desktop app that imports Google Docs exports, manages a static site with sidebar navigation, and publishes to GitHub Pages.

## Quick Start

1. Download the `SiteTools` executable (or build from source).
2. Place it in any directory (it will create a template, CSS, and config on first run).
3. Run `./SiteTools`.
4. Open the **Setup** tab — enter your site title, GitHub remote URL, and **GitHub Token** (needed for HTTPS push auth — this is a personal access token starting with `ghp_`, NOT a GPG key).
5. Get your token at [github.com/settings/tokens](https://github.com/settings/tokens) — create a classic token with `repo` scope.
6. Open the **Owner** tab — set your name, bio, and avatar.
7. Click **Generate & Push** on the Setup tab.

Your site is live at `https://your-username.github.io/your-repo/`.

## Tabs

- **Setup** — Site title, git, GitHub Token, Supabase, and "Generate & Push" (starts here)
- **Owner** — Your name, bio, avatar, and contact links
- **Import** — Import Google Docs exports (.zip) as site pages
- **Management** — Add/edit HTML files and sidebar entries
- **Theme** — Pick colors and fonts
- **Comments** — Moderate reader comments (requires Supabase)
- **Help & Guide** — Full documentation

## Building from Source

```bash
python3 build.py
```

Requires Python 3.10+ and creates a standalone executable bundled with PyQt5, a static git binary, plus other necessary packages.
