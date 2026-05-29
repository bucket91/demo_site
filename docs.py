#!/usr/bin/env python3
from PyQt5 import QtWidgets

DOCS_HTML = """\
<style>
  body { background: #0d1117; color: #c9d1d9; font-family: system-ui, sans-serif; padding: 8px 20px; }
  h1 { color: #c9d1d9; font-size: 22px; margin: 20px 0 6px; }
  h2 { color: #c9d1d9; font-size: 17px; margin: 24px 0 4px; border-bottom: 1px solid #30363d; padding-bottom: 4px; }
  p, li { line-height: 1.6; margin: 3px 0; color: #c9d1d9; }
  code { background: #161b22; color: #58a6ff; padding: 1px 6px; border-radius: 3px; font-size: 12px; }
  pre { background: #161b22; color: #c9d1d9; padding: 10px 14px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin: 6px 0; border: 1px solid #30363d; }
  .step { background: #161b22; border-left: 3px solid #58a6ff; padding: 10px 14px; margin: 10px 0; border-radius: 0 6px 6px 0; }
  .step b { color: #58a6ff; }
  hr { border: none; border-top: 1px solid #30363d; margin: 16px 0; }
</style>

<h1>How to Use This App</h1>

<p>Import Google Docs / Word files in the <b>Content</b> tab, organize pages, and publish to GitHub Pages via the <b>Settings</b> tab.</p>

<hr>

<h2>Quick Start</h2>
<div class="step"><b>1.</b> <b>Settings</b> tab → enter GitHub repo URL + token → <b>Initialize</b> → <b>Generate</b></div>
<div class="step"><b>2.</b> <b>Design</b> tab → set your name and site title → <b>Save</b></div>
<div class="step"><b>3.</b> <b>Content</b> tab → pick a <code>.zip</code> or <code>.mht</code> file → <b>Save</b></div>

<hr>

<h2>Supabase (Comments)</h2>
<p>Your site has a comment form on every page using <b>Supabase</b>.</p>
<div class="step"><b>Set up the database (one-time):</b> Go to <a href="https://supabase.com">supabase.com</a> → create a project → open <b>SQL Editor</b> and run:
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
<div class="step"><b>Connect:</b> Paste <b>Project URL</b> + <b>anon key</b> into <b>Settings</b> → check <b>Enable comments</b> → <b>Generate</b></div>
<div class="step"><b>Manage:</b> use the <b>Comments</b> tab to view, edit, or delete comments</div>
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
                background: #0d1117; color: #c9d1d9;
                border: none;
            }
        """)
        browser.setHtml(DOCS_HTML)
        layout.addWidget(browser)
