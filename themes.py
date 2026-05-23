from string import Template

CSS_TEMPLATE = Template("""\
:root {
  --body-bg: $body_bg;
  --text: $text;
  --hero-bg: $hero_bg;
  --card-bg: $card_bg;
  --card-border: $card_border;
  --input-bg: $input_bg;
  --input-border: $input_border;
  --label: $label;
  --muted: $muted;
  --accent: $accent;
  --accent-hover: $accent_hover;
  --accent-text: $accent_text;
}
body.dark-mode {
  --body-bg: $dark_body_bg;
  --text: $dark_text;
  --hero-bg: $dark_hero_bg;
  --card-bg: $dark_card_bg;
  --card-border: $dark_card_border;
  --input-bg: $dark_input_bg;
  --input-border: $dark_input_border;
  --label: $dark_label;
  --muted: $dark_muted;
  --accent: $dark_accent;
  --accent-hover: $dark_accent_hover;
  --accent-text: $dark_accent_text;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: $font_family;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--body-bg);
  color: var(--text);
  transition: background 0.3s, color 0.3s;
}

header {
  background: $header_bg;
  color: $header_text;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}
header h1 {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
}
nav a {
  color: $header_text;
  text-decoration: none;
  margin-left: 1rem;
}

.theme-toggle {
  background: none;
  border: 1px solid $theme_border;
  color: $header_text;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  line-height: 1;
}

.layout {
  display: flex;
  flex: 1;
}
main {
  padding: 0 1.25rem;
  width: 100%;
}

.sidebar {
  width: 250px;
  background: $sidebar_bg;
  color: $sidebar_text;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  z-index: 1000;
  overflow-y: auto;
}

.sidebar-owner {
  padding: 1.25rem 1rem;
  text-align: center;
  border-bottom: 1px solid $sidebar_border;
}
.owner-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 0.6rem;
  border: 2px solid $avatar_border;
}
.owner-name {
  font-size: 1rem;
  font-weight: 700;
  color: $sidebar_text;
  margin-bottom: 0.25rem;
}
.owner-bio {
  font-size: 0.8rem;
  color: $link_muted;
}
.sidebar.open { transform: translateX(0); }

.sidebar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid $sidebar_border;
}
.sidebar-top h2 { font-size: 1.2rem; }

.category { border-bottom: 1px solid $sidebar_border; }
.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: $sidebar_text;
  font-weight: 600;
  transition: background 0.2s;
  user-select: none;
}
.category-header:hover { background: $sidebar_hover; }
.category-header .arrow {
  transition: transform 0.2s;
  font-size: 0.8rem;
}
.category-header .arrow.open { transform: rotate(90deg); }
.sub-links {
  list-style: none;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.sub-links.open { max-height: 300px; }
.sub-links li a {
  display: block;
  color: $link_muted;
  text-decoration: none;
  padding: 0.6rem 1rem 0.6rem 2rem;
  transition: background 0.2s;
}
.sub-links li a:hover { background: $sidebar_hover; color: $link_hover_text; }

.sidebar-toggle, .close-btn {
  background: none;
  border: none;
  color: $sidebar_text;
  font-size: 1.5rem;
  cursor: pointer;
}

.hero {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: var(--hero-bg);
  transition: background 0.3s;
}

.home-owner {
  text-align: center;
  padding: 2rem 1rem 0.5rem;
}
.home-owner-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid $avatar_border;
  margin-bottom: 0.5rem;
}
.home-owner-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
}
.home-owner-bio {
  font-size: 0.9rem;
  color: var(--muted);
  margin-top: 0.2rem;
}

.home-hero {
  text-align: center;
  padding: 1rem 1rem 1.5rem;
}
.home-hero h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}
.home-tagline {
  color: var(--muted);
  font-size: 1rem;
}

.home-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  max-width: 800px;
  margin: 1.5rem auto;
  padding: 0 1rem;
}
.home-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 1.25rem;
  transition: background 0.3s, border-color 0.3s;
}
.home-card h2 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--accent);
  color: var(--label);
}
.home-card ul { list-style: none; }
.home-card li { margin-bottom: 0.4rem; }
.home-card a {
  color: var(--accent);
  text-decoration: none;
  font-size: 0.9rem;
}
.home-card a:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.home-demo {
  text-align: center;
  padding: 1rem 1rem 2rem;
  color: var(--muted);
  font-size: 0.9rem;
}
.home-demo a { color: var(--accent); }

footer {
  background: $footer_bg;
  color: $footer_text;
  text-align: center;
  padding: 1rem;
}

#comments-section {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}
#comments-section h3 {
  margin-bottom: 1rem;
  color: var(--label);
  border-bottom: 2px solid var(--label);
  padding-bottom: 0.5rem;
  transition: color 0.3s, border-color 0.3s;
}
.comment {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: background 0.3s, border-color 0.3s;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.comment-date { color: var(--muted); font-size: 0.85rem; }
.no-comments { color: var(--muted); font-style: italic; }
#comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
#comment-form input,
#comment-form textarea {
  padding: 0.75rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.95rem;
  background: var(--input-bg);
  color: var(--text);
  transition: background 0.3s, color 0.3s, border-color 0.3s;
}
#comment-form textarea { min-height: 100px; resize: vertical; }
#comment-form button {
  background: var(--accent);
  color: var(--accent-text);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  align-self: flex-start;
  transition: background 0.2s;
}
#comment-form button:hover { background: var(--accent-hover); }
#comment-form button:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-aspect-ratio: 1/1) {
  .layout { flex-direction: column; }
  #comments-section {
    width: 100%;
    margin-left: auto;
    margin-right: auto;
  }
}
""")

THEMES = {
    "Dark": {
        "body_bg": "#f0f0f5", "text": "#222", "hero_bg": "#f0f0f5",
        "card_bg": "#fff", "card_border": "#e0e0e0",
        "input_bg": "#fff", "input_border": "#ccc",
        "label": "#222", "muted": "#999",
        "accent": "#333", "accent_hover": "#555", "accent_text": "#eee",
        "dark_body_bg": "#121212", "dark_text": "#e0e0e0", "dark_hero_bg": "#121212",
        "dark_card_bg": "#1e1e1e", "dark_card_border": "#333",
        "dark_input_bg": "#2a2a2a", "dark_input_border": "#444",
        "dark_label": "#e0e0e0", "dark_muted": "#888",
        "dark_accent": "#333", "dark_accent_hover": "#444", "dark_accent_text": "#e0e0e0",
        "header_bg": "#1e1e1e", "header_text": "#eee",
        "sidebar_bg": "#2a2a2a", "sidebar_text": "#eee",
        "sidebar_border": "#333", "sidebar_hover": "#333",
        "link_muted": "#999", "link_hover_text": "#eee",
        "avatar_border": "#555",
        "footer_bg": "#1e1e1e", "footer_text": "#eee",
        "theme_border": "#eee",
    },
    "Light": {
        "body_bg": "#ffffff", "text": "#1a1a1a", "hero_bg": "#f8f9fa",
        "card_bg": "#ffffff", "card_border": "#dee2e6",
        "input_bg": "#ffffff", "input_border": "#ced4da",
        "label": "#1a1a1a", "muted": "#6c757d",
        "accent": "#007bff", "accent_hover": "#0056b3", "accent_text": "#ffffff",
        "dark_body_bg": "#f8f9fa", "dark_text": "#1a1a1a", "dark_hero_bg": "#ffffff",
        "dark_card_bg": "#ffffff", "dark_card_border": "#dee2e6",
        "dark_input_bg": "#ffffff", "dark_input_border": "#ced4da",
        "dark_label": "#1a1a1a", "dark_muted": "#6c757d",
        "dark_accent": "#007bff", "dark_accent_hover": "#0056b3", "dark_accent_text": "#ffffff",
        "header_bg": "#f8f9fa", "header_text": "#1a1a1a",
        "sidebar_bg": "#f8f9fa", "sidebar_text": "#1a1a1a",
        "sidebar_border": "#dee2e6", "sidebar_hover": "#e9ecef",
        "link_muted": "#6c757d", "link_hover_text": "#1a1a1a",
        "avatar_border": "#dee2e6",
        "footer_bg": "#f8f9fa", "footer_text": "#1a1a1a",
        "theme_border": "#ced4da",
    },
    "Ocean": {
        "body_bg": "#e8f4fd", "text": "#0a2a44", "hero_bg": "#d6edfc",
        "card_bg": "#ffffff", "card_border": "#b8d4e8",
        "input_bg": "#ffffff", "input_border": "#8ab8d4",
        "label": "#0a2a44", "muted": "#5a7a8a",
        "accent": "#1a6ea0", "accent_hover": "#145882", "accent_text": "#ffffff",
        "dark_body_bg": "#0a1a2e", "dark_text": "#d6edfc", "dark_hero_bg": "#0e2238",
        "dark_card_bg": "#122a40", "dark_card_border": "#1a3a52",
        "dark_input_bg": "#0e2238", "dark_input_border": "#1a3a52",
        "dark_label": "#d6edfc", "dark_muted": "#6a8a9a",
        "dark_accent": "#3a9ad8", "dark_accent_hover": "#58b0e8", "dark_accent_text": "#0a1a2e",
        "header_bg": "#0e3050", "header_text": "#e8f4fd",
        "sidebar_bg": "#0e3050", "sidebar_text": "#e8f4fd",
        "sidebar_border": "#1a4a6a", "sidebar_hover": "#1a4a6a",
        "link_muted": "#8ab8d4", "link_hover_text": "#ffffff",
        "avatar_border": "#3a7a9a",
        "footer_bg": "#0e3050", "footer_text": "#e8f4fd",
        "theme_border": "#3a7a9a",
    },
    "Forest": {
        "body_bg": "#edf7ee", "text": "#1a3a1a", "hero_bg": "#dcefd8",
        "card_bg": "#ffffff", "card_border": "#b8d4b0",
        "input_bg": "#ffffff", "input_border": "#8ab880",
        "label": "#1a3a1a", "muted": "#5a7a52",
        "accent": "#2a7a2a", "accent_hover": "#1e5e1e", "accent_text": "#ffffff",
        "dark_body_bg": "#0e1e0e", "dark_text": "#dcefd8", "dark_hero_bg": "#122612",
        "dark_card_bg": "#1a3018", "dark_card_border": "#2a4a22",
        "dark_input_bg": "#122612", "dark_input_border": "#2a4a22",
        "dark_label": "#dcefd8", "dark_muted": "#6a8a62",
        "dark_accent": "#4aba4a", "dark_accent_hover": "#6ad46a", "dark_accent_text": "#0e1e0e",
        "header_bg": "#1a3a1a", "header_text": "#edf7ee",
        "sidebar_bg": "#1a3a1a", "sidebar_text": "#edf7ee",
        "sidebar_border": "#2a5a2a", "sidebar_hover": "#2a5a2a",
        "link_muted": "#8ab880", "link_hover_text": "#ffffff",
        "avatar_border": "#4a8a3a",
        "footer_bg": "#1a3a1a", "footer_text": "#edf7ee",
        "theme_border": "#4a8a3a",
    },
    "Sunset": {
        "body_bg": "#fef0e8", "text": "#4a2a1a", "hero_bg": "#fde4d0",
        "card_bg": "#ffffff", "card_border": "#e8c8b0",
        "input_bg": "#ffffff", "input_border": "#d4a888",
        "label": "#4a2a1a", "muted": "#8a6a52",
        "accent": "#c05a3a", "accent_hover": "#a04a2e", "accent_text": "#ffffff",
        "dark_body_bg": "#2a1a0e", "dark_text": "#fde4d0", "dark_hero_bg": "#342216",
        "dark_card_bg": "#3e2a1a", "dark_card_border": "#5a3a22",
        "dark_input_bg": "#342216", "dark_input_border": "#5a3a22",
        "dark_label": "#fde4d0", "dark_muted": "#8a6a52",
        "dark_accent": "#e07a5a", "dark_accent_hover": "#f08a6a", "dark_accent_text": "#2a1a0e",
        "header_bg": "#5a2a1a", "header_text": "#fef0e8",
        "sidebar_bg": "#5a2a1a", "sidebar_text": "#fef0e8",
        "sidebar_border": "#7a4a2a", "sidebar_hover": "#7a4a2a",
        "link_muted": "#d4a888", "link_hover_text": "#ffffff",
        "avatar_border": "#a06a3a",
        "footer_bg": "#5a2a1a", "footer_text": "#fef0e8",
        "theme_border": "#a06a3a",
    },
    "Nord": {
        "body_bg": "#eceff4", "text": "#2e3440", "hero_bg": "#e5e9f0",
        "card_bg": "#ffffff", "card_border": "#d8dee9",
        "input_bg": "#ffffff", "input_border": "#c8cede",
        "label": "#2e3440", "muted": "#7a8294",
        "accent": "#5e81ac", "accent_hover": "#4a6a92", "accent_text": "#ffffff",
        "dark_body_bg": "#2e3440", "dark_text": "#d8dee9", "dark_hero_bg": "#3b4252",
        "dark_card_bg": "#434c5e", "dark_card_border": "#4c566a",
        "dark_input_bg": "#3b4252", "dark_input_border": "#4c566a",
        "dark_label": "#d8dee9", "dark_muted": "#7a8294",
        "dark_accent": "#88c0d0", "dark_accent_hover": "#a8d8e8", "dark_accent_text": "#2e3440",
        "header_bg": "#3b4252", "header_text": "#eceff4",
        "sidebar_bg": "#3b4252", "sidebar_text": "#eceff4",
        "sidebar_border": "#4c566a", "sidebar_hover": "#4c566a",
        "link_muted": "#a4aeba", "link_hover_text": "#ffffff",
        "avatar_border": "#6a728a",
        "footer_bg": "#3b4252", "footer_text": "#eceff4",
        "theme_border": "#6a728a",
    },
    "Dracula": {
        "body_bg": "#f8f0fc", "text": "#282a36", "hero_bg": "#f0e6f6",
        "card_bg": "#ffffff", "card_border": "#d8c8e8",
        "input_bg": "#ffffff", "input_border": "#c8a8d8",
        "label": "#282a36", "muted": "#7a6a8a",
        "accent": "#8a5ab5", "accent_hover": "#6a3a95", "accent_text": "#ffffff",
        "dark_body_bg": "#1e1e2e", "dark_text": "#e0d6f0", "dark_hero_bg": "#282a36",
        "dark_card_bg": "#32304a", "dark_card_border": "#44405a",
        "dark_input_bg": "#282a36", "dark_input_border": "#44405a",
        "dark_label": "#e0d6f0", "dark_muted": "#7a6a8a",
        "dark_accent": "#bd93f9", "dark_accent_hover": "#d4b0ff", "dark_accent_text": "#282a36",
        "header_bg": "#32304a", "header_text": "#f8f0fc",
        "sidebar_bg": "#32304a", "sidebar_text": "#f8f0fc",
        "sidebar_border": "#4a4a62", "sidebar_hover": "#4a4a62",
        "link_muted": "#b8a8d0", "link_hover_text": "#ffffff",
        "avatar_border": "#7a6a9a",
        "footer_bg": "#32304a", "footer_text": "#f8f0fc",
        "theme_border": "#7a6a9a",
    },
    "Monokai": {
        "body_bg": "#f5f5e8", "text": "#272822", "hero_bg": "#efefe0",
        "card_bg": "#ffffff", "card_border": "#d8d8c8",
        "input_bg": "#ffffff", "input_border": "#c8c8b8",
        "label": "#272822", "muted": "#7a7a6a",
        "accent": "#a6a61a", "accent_hover": "#88880e", "accent_text": "#272822",
        "dark_body_bg": "#1e1f1c", "dark_text": "#f8f8f2", "dark_hero_bg": "#272822",
        "dark_card_bg": "#3e3f3a", "dark_card_border": "#4e4f48",
        "dark_input_bg": "#272822", "dark_input_border": "#4e4f48",
        "dark_label": "#f8f8f2", "dark_muted": "#7a7a6a",
        "dark_accent": "#a6e22e", "dark_accent_hover": "#c0f050", "dark_accent_text": "#272822",
        "header_bg": "#272822", "header_text": "#f8f8f2",
        "sidebar_bg": "#3e3f3a", "sidebar_text": "#f8f8f2",
        "sidebar_border": "#4e4f48", "sidebar_hover": "#4e4f48",
        "link_muted": "#a8a892", "link_hover_text": "#ffffff",
        "avatar_border": "#6a6a5a",
        "footer_bg": "#272822", "footer_text": "#f8f8f2",
        "theme_border": "#6a6a5a",
    },
    "GitHub": {
        "body_bg": "#ffffff", "text": "#24292e", "hero_bg": "#f6f8fa",
        "card_bg": "#ffffff", "card_border": "#e1e4e8",
        "input_bg": "#ffffff", "input_border": "#d1d5da",
        "label": "#24292e", "muted": "#586069",
        "accent": "#0366d6", "accent_hover": "#0256b9", "accent_text": "#ffffff",
        "dark_body_bg": "#0d1117", "dark_text": "#c9d1d9", "dark_hero_bg": "#161b22",
        "dark_card_bg": "#21262d", "dark_card_border": "#30363d",
        "dark_input_bg": "#161b22", "dark_input_border": "#30363d",
        "dark_label": "#c9d1d9", "dark_muted": "#8b949e",
        "dark_accent": "#58a6ff", "dark_accent_hover": "#79c0ff", "dark_accent_text": "#0d1117",
        "header_bg": "#24292e", "header_text": "#ffffff",
        "sidebar_bg": "#24292e", "sidebar_text": "#ffffff",
        "sidebar_border": "#404448", "sidebar_hover": "#404448",
        "link_muted": "#959da5", "link_hover_text": "#ffffff",
        "avatar_border": "#586069",
        "footer_bg": "#24292e", "footer_text": "#ffffff",
        "theme_border": "#586069",
    },
    "Midnight": {
        "body_bg": "#e8ecf0", "text": "#0d1117", "hero_bg": "#dce0e8",
        "card_bg": "#ffffff", "card_border": "#c8ced8",
        "input_bg": "#ffffff", "input_border": "#b0b8c8",
        "label": "#0d1117", "muted": "#6e7681",
        "accent": "#1f6feb", "accent_hover": "#1858c8", "accent_text": "#ffffff",
        "dark_body_bg": "#0d1117", "dark_text": "#c9d1d9", "dark_hero_bg": "#161b22",
        "dark_card_bg": "#161b22", "dark_card_border": "#30363d",
        "dark_input_bg": "#0d1117", "dark_input_border": "#30363d",
        "dark_label": "#c9d1d9", "dark_muted": "#6e7681",
        "dark_accent": "#58a6ff", "dark_accent_hover": "#79c0ff", "dark_accent_text": "#0d1117",
        "header_bg": "#0d1117", "header_text": "#c9d1d9",
        "sidebar_bg": "#161b22", "sidebar_text": "#c9d1d9",
        "sidebar_border": "#30363d", "sidebar_hover": "#21262d",
        "link_muted": "#6e7681", "link_hover_text": "#c9d1d9",
        "avatar_border": "#30363d",
        "footer_bg": "#0d1117", "footer_text": "#c9d1d9",
        "theme_border": "#30363d",
    },
}

FONTS = {
    "System UI": "system-ui, -apple-system, sans-serif",
    "Classic Serif": "Georgia, 'Times New Roman', serif",
    "Classic Sans": "Arial, Helvetica, sans-serif",
    "Monospace": "'Courier New', Courier, monospace",
    "Humanist": "'Segoe UI', Roboto, 'Helvetica Neue', sans-serif",
    "Slate Serif": "Garamond, 'Times New Roman', serif",
    "Verdana": "Verdana, Geneva, sans-serif",
    "Trebuchet": "'Trebuchet MS', 'Lucida Grande', sans-serif",
    "Palatino": "Palatino, 'Palatino Linotype', serif",
    "Tahoma": "Tahoma, Geneva, Verdana, sans-serif",
}
