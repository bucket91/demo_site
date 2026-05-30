import os, json

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
ADVANCED_JSON = os.path.join(SITE_DIR, "advanced_theme.json")
ADVANCED_CSS = os.path.join(SITE_DIR, "advanced.css")

DEFAULT = {
    "shadows": {
        "enabled": False,
        "preset": "medium",
        "color": "#000000",
        "opacity_light": 10,
        "opacity_dark": 45,
        "apply_cards": True,
        "apply_header": True,
        "apply_sidebar": False,
        "apply_images": True,
        "apply_headings": False,
        "hover_lift": 6,
        "transition_speed": 300
    },
    "corners": {
        "enabled": False,
        "card": 10,
        "button": 6,
        "input": 6,
        "image": 0,
        "avatar": 50,
        "header": 0,
        "sidebar": 0
    },
    "backgrounds": {
        "enabled": False,
        "type": "gradient",
        "light_colors": ["#e8ecf0", "#dce0e8"],
        "dark_colors": ["#161b22", "#0d1117"],
        "direction": "to bottom",
        "animation": "none",
        "pattern": "none",
        "pattern_opacity": 15,
        "pattern_color": "#000000",
        "bg_image": "",
        "bg_size": "cover"
    },
    "hover_effects": {
        "enabled": False,
        "page_load": "none",
        "card_hover": "lift",
        "button_hover": "darken",
        "link_hover": "underline",
        "image_hover": "zoom",
        "smooth_scroll": True,
        "scroll_reveal": False
    },
    "borders": {
        "enabled": False,
        "card_width": 1,
        "card_style": "solid",
        "card_color_mode": "theme",
        "card_custom_color": "#cccccc",
        "input_width": 1,
        "separator_style": "solid",
        "separator_width": 1
    },
    "typography": {
        "enabled": False,
        "heading_letter_spacing": 0,
        "body_letter_spacing": 0,
        "body_line_height": 1.7,
        "heading_line_height": 1.3,
        "link_style": "colored",
        "blockquote_style": "border",
        "selection_color": "#3399ff",
        "base_font_size": 16,
        "h1_size": 2.0,
        "h2_size": 1.5,
        "h3_size": 1.25
    },
    "layout": {
        "enabled": False,
        "page_max_width": 1100,
        "sidebar_width": 250,
        "content_padding": 20,
        "header_position": "static"
    },
    "custom_css": ""
}

SHADOW_PRESETS = {
    "none": "none",
    "subtle": "0 1px 3px rgba(0,0,0,OPACITY)",
    "medium": "0 4px 12px rgba(0,0,0,OPACITY)",
    "deep": "0 8px 24px rgba(0,0,0,OPACITY)"
}

PATTERN_CSS = {
    "none": "",
    "dots": "radial-gradient(var(--adv-pattern-color) 1px, transparent 1px)",
    "grid": "linear-gradient(var(--adv-pattern-color) 1px, transparent 1px), linear-gradient(90deg, var(--adv-pattern-color) 1px, transparent 1px)",
    "stripes": "repeating-linear-gradient(45deg, transparent, transparent 5px, var(--adv-pattern-color) 5px, var(--adv-pattern-color) 6px)",
    "diagonal": "repeating-linear-gradient(45deg, var(--adv-pattern-color) 0px, var(--adv-pattern-color) 1px, transparent 1px, transparent 8px)"
}

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


def load():
    if not os.path.exists(ADVANCED_JSON):
        save(DEFAULT)
        return dict(DEFAULT)
    try:
        with open(ADVANCED_JSON, encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT)
        _deep_merge(merged, data)
        return merged
    except Exception:
        return dict(DEFAULT)


def save(data):
    try:
        with open(ADVANCED_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving advanced theme: {e}")


def _deep_merge(base, override):
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def generate_css(data):
    lines = []
    lines.append("/* Advanced Theme — auto-generated. Do not edit directly. */")
    lines.append("")

    shadows = data.get("shadows", {})
    corners = data.get("corners", {})
    backgrounds = data.get("backgrounds", {})
    hover_effects = data.get("hover_effects", {})
    borders = data.get("borders", {})
    typography = data.get("typography", {})
    layout = data.get("layout", {})
    custom_css = data.get("custom_css", "")

    # Collect all variable declarations for :root and body.dark-mode
    root_vars = []
    dark_vars = []

    # --- Shadows ---
    if shadows.get("enabled"):
        preset = shadows.get("preset", "medium")
        color = shadows.get("color", "#000000")
        ol = shadows.get("opacity_light", 10) / 100.0
        od = shadows.get("opacity_dark", 45) / 100.0

        shadow_def = SHADOW_PRESETS.get(preset, "none")
        if shadow_def != "none":
            root_vars.append(f"  --adv-shadow: {shadow_def.replace('OPACITY', str(ol))};")
            dark_vars.append(f"  --adv-shadow: {shadow_def.replace('OPACITY', str(od))};")
        else:
            root_vars.append("  --adv-shadow: none;")
            dark_vars.append("  --adv-shadow: none;")

        ts = shadows.get("transition_speed", 300) / 1000.0
        root_vars.append(f"  --adv-transition: {ts}s;")

        hl = shadows.get("hover_lift", 6)
        root_vars.append(f"  --adv-hover-lift: {hl}px;")

    # --- Corners ---
    if corners.get("enabled"):
        for key in ["card", "button", "input", "image", "avatar", "header", "sidebar"]:
            val = corners.get(key, 0)
            root_vars.append(f"  --adv-radius-{key}: {val}px;")

    # --- Backgrounds ---
    if backgrounds.get("enabled"):
        bg_type = backgrounds.get("type", "solid")
        light_cols = backgrounds.get("light_colors", [])
        dark_cols = backgrounds.get("dark_colors", [])
        direction = backgrounds.get("direction", "to bottom")
        animation = backgrounds.get("animation", "none")
        pattern = backgrounds.get("pattern", "none")
        po = backgrounds.get("pattern_opacity", 15)
        pc = backgrounds.get("pattern_color", "#000000")

        root_vars.append(f"  --adv-pattern-color: {pc};")
        root_vars.append(f"  --adv-pattern-opacity: {po / 100.0};")

        if bg_type == "gradient" and len(light_cols) >= 2:
            lc = ", ".join(light_cols)
            dc = ", ".join(dark_cols) if len(dark_cols) >= 2 else lc
            root_vars.append(f"  --adv-bg: linear-gradient({direction}, {lc});")
            dark_vars.append(f"  --adv-bg: linear-gradient({direction}, {dc});")

            if animation in ("slow", "normal", "fast"):
                speed = {"slow": "8s", "normal": "4s", "fast": "2s"}[animation]
                root_vars.append(f"  --adv-bg-animation: {speed};")

        elif bg_type == "pattern":
            pat = PATTERN_CSS.get(pattern, "")
            if pat:
                lc = light_cols[0] if light_cols else "var(--body-bg)"
                dc = dark_cols[0] if dark_cols else "var(--body-bg)"
                root_vars.append(f"  --adv-bg: {lc};")
                dark_vars.append(f"  --adv-bg: {dc};")
                size = {"dots": "20px 20px", "grid": "20px 20px", "stripes": "12px 12px", "diagonal": "16px 16px"}.get(pattern, "20px 20px")
                root_vars.append(f"  --adv-bg-image: {pat};")
                root_vars.append(f"  --adv-bg-size: {size};")
        else:
            lc = light_cols[0] if light_cols else "var(--body-bg)"
            dc = dark_cols[0] if dark_cols else "var(--body-bg)"
            root_vars.append(f"  --adv-bg: {lc};")
            dark_vars.append(f"  --adv-bg: {dc};")

    # --- Borders ---
    if borders.get("enabled"):
        cw = borders.get("card_width", 1)
        cs = borders.get("card_style", "solid")
        cm = borders.get("card_color_mode", "theme")
        cc = borders.get("card_custom_color", "#cccccc")
        iw = borders.get("input_width", 1)
        ss = borders.get("separator_style", "solid")
        sw = borders.get("separator_width", 1)

        if cm == "theme":
            root_vars.append("  --adv-card-border-color: var(--card-border);")
            dark_vars.append("  --adv-card-border-color: var(--card-border);")
        else:
            root_vars.append(f"  --adv-card-border-color: {cc};")
            dark_vars.append(f"  --adv-card-border-color: {cc};")

        root_vars.append(f"  --adv-card-border: {cw}px {cs} var(--adv-card-border-color);")
        root_vars.append(f"  --adv-input-border-width: {iw}px;")
        root_vars.append(f"  --adv-separator-style: {ss};")
        root_vars.append(f"  --adv-separator-width: {sw}px;")

    # --- Typography ---
    if typography.get("enabled"):
        hls = typography.get("heading_letter_spacing", 0)
        bls = typography.get("body_letter_spacing", 0)
        blh = typography.get("body_line_height", 1.7)
        hlh = typography.get("heading_line_height", 1.3)
        sc = typography.get("selection_color", "#3399ff")
        bf = typography.get("base_font_size", 16)
        h1s = typography.get("h1_size", 2.0)
        h2s = typography.get("h2_size", 1.5)
        h3s = typography.get("h3_size", 1.25)

        root_vars.append(f"  --adv-heading-letter-spacing: {hls}px;")
        root_vars.append(f"  --adv-body-letter-spacing: {bls}px;")
        root_vars.append(f"  --adv-body-line-height: {blh};")
        root_vars.append(f"  --adv-heading-line-height: {hlh};")
        root_vars.append(f"  --adv-selection-color: {sc};")
        root_vars.append(f"  --adv-base-font-size: {bf}px;")
        root_vars.append(f"  --adv-h1-size: {h1s}em;")
        root_vars.append(f"  --adv-h2-size: {h2s}em;")
        root_vars.append(f"  --adv-h3-size: {h3s}em;")

    # --- Layout ---
    if layout.get("enabled"):
        pmw = layout.get("page_max_width", 1100)
        sbw = layout.get("sidebar_width", 250)
        cp = layout.get("content_padding", 20)
        hp = layout.get("header_position", "static")

        root_vars.append(f"  --adv-page-max-width: {pmw}px;")
        root_vars.append(f"  --adv-sidebar-width: {sbw}px;")
        root_vars.append(f"  --adv-content-padding: {cp}px;")
        root_vars.append(f"  --adv-header-position: {hp};")

    # Write :root block
    if root_vars:
        lines.append(":root {")
        lines.extend(root_vars)
        lines.append("}")
        lines.append("")

    if dark_vars:
        lines.append("body.dark-mode {")
        lines.extend(dark_vars)
        lines.append("}")
        lines.append("")

    # --- Actual CSS rules ---
    if shadows.get("enabled"):
        apply_cards = shadows.get("apply_cards", True)
        apply_header = shadows.get("apply_header", True)
        apply_sidebar = shadows.get("apply_sidebar", False)
        apply_images = shadows.get("apply_images", True)
        apply_headings = shadows.get("apply_headings", False)
        hl = shadows.get("hover_lift", 6)
        ts = shadows.get("transition_speed", 300) / 1000.0

        selectors = []
        if apply_cards:
            selectors.extend([".home-card", ".comment", ".sidebar-owner"])
        if apply_header:
            selectors.append("header")
        if apply_sidebar:
            selectors.append(".sidebar")
        if apply_images:
            selectors.append(".doc-content img:not([style*=\"float\"])")

        if selectors:
            sel = ", ".join(selectors)
            lines.append(f"{sel} {{")
            lines.append("  box-shadow: var(--adv-shadow);")
            lines.append(f"  transition: box-shadow {ts}s, transform {ts}s;")
            lines.append("}")
            lines.append("")

        if apply_headings:
            lines.append("h1, h2, h3, h4, h5, h6 {")
            lines.append("  text-shadow: var(--adv-shadow);")
            lines.append("}")

        if hl > 0 and apply_cards:
            lines.append(".home-card:hover, .comment:hover {")
            lines.append(f"  transform: translateY(-{hl}px);")
            lines.append("  box-shadow: var(--adv-shadow);")
            lines.append("}")
            lines.append("")

    if corners.get("enabled"):
        sel_map = [
            (".home-card, .comment, .sidebar-owner", "card"),
            (".theme-toggle, button:not(.sidebar-toggle):not(.close-btn)", "button"),
            ("#comment-form input, #comment-form textarea", "input"),
            (".doc-content img", "image"),
            (".owner-avatar, .owner-card-avatar", "avatar"),
            ("header", "header"),
            (".sidebar", "sidebar"),
        ]
        for sel, key in sel_map:
            lines.append(f"{sel} {{")
            lines.append(f"  border-radius: var(--adv-radius-{key});")
            lines.append("}")
            lines.append("")

    if backgrounds.get("enabled"):
        bg_type = backgrounds.get("type", "solid")
        pattern = backgrounds.get("pattern", "none")
        animation = backgrounds.get("animation", "none")

        lines.append("body {")
        if bg_type == "pattern" and pattern != "none":
            lines.append("  background-color: var(--adv-bg) !important;")
            lines.append("  background-image: var(--adv-bg-image);")
            lines.append("  background-size: var(--adv-bg-size);")
        elif bg_type == "gradient":
            lines.append("  background: var(--adv-bg) !important;")
            if animation != "none":
                lines.append("  background-size: 400% 400%;")
                lines.append("  animation: advGradient var(--adv-bg-animation) ease infinite;")
        else:
            lines.append("  background: var(--adv-bg) !important;")

        if backgrounds.get("bg_image"):
            lines.append(f"  background-image: url('{backgrounds['bg_image']}') !important;")
            lines.append(f"  background-size: {backgrounds.get('bg_size', 'cover')};")
            lines.append("  background-position: center;")
            lines.append("  background-repeat: no-repeat;")
            lines.append("  background-attachment: fixed;")

        lines.append("  transition: background 0.3s;")
        lines.append("}")
        lines.append("")

        if animation != "none":
            lines.append("@keyframes advGradient {")
            lines.append("  0% { background-position: 0% 50%; }")
            lines.append("  50% { background-position: 100% 50%; }")
            lines.append("  100% { background-position: 0% 50%; }")
            lines.append("}")
            lines.append("")

    if hover_effects.get("enabled"):
        page_load = hover_effects.get("page_load", "none")
        card_hover = hover_effects.get("card_hover", "lift")
        button_hover = hover_effects.get("button_hover", "darken")
        link_hover = hover_effects.get("link_hover", "underline")
        image_hover = hover_effects.get("image_hover", "zoom")
        scroll_reveal = hover_effects.get("scroll_reveal", False)

        if page_load != "none":
            lines.append("body {")
            if page_load == "fade":
                lines.append("  animation: advFadeIn 0.6s ease;")
            elif page_load == "slide":
                lines.append("  animation: advSlideUp 0.6s ease;")
            elif page_load == "scale":
                lines.append("  animation: advScaleIn 0.5s ease;")
            lines.append("}")
            lines.append("")

            anim_css = {
                "fade": ("@keyframes advFadeIn { from { opacity: 0; } to { opacity: 1; } }", ""),
                "slide": ("@keyframes advSlideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }", ""),
                "scale": ("@keyframes advScaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }", ""),
            }
            if page_load in anim_css:
                lines.append(anim_css[page_load][0])
                lines.append("")

        if card_hover != "none":
            effects = {
                "lift": ".home-card:hover, .comment:hover { transform: translateY(var(--adv-hover-lift, -6px)); box-shadow: var(--adv-shadow); }",
                "glow": ".home-card:hover, .comment:hover { box-shadow: 0 0 20px var(--accent); border-color: var(--accent); }",
                "border": ".home-card:hover, .comment:hover { border-color: var(--accent); }",
                "scale": ".home-card:hover, .comment:hover { transform: scale(1.02); }",
                "shadow": ".home-card:hover, .comment:hover { box-shadow: var(--adv-shadow); }",
            }
            if card_hover in effects:
                lines.append(effects[card_hover])
                lines.append("")

        if button_hover != "none":
            effects = {
                "darken": "#comment-form button:hover { filter: brightness(1.1); }",
                "lift": "#comment-form button:hover { transform: translateY(-2px); box-shadow: var(--adv-shadow); }",
                "fill": "#comment-form button:hover { transform: scale(1.03); }",
                "glow": "#comment-form button:hover { box-shadow: 0 0 12px var(--accent); }",
            }
            if button_hover in effects:
                lines.append(effects[button_hover])
                lines.append("")

        if link_hover != "none":
            effects = {
                "underline": ".sub-links li a:hover, .home-card a:hover { text-decoration: underline; }",
                "color": ".sub-links li a:hover, .home-card a:hover { color: var(--accent-hover) !important; }",
                "animated": ".sub-links li a, .home-card a { background-image: linear-gradient(var(--accent), var(--accent)); background-size: 0 2px; background-repeat: no-repeat; background-position: left bottom; transition: background-size 0.3s; } .sub-links li a:hover, .home-card a:hover { background-size: 100% 2px; color: var(--accent-hover) !important; }",
            }
            if link_hover in effects:
                lines.append(effects[link_hover])
                lines.append("")

        if image_hover != "none":
            effects = {
                "zoom": ".doc-content img:not([style*=\"float\"]) { transition: transform 0.3s; } .doc-content img:not([style*=\"float\"]):hover { transform: scale(1.03); }",
                "overlay": ".doc-content img:not([style*=\"float\"]) { position: relative; } .doc-content img:not([style*=\"float\"]):hover { filter: brightness(1.1); }",
                "grayscale": ".doc-content img:not([style*=\"float\"]) { filter: grayscale(0); transition: filter 0.3s; } .doc-content img:not([style*=\"float\"]):hover { filter: grayscale(0); }",
            }
            if image_hover in effects:
                lines.append(effects[image_hover])
                lines.append("")

        if hover_effects.get("smooth_scroll", True):
            lines.append("html { scroll-behavior: smooth; }")
            lines.append("")

        if scroll_reveal:
            lines.append(""".home-card, .comment, .doc-content img, .doc-content blockquote {
  opacity: 0;
  transform: translateY(20px);
  animation: advReveal 0.6s ease forwards;
}
.home-card:nth-child(2) { animation-delay: 0.1s; }
.home-card:nth-child(3) { animation-delay: 0.2s; }
.home-card:nth-child(4) { animation-delay: 0.3s; }
@keyframes advReveal {
  to { opacity: 1; transform: translateY(0); }
}
""")
            lines.append("")

    if borders.get("enabled"):
        cw = borders.get("card_width", 1)
        cs = borders.get("card_style", "solid")
        iw = borders.get("input_width", 1)
        ss = borders.get("separator_style", "solid")
        sw = borders.get("separator_width", 1)

        lines.append(".home-card, .comment {")
        lines.append("  border: var(--adv-card-border);")
        lines.append("}")
        lines.append("")

        lines.append("#comment-form input, #comment-form textarea {")
        lines.append(f"  border-width: {iw}px;")
        lines.append("}")
        lines.append("")

        if ss != "none":
            border_css = {"solid": "solid", "dashed": "dashed", "gradient": "solid"}.get(ss, "solid")
            lines.append(".category, .sidebar-top, .sidebar-owner {")
            lines.append(f"  border-bottom: {sw}px {border_css} var(--adv-card-border-color);")
            lines.append("}")
            lines.append("")

    if typography.get("enabled"):
        ls = typography.get("link_style", "colored")
        bq = typography.get("blockquote_style", "border")
        sc = typography.get("selection_color", "#3399ff")

        lines.append("""
body, .doc-content {
  font-size: var(--adv-base-font-size);
  letter-spacing: var(--adv-body-letter-spacing, 0);
  line-height: var(--adv-body-line-height);
}
h1, h2, h3, h4, h5, h6 {
  letter-spacing: var(--adv-heading-letter-spacing, 0);
  line-height: var(--adv-heading-line-height);
}
h1 { font-size: var(--adv-h1-size); }
h2 { font-size: var(--adv-h2-size); }
h3 { font-size: var(--adv-h3-size); }
""")
        if ls == "colored":
            lines.append(".doc-content a { color: var(--adv-link-color, var(--accent)); }")
        elif ls == "underline":
            lines.append(".doc-content a { text-decoration: underline; }")
        elif ls == "animated":
            lines.append(""".doc-content a {
  background-image: linear-gradient(var(--accent), var(--accent));
  background-size: 0 2px;
  background-repeat: no-repeat;
  background-position: left bottom;
  transition: background-size 0.3s;
  text-decoration: none;
}
.doc-content a:hover {
  background-size: 100% 2px;
}
""")

        if bq == "icon":
            lines.append(""".doc-content blockquote {
  border-left: none;
  padding-left: 3rem;
  position: relative;
}
.doc-content blockquote::before {
  content: '\\201C';
  font-size: 4rem;
  position: absolute;
  left: 0;
  top: -1rem;
  color: var(--accent);
  opacity: 0.5;
  font-family: Georgia, serif;
}
""")
        elif bq == "background":
            lines.append(""".doc-content blockquote {
  border-left: none;
  background: var(--card-bg);
  border-radius: var(--adv-radius-card, 8px);
  padding: 1rem 1.5rem;
}
""")
        elif bq == "stylized":
            lines.append(""".doc-content blockquote {
  border-left: 4px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: var(--card-bg);
  padding: 1rem 1.5rem;
  font-style: italic;
}
""")

        lines.append(f"""
::selection {{
  background: {sc};
  color: #fff;
}}
""")

    if layout.get("enabled"):
        pmw = layout.get("page_max_width", 1100)
        sbw = layout.get("sidebar_width", 250)
        cp = layout.get("content_padding", 20)
        hp = layout.get("header_position", "static")

        lines.append(f"""
main {{
  max-width: var(--adv-page-max-width);
  margin: 0 auto;
  padding-left: var(--adv-content-padding);
  padding-right: var(--adv-content-padding);
}}
.sidebar {{
  width: var(--adv-sidebar-width);
}}
""")

        if hp == "sticky":
            lines.append("""
header {
  position: sticky;
  top: 0;
  z-index: 100;
}
""")
        elif hp == "fixed":
            lines.append("""
header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
body { padding-top: 60px; }
""")

    # --- Custom CSS ---
    if custom_css and custom_css.strip():
        lines.append("")
        lines.append("/* === Custom CSS === */")
        lines.append(custom_css.strip())

    output = "\n".join(lines)
    return output


def regenerate(data=None):
    if data is None:
        data = load()
    css = generate_css(data)
    try:
        with open(ADVANCED_CSS, "w", encoding="utf-8") as f:
            f.write(css)
        return True
    except Exception as e:
        print(f"Error writing advanced.css: {e}")
        return False
