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

<p>This app turns Google Docs exports into a styled website and publishes it on GitHub Pages. Just import, organize, and generate.</p>

<hr>

<h2>Quick Start</h2>
<div class="step"><b>1.</b> Go to <b>Setup</b> tab → enter your GitHub repo URL + token → click <b>Initialize</b> then <b>Generate</b></div>
<div class="step"><b>2.</b> Go to <b>Owner</b> tab → add your name and photo → click <b>Save</b></div>
<div class="step"><b>3.</b> Go to <b>Import</b> tab → pick a <code>.zip</code> or <code>.mht</code> file → click <b>Save to Site</b></div>
<p>Your site is live at <code>https://yourusername.github.io/repo/</code></p>

<hr>

<h2>Adding Pages (Import tab)</h2>
<div class="step"><b>Google Docs:</b> <b>File → Download → Web page (.html, zipped)</b> → pick the <code>.zip</code> in the Import tab</div>
<div class="step"><b>Microsoft Word:</b> <b>File → Save As → Web Page, Single File (.mht)</b> → pick the <code>.mht</code> in the Import tab</div>
<div class="step"><b>Then:</b> Click <b>Save to Site</b> → enter a <b>Category</b> (folder) and <b>Page title</b> → done</div>
<p>The page is automatically added to your site's sidebar.</p>

<hr>

<h2>Organizing Pages (Management tab)</h2>
<p>Drag entries to reorder them. Double-click to rename. Right-click to delete.</p>
<div class="step"><b>Reorder:</b> drag the handle to move pages up/down or into a different category</div>
<div class="step"><b>Rename:</b> double-click a name and type a new one</div>
<div class="step"><b>Add existing HTML:</b> click <b>+ Add</b> → pick a file → choose category + name</div>
<div class="step"><b>New files found:</b> click <b>⟳</b> to scan — new HTML files appear in the "Discovered" section with <b>+</b> to add them</div>

<hr>

<h2>Customizing the Look (Theme tab)</h2>
<div class="step"><b>Preset:</b> pick a theme from the dropdown → click <b>Apply Theme</b></div>
<div class="step"><b>Custom colors:</b> select <b>Custom...</b> → click <b>Customize Colors...</b> → pick your colors → <b>Apply Theme</b></div>
<div class="step"><b>Custom font:</b> paste a Google Fonts URL and family name → <b>Apply Theme</b></div>

<hr>

<h2>Profile & Contacts (Owner tab)</h2>
<p>Your name, bio, photo, and social links appear as the first card on the homepage and in the sidebar.</p>
<div class="step">Add contacts like <b>WhatsApp</b>, <b>Telegram</b>, <b>YouTube</b>, <b>GitHub</b>, <b>Email</b> — the app auto-detects the link type</div>
<div class="step">Click <b>Save</b> — your site regenerates automatically</div>

<hr>

<h2>GitHub Setup (Setup tab)</h2>
<div class="step"><b>Remote URL:</b> <code>https://github.com/username/repo.git</code></div>
<div class="step"><b>Token:</b> get one at <a href="https://github.com/settings/tokens">github.com/settings/tokens</a> → <b>Generate new token (classic)</b> → check <code>repo</code> → paste it here (NOT a GPG key)</div>
<div class="step"><b>Initialize:</b> click to set up the repo and remote</div>
<div class="step"><b>Generate:</b> wraps all pages with the template, commits, and pushes live</div>

<hr>

<h2>Comments (Supabase)</h2>
<p>Your site has a comment form on every page. It uses <b>Supabase</b> as the database.</p>
<div class="step"><b>Set up the database (one-time):</b> Go to <a href="https://supabase.com">supabase.com</a> → create a project → open <b>SQL Editor</b> and run this:
<pre>CREATE TABLE comments (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  page TEXT NOT NULL,
  name TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_insert" ON comments FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select" ON comments FOR SELECT TO anon USING (true);</pre>
</div>
<div class="step"><b>Connect the app:</b> Paste your Supabase <b>Project URL</b> and <b>anon key</b> into the <b>Setup</b> tab → check <b>Enable comments</b> → <b>Generate</b></div>
<div class="step"><b>Manage comments:</b> use the <b>Comments</b> tab to view, edit, or delete comments</div>
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
                border: none;
            }
        """)
        browser.setHtml(DOCS_HTML)
        layout.addWidget(browser)
