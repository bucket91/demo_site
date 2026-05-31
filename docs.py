#!/usr/bin/env python3
from PyQt6 import QtWidgets, QtCore

STYLE = """
QWidget { background: transparent; }
QLabel { color: #c9d1d9; }
QLabel.dim { color: #6e7681; }
QLabel.heading { font-weight: bold; color: #c9d1d9; font-size: 16px; padding: 4px 0; }
QGroupBox {
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    margin-top: 12px; padding: 16px 14px 14px;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 2px 8px; color: #58a6ff; font-weight: bold;
}
QTextEdit.sql {
    background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
    border-radius: 6px; padding: 10px; font-family: monospace; font-size: 12px;
}
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: #161b22; width: 8px; }
QScrollBar::handle:vertical { background: #484f58; border-radius: 4px; }
"""


def _section(title, *lines):
    g = QtWidgets.QGroupBox(title)
    l = QtWidgets.QVBoxLayout(g)
    l.setSpacing(4)
    for text in lines:
        if text == "---":  # thin spacer
            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            sep.setStyleSheet("background: #30363d; max-height: 1px; margin: 4px 0;")
            l.addWidget(sep)
        elif text.startswith("$ "):  # sub-heading
            lbl = QtWidgets.QLabel(text[2:])
            lbl.setStyleSheet("font-weight: bold; color: #c9d1d9; margin-top: 4px;")
            l.addWidget(lbl)
        else:
            lbl = QtWidgets.QLabel(text)
            lbl.setWordWrap(True)
            lbl.setProperty("class", "dim")
            l.addWidget(lbl)
    l.addStretch()
    return g


def _build_page(title, sections):
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
    w = QtWidgets.QWidget()
    l = QtWidgets.QVBoxLayout(w)
    l.setContentsMargins(20, 16, 20, 16)
    l.setSpacing(4)
    heading = QtWidgets.QLabel(title)
    heading.setProperty("class", "heading")
    l.addWidget(heading)
    for s in sections:
        l.addWidget(s)
    # Contact footer
    sep = QtWidgets.QFrame()
    sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
    sep.setStyleSheet("background: #30363d; max-height: 1px; margin: 8px 0;")
    l.addWidget(sep)
    contact = QtWidgets.QLabel(
        'Need help?  contact via '
        '<a href="https://discord.com/users/mhd235" style="color:#58a6ff;">Discord</a> or '
        '<a href="mailto:mhd235@proton.me" style="color:#58a6ff;">Email</a>'
    )
    contact.setTextFormat(QtCore.Qt.TextFormat.RichText)
    contact.setOpenExternalLinks(True)
    contact.setStyleSheet("color: #6e7681; font-size: 12px;")
    contact.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    l.addWidget(contact)
    l.addStretch()
    scroll.setWidget(w)
    return scroll


def _design_page():
    return _build_page("Design", [
        _section("Site Title",
                 "Type your site name in the Title field. It appears in browser tabs and search results.",
                 "---",
                 "$ Preview Buttons",
                 "Preview Local — opens your generated site in your default browser from your local files.",
                 "Preview Online — opens the published site on GitHub Pages (requires a configured remote URL)."),
        _section("Owner",
                 "Set your name, title, a short bio, and contact links shown in the site sidebar.",
                 "$ Contacts format — one per line:",
                 '  Label | URL    e.g.  GitHub | https://github.com/username',
                 "$ Avatar",
                 "Upload a PNG, JPG, or GIF image. It is automatically cropped to a circle."),
        _section("UI Font Size",
                 "Adjust the application's interface text size (range 10–24). Changes apply immediately."),
        _section("Theme",
                 "Pick a preset color theme from the dropdown. The swatches below show the key colors for the selected theme.",
                 "---",
                 "$ Custom Colors",
                 'Select "Custom..." from the theme dropdown, then click "Customize Colors" to edit every color individually.'),
        _section("Font",
                 "Choose a built-in font from the dropdown, or import your own.",
                 "---",
                 "$ Import Custom Font",
                 "Supported formats: .ttf, .woff, .woff2, .otf. Select the file, give it a family name, and click Import. The font appears in the font dropdown and is embedded via @font-face.",
                 "---",
                 '$ Click "Apply Theme" to write the CSS and regenerate the site.'),
    ])


def _content_page():
    return _build_page("Content", [
        _section("Import",
                 "Supported file formats:",
                 "$ Google Docs export — Select a .zip file containing index.html and an images/ folder.",
                 "$ MHT / MHTML — Single-file web archive (saved from a browser).",
                 "---",
                 "After selecting a file, you can preview the cleaned result before saving. Choose a category (folder) and a page title. The page is written to category/title-slug.html and registered in the sidebar automatically."),
        _section("Page Management",
                 "Pages appear in a tree view organized by category.",
                 "$ Reorder — Drag and drop pages within or between categories.",
                 "$ Rename — Double-click a page name or right-click → Rename.",
                 "$ Delete — Right-click a page or category → Delete.",
                 "$ Comments — Right-click a page to toggle the comment form on/off for that page.",
                 "---",
                 '$ "+ Add" — Browse for an existing .html file, assign a category, and add it to the sidebar.',
                 '$ "Scan" — Discovers unregistered .html files in the site folder and lets you add them with one click.',
                 '$ "Delete Selected" — Removes the selected page or category.'),
        _section("Generate",
                 'Click "Generate" in the page manager (or "Save" in the Import section) to rebuild the static site with your changes.'),
    ])


def _settings_page():
    return _build_page("Settings", [
        _section("GitHub / Git",
                 "Connect your site to a GitHub repository for publishing.",
                 "$ Remote URL — e.g. https://github.com/username/repo.git",
                 "$ GitHub Token — A classic personal access token with repo scope. Create one at github.com/settings/tokens.",
                 "---",
                 '$ "Initialize" — Sets up the local git repository and connects it to the remote.',
                 '$ "Generate" — Builds the static site and pushes it to GitHub Pages.'),
        _section("Supabase (Comments)",
                 "To enable comments on your site, enter your Supabase project URL and anon public key.",
                 "---",
                 "See the Comments help tab for the one-time database setup (SQL table creation).",
                 "Comments are automatically enabled when both fields are filled."),
        _section("Status",
                 "The status panel shows: git availability, remote connectivity, and the last generation output. Use it to verify everything is working before publishing."),
    ])


def _comments_page():
    sql = QtWidgets.QTextEdit()
    sql.setReadOnly(True)
    sql.setProperty("class", "sql")
    sql.setMaximumHeight(260)
    sql.setPlainText("""CREATE TABLE comments (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  page TEXT NOT NULL,
  name TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_insert" ON comments FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select" ON comments FOR SELECT TO anon USING (true);""")

    g = QtWidgets.QGroupBox("One-Time Database Setup")
    gl = QtWidgets.QVBoxLayout(g)
    gl.setSpacing(6)
    lbl = QtWidgets.QLabel(
        "Go to supabase.com → open your project → SQL Editor → paste and run:")
    lbl.setWordWrap(True)
    lbl.setProperty("class", "dim")
    gl.addWidget(lbl)
    gl.addWidget(sql)
    hint = QtWidgets.QLabel("Copy the SQL above and run it in the Supabase SQL Editor.")
    hint.setStyleSheet("color: #8b949e; font-size: 12px;")
    gl.addWidget(hint)

    return _build_page("Comments", [
        _section("Overview",
                 "Every page on your site includes a comment form powered by Supabase. "
                 "Visitors can post comments without signing in.",
                 "Comments are stored in a Supabase database table."),
        g,
        _section("Connect",
                 "After running the SQL, go to the Settings tab and paste your Supabase project URL and anon public key.",
                 "Comments appear automatically on all pages (except those with comments toggled off in the Content tab)."),
        _section("Manage Comments",
                 'Use the Comments tab in the main window to view, edit, search, and delete comments.',
                 "The table shows the commenter name, page path, body text, and creation date."),
    ])


class DocsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top = QtWidgets.QWidget()
        top.setStyleSheet("background: #161b22; border-bottom: 1px solid #30363d;")
        tl = QtWidgets.QHBoxLayout(top)
        tl.setContentsMargins(16, 8, 16, 8)
        self.help_heading = QtWidgets.QLabel("Help")
        self.help_heading.setStyleSheet("font-weight: bold; color: #c9d1d9; font-size: 15px;")
        tl.addWidget(self.help_heading)
        tl.addSpacing(16)
        self.combo = QtWidgets.QComboBox()
        self.combo.setView(QtWidgets.QListView())
        self.combo.addItems(["Design", "Advanced", "Content", "Settings", "Comments"])
        self.combo.setMinimumWidth(180)
        tl.addWidget(self.combo)
        tl.addStretch()
        layout.addWidget(top)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(_design_page())
        self.stack.addWidget(_content_page())
        self.stack.addWidget(_settings_page())
        self.stack.addWidget(_comments_page())
        layout.addWidget(self.stack, 1)

        self.combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.setStyleSheet(STYLE)
