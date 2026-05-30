#!/usr/bin/env python3
from PyQt5 import QtWidgets, QtCore

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
        if text == "---":
            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.HLine)
            sep.setStyleSheet("background: #30363d; max-height: 1px; margin: 4px 0;")
            l.addWidget(sep)
        elif text.startswith("$ "):
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
    scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
    w = QtWidgets.QWidget()
    l = QtWidgets.QVBoxLayout(w)
    l.setContentsMargins(20, 16, 20, 16)
    l.setSpacing(4)
    heading = QtWidgets.QLabel(title)
    heading.setProperty("class", "heading")
    l.addWidget(heading)
    for s in sections:
        l.addWidget(s)
    sep = QtWidgets.QFrame()
    sep.setFrameShape(QtWidgets.QFrame.HLine)
    sep.setStyleSheet("background: #30363d; max-height: 1px; margin: 8px 0;")
    l.addWidget(sep)
    contact = QtWidgets.QLabel(
        'Need help?  contact via '
        '<a href="https://discord.com/users/mhd235" style="color:#58a6ff;">Discord</a> or '
        '<a href="mailto:mhd235@proton.me" style="color:#58a6ff;">Email</a>'
    )
    contact.setTextFormat(QtCore.Qt.RichText)
    contact.setOpenExternalLinks(True)
    contact.setStyleSheet("color: #6e7681; font-size: 12px;")
    contact.setAlignment(QtCore.Qt.AlignCenter)
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
                 "Upload a PNG, JPG, or GIF image. It is automatically cropped to a circle.",
                 "---",
                 "The log box below Owner tracks all operations. Apply Theme output is logged here too."),
        _section("UI Font Size",
                 "Adjust the application's interface text size (range 10–24). Changes apply immediately."),
        _section("Theme",
                 "Pick a preset color theme from the dropdown. The swatches show the key colors for the selected theme.",
                 "The selected theme is persisted in config.json (selected_theme) and restored on next launch.",
                 "---",
                 "$ Custom Colors",
                 'Select "Custom..." from the theme dropdown, then click "Customize Colors" to edit every color individually.',
                 "---",
                 'Applying a theme automatically updates the Advanced tab base colors to match.'),
        _section("Font",
                 "Choose a built-in font from the dropdown, or import your own.",
                 "---",
                 "$ Import Custom Font",
                 "Supported formats: .ttf, .woff, .woff2, .otf. Select the file, give it a family name, and click Import. The font appears in the font dropdown and is embedded via @font-face.",
                 "The selected font is persisted in config.json (selected_font) and restored on next launch.",
                 "---",
                 '$ Click "Apply Theme" to write the CSS and regenerate the site.'),
    ])


def _advanced_page():
    return _build_page("Advanced", [
        _section("Backgrounds",
                 "Choose from four background types for your site:",
                 "$ Gradient — Linear, radial, or conic gradients with multiple color stops, direction/angle/position controls, and optional animation (pulse, shimmer, rotate, breathing).",
                 "$ Image — Upload a background image with controls for size, position, repeat, attachment, CSS filters, blend modes, and overlay (solid or gradient on top).",
                 "$ Video — Upload a video file (.mp4, .mov, .avi, etc.). It is automatically converted to WebM (VP9 codec, no audio) for lightweight playback. Supports opacity and overlay (solid or gradient on top of the video). The video plays muted, looped, and is preload=metadata optimized.",
                 "---",
                 "All types support opacity, pattern overlays, and fallback colors."),
        _section("Shadows",
                 "Add depth to cards, header, sidebar, images, and headings.",
                 "Presets: none, subtle, medium, deep. Customize color, light/dark opacity, hover lift amount, and transition speed."),
        _section("Corners",
                 "Control border-radius for cards, buttons, inputs, images, avatar, header, and sidebar independently."),
        _section("Borders",
                 "Toggle borders on cards and inputs. Set width, style (solid/dashed/dotted), and color mode (follow theme or custom)."),
        _section("Hover Effects",
                 "Page load animation (fade-in/slide-up/scale-in), card hover (lift/darken/border), button hover (darken/glow/scale), link hover (underline/color/glow), and image hover (zoom/darken/gray). Enable smooth scrolling and scroll-reveal animations."),
        _section("Typography",
                 "Import Google Fonts by family name, or upload custom .ttf/.woff/.woff2/.otf files. Set base font size (12–24px) and heading scale (1.0–2.0). Control line height, letter spacing, and word spacing."),
        _section("Animation (Background)",
                 "Animate gradient backgrounds with pulse, shimmer, rotate, or breathing effects. Configure speed (1–20s) and easing (ease, linear, ease-in-out, etc.). Video backgrounds also support a separate animation overlay option."),
        _section("AVIF Optimization",
                 "Enable AVIF image conversion for smaller file sizes (typically 30-50% smaller than WebP). AVIF is served via <picture> elements with WebP fallback.",
                 "---",
                 "Quality (CRF 20–50): lower = better quality, higher = smaller file. Default 30.",
                 "---",
                 "$ Note: AVIF conversion is slow (5-10 seconds per image). It runs during generation. The encoder tries libsvtav1 first (fast), then falls back to libaom-av1 (reliable)."),
    ])


def _content_page():
    return _build_page("Content", [
        _section("Import",
                 "Supported file formats:",
                 "$ Google Docs export — Select a .zip file containing index.html and an images/ folder.",
                 "$ MHT / MHTML — Single-file web archive (saved from a browser).",
                 "---",
                 "After selecting a file, you can preview the cleaned result before saving. Choose a category (folder) and a page title. The page is written to category/title-slug.html and registered in the sidebar automatically.",
                 "---",
                 "During generation, any base64-encoded images in the HTML are extracted, saved as WebP files in images/, and replaced with file references. If AVIF is enabled, a <picture> element with AVIF + WebP sources is generated instead."),
        _section("Page Management",
                 "Pages appear in a tree view organized by category.",
                 "$ Reorder — Drag and drop pages within or between categories.",
                 "$ Rename — Double-click a page name or right-click → Rename.",
                 "$ Remove vs Delete — Right-click → Remove: removes from sidebar, keeps file on disk. Delete: removes from sidebar AND deletes the file permanently.",
                 "$ Remove Category vs Delete Category — Remove: hides category from sidebar, keeps folder and files. Delete: removes from sidebar and deletes the folder and all files inside.",
                 "$ Comments — Right-click a page to toggle the comment form on/off for that page.",
                 "---",
                 '$ "+ Add" — Browse for an existing .html file, assign a category, and add it to the sidebar.',
                 '$ "Scan" — Discovers unregistered .html files in the site folder and lets you add them with one click.',
                 '$ "Delete Selected" — Removes the selected page or category.'),
        _section("Cleanup",
                 'The "Cleanup" button (bottom bar) scans for unused files:',
                 "$ Orphaned images in images/ not referenced by any page.",
                 "$ Unregistered .html files not linked in the sidebar.",
                 "$ Empty directories with no content.",
                 "A dialog shows all candidates with checkboxes. Select which to delete and click Delete Selected."),
        _section("Generation Output",
                 "When you click Generate, the following optimizations are applied:",
                 "$ Base64 data URIs → extracted and saved as WebP/WebM files in images/.",
                 "$ AVIF conversion — existing WebP files are batch-converted if AVIF is enabled in Advanced.",
                 "$ Lazy loading — content images get loading=\"lazy\" + fetchpriority=\"low\" (above-fold images keep fetchpriority=\"high\", no lazy).",
                 "$ Cache busting — style.css, advanced.css, and site.js get ?v=<8-char-hash> query strings.",
                 "$ Advanced CSS — loaded with media=\"print\" onload=\"this.media='all'\" (non-blocking) with a <noscript> fallback.",
                 "$ Preconnect — <link rel=\"preconnect\"> to Supabase URL if configured.",
                 "$ Color-scheme meta — <meta name=\"color-scheme\" content=\"light dark\"> prevents form-control flash.",
                 "$ HTML minification — leading whitespace stripped, blank lines collapsed."),
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
        _section("Executable Build",
                 'Use python build.py from the terminal to build a standalone executable with PyInstaller.',
                 "$ --strip — Strips debug symbols from all bundled binaries (smaller file size).",
                 "$ --optimize 2 — Python bytecode optimization (removes docstrings, compresses asserts).",
                 "$ --exclude-module PyQt5.QtWaylandClient — Excludes Wayland display server plugins (not needed on X11/Windows).",
                 "---",
                 "The Comments tab is loaded lazily (imported on first click) to keep startup fast."),
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
        self.stack.addWidget(_advanced_page())
        self.stack.addWidget(_content_page())
        self.stack.addWidget(_settings_page())
        self.stack.addWidget(_comments_page())
        layout.addWidget(self.stack, 1)

        self.combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.setStyleSheet(STYLE)
