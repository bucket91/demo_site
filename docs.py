#!/usr/bin/env python3
from PyQt5 import QtWidgets

DOCS_HTML = """\
<style>
  body { background: #1a1a1a; color: #e0e0e0; font-family: system-ui, sans-serif; padding: 8px 20px; }
  h1 { color: #fff; font-size: 22px; margin: 20px 0 6px; }
  h2 { color: #ddd; font-size: 17px; margin: 24px 0 4px; border-bottom: 1px solid #333; padding-bottom: 4px; }
  h3 { color: #ccc; font-size: 14px; margin: 16px 0 2px; }
  p, li { line-height: 1.6; margin: 3px 0; }
  ol, ul { margin: 4px 0 4px 20px; padding: 0; }
  code { background: #333; color: #a0d0ff; padding: 1px 6px; border-radius: 3px; font-size: 12px; }
  pre { background: #222; color: #d0d0d0; padding: 10px 14px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin: 6px 0; border: 1px solid #333; }
  b { color: #fff; }
  .step { background: #252525; border-left: 3px solid #58a6ff; padding: 10px 14px; margin: 10px 0; border-radius: 0 6px 6px 0; }
  .step b { color: #58a6ff; }
  hr { border: none; border-top: 1px solid #333; margin: 16px 0; }
</style>

<h1>How to Use This App</h1>

<p>This app manages a static website hosted on <b>GitHub Pages</b>. It wraps your HTML pages in a shared template (header, sidebar, comments, footer), handles theming, and publishes everything with one click.</p>

<hr>

<h2>The Big Picture</h2>
<ol>
  <li>Place HTML files in folders inside <code>site/</code> — each folder becomes a sidebar category, each file becomes a page</li>
  <li>Use the tabs below to configure, add content, and customize the look</li>
  <li>Click <b>Apply</b> or <b>Generate &amp; Push</b> — the app rewrites your pages with the template and pushes to GitHub</li>
  <li>GitHub Pages auto-deploys — your site goes live instantly</li>
</ol>

<hr>

<h2>Site Generator Tab</h2>
<div class="step">
  <b>Step 1:</b> Enter your Supabase Project URL and Anon Key (get these from your Supabase dashboard → Settings → API).
</div>
<div class="step">
  <b>Step 2:</b> Check "Enable comments" if you want a comment form on every page.
</div>
<div class="step">
  <b>Step 3:</b> Enter your GitHub repository URL (e.g. <code>https://github.com/you/repo.git</code>), your git name/email, and a commit message.
</div>
<div class="step">
  <b>Step 4:</b> Fill in your name, bio, and avatar URL — these appear in the sidebar and homepage.
</div>
<div class="step">
  <b>Step 5:</b> Click <b>Generate &amp; Push</b>. Watch the log — it will wrap all pages, commit, and push. Your site is now live.
</div>

<hr>

<h2>Comment Admin Tab</h2>
<p>Manage comments left on your site.</p>
<div class="step">
  <b>Step 1:</b> Click <b>Refresh</b> to load comments from Supabase.
</div>
<div class="step">
  <b>Step 2:</b> Select a row and click <b>Edit Selected</b> to change the name, page, or body text.
</div>
<div class="step">
  <b>Step 3:</b> Select a row and click <b>Delete Selected</b> to remove it (confirmation required).
</div>


<hr>

<h2>Docx to HTML Tab</h2>
<p>Convert Word documents into web pages.</p>
<div class="step">
  <b>Step 1:</b> Click <b>Browse</b> and pick a <code>.docx</code> file.
</div>
<div class="step">
  <b>Step 2:</b> Preview the HTML output.
</div>
<div class="step">
  <b>Step 3:</b> Click <b>Save as HTML</b> (standalone file) or <b>Add to Site + Generate</b> (adds to a category and rebuilds the site).
</div>
<p>When adding to site, you'll enter a category name, page title, and sidebar label.</p>

<hr>

<h2>Reference Manager Tab</h2>
<p>Add existing HTML files to your site with proper sidebar entries.</p>
<div class="step">
  <b>Step 1:</b> Browse and select an HTML file.
</div>
<div class="step">
  <b>Step 2:</b> Enter the display name (how it appears in the sidebar menu).
</div>
<div class="step">
  <b>Step 3:</b> Select or type a category (folder name). A new folder is created if it doesn't exist.
</div>
<div class="step">
  <b>Step 4:</b> Click <b>Add Entry &amp; Generate</b> — the file is copied, the sidebar reference file is updated, and the site regenerates.
</div>

<hr>

<h2>Theme Customizer Tab</h2>
<p>Change colors, fonts, and the site title.</p>

<h3>Apply a preset theme</h3>
<div class="step">
  <b>Step 1:</b> Pick a theme from the dropdown (Dark, Light, Ocean, Forest, etc.).
</div>
<div class="step">
  <b>Step 2:</b> Optionally pick a font and type a site title.
</div>
<div class="step">
  <b>Step 3:</b> Click <b>Apply Theme</b> — the CSS is rewritten and the site regenerates.
</div>

<h3>Create your own colors</h3>
<div class="step">
  <b>Step 1:</b> Select <b>Custom...</b> from the theme dropdown.
</div>
<div class="step">
  <b>Step 2:</b> Click <b>Customize Colors...</b> to open the color picker popup.
</div>
<div class="step">
  <b>Step 3:</b> Click any color swatch — the system color picker opens. Choose a color and it updates instantly.
</div>
<div class="step">
  <b>Step 4:</b> Click <b>Save Colors</b> to keep your changes, or <b>Reset to Default</b> to start over.
</div>
<div class="step">
  <b>Step 5:</b> Back in the main tab, click <b>Apply Theme</b> to write your colors to the site.
</div>

<h3>Import a custom font</h3>
<div class="step">
  <b>Step 1:</b> In the "Import Custom Font" section, click <b>Browse</b> and pick a <code>.ttf</code>, <code>.otf</code>, <code>.woff</code>, or <code>.woff2</code> file.
</div>
<div class="step">
  <b>Step 2:</b> Type a family name (e.g. "MyFont") and click <b>Import</b>.
</div>
<div class="step">
  <b>Step 3:</b> Select your imported font from the font dropdown, then click <b>Apply Theme</b>.
</div>

<hr>

<h2>Quick Start (First Time)</h2>
<ol>
  <li>Open the <b>Site Generator</b> tab — enter your Supabase URL, anon key, GitHub remote URL, and owner info</li>
  <li>Click <b>Generate &amp; Push</b> — this creates your initial site</li>
  <li>Open the <b>Theme Customizer</b> tab — pick a theme and font, click <b>Apply Theme</b></li>
  <li>Your site is live. Add pages by dropping HTML files into folders and running Generate again, or use the <b>Docx to HTML</b> or <b>Reference Manager</b> tabs</li>
</ol>

<hr>

<hr>

<h2>Git Setup Tab</h2>
<p>Initialize git, configure your remote, and push your site to GitHub.</p>
<div class="step">
  <b>Step 1:</b> Enter your Remote URL, User name, and User email in the fields (pre-filled from <code>config.json</code>).
</div>
<div class="step">
  <b>Step 2:</b> Click <b>Init Repo</b> to create the git repository, set your identity, and add the remote.
</div>
<div class="step">
  <b>Step 3:</b> Click <b>Stage &amp; Commit</b> to add all files and create the initial commit. Check <b>Auto-push</b> to push immediately.
</div>
<div class="step">
  <b>Step 4:</b> Click <b>Full Setup</b> to do all steps at once.
</div>

<hr>

<h2>Supabase Setup</h2>
<p>The comment system uses <b>Supabase</b> as its database. Follow these steps to set it up:</p>

<div class="step">
  <b>Step 1:</b> Go to <a href="https://supabase.com">supabase.com</a> and create a project.
</div>
<div class="step">
  <b>Step 2:</b> In your project dashboard, go to <b>Settings → API</b>. Copy the <b>Project URL</b> and the <b>anon public key</b>.
</div>
<div class="step">
  <b>Step 3:</b> Go to the <b>Site Generator</b> tab in this app. Paste your Project URL and anon key into the Supabase fields.
</div>
<div class="step">
  <b>Step 4:</b> Check <b>Enable comments</b> and click <b>Generate &amp; Push</b>. Every page now has a comment form.
</div>
"""


class DocsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        browser = QtWidgets.QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background: #1a1a1a; color: #e0e0e0;
                border: none; font-size: 13px;
            }
        """)
        browser.setHtml(DOCS_HTML)
        layout.addWidget(browser)
