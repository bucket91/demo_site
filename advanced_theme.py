import os, json

SITE_DIR = None
SETTINGS_DIR = None

def _adv_json():
    d = SETTINGS_DIR or SITE_DIR
    return os.path.join(d, "advanced_theme.json") if d else None

def _adv_css():
    return os.path.join(SITE_DIR, "advanced.css") if SITE_DIR else None

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
        "gradient_subtype": "linear",
        "direction": "to bottom",
        "gradient_angle": 180,
        "radial_shape": "ellipse",
        "radial_position": "center",
        "conic_position": "center",
        "gradient_repeat": False,
        "animation": "none",
        "animation_speed": 4,
        "animation_easing": "ease",
        "pattern": "none",
        "pattern_opacity": 15,
        "pattern_color": "#000000",
        "pattern_size": 20,
        "bg_image": "",
        "bg_size": "cover",
        "bg_position": "center",
        "bg_repeat": "no-repeat",
        "bg_attachment": "scroll",
        "image_filter": "none",
        "image_filter_value": 50,
        "image_overlay": "none",
        "image_overlay_color": "#000000",
        "image_overlay_opacity": 30,
        "blend_mode": "normal",
        "bg_opacity": 100,
        "bg_video": "",
        "video_fallback": "",
        "video_opacity": 100,
        "video_overlay": "none",
        "video_overlay_color": "#000000",
        "video_overlay_opacity": 30
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
    "dots_large": "radial-gradient(var(--adv-pattern-color) 2px, transparent 2px)",
    "grid": "linear-gradient(var(--adv-pattern-color) 1px, transparent 1px), linear-gradient(90deg, var(--adv-pattern-color) 1px, transparent 1px)",
    "stripes": "repeating-linear-gradient(45deg, transparent, transparent 5px, var(--adv-pattern-color) 5px, var(--adv-pattern-color) 6px)",
    "stripes_h": "repeating-linear-gradient(0deg, transparent, transparent 5px, var(--adv-pattern-color) 5px, var(--adv-pattern-color) 6px)",
    "stripes_v": "repeating-linear-gradient(90deg, transparent, transparent 5px, var(--adv-pattern-color) 5px, var(--adv-pattern-color) 6px)",
    "diagonal": "repeating-linear-gradient(45deg, var(--adv-pattern-color) 0px, var(--adv-pattern-color) 1px, transparent 1px, transparent 8px)",
    "crosshatch": "repeating-linear-gradient(45deg, transparent, transparent 5px, var(--adv-pattern-color) 5px, var(--adv-pattern-color) 6px), repeating-linear-gradient(-45deg, transparent, transparent 5px, var(--adv-pattern-color) 5px, var(--adv-pattern-color) 6px)",
    "zigzag": "linear-gradient(135deg, var(--adv-pattern-color) 25%, transparent 25%), linear-gradient(225deg, var(--adv-pattern-color) 25%, transparent 25%), linear-gradient(315deg, var(--adv-pattern-color) 25%, transparent 25%), linear-gradient(45deg, var(--adv-pattern-color) 25%, transparent 25%)",
    "waves": "radial-gradient(ellipse at 20% 50%, var(--adv-pattern-color) 10%, transparent 30%), radial-gradient(ellipse at 80% 50%, var(--adv-pattern-color) 10%, transparent 30%)",
    "chevron": "linear-gradient(135deg, var(--adv-pattern-color) 33.33%, transparent 33.33%), linear-gradient(225deg, var(--adv-pattern-color) 33.33%, transparent 33.33%)",
    "honeycomb": "radial-gradient(circle at 25% 25%, var(--adv-pattern-color) 1px, transparent 1px), radial-gradient(circle at 75% 75%, var(--adv-pattern-color) 1px, transparent 1px)",
    "polka": "radial-gradient(circle, var(--adv-pattern-color) 2px, transparent 2px)",
}

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


def _build_gradient_function(settings, colors_str):
    gtype = settings.get("gradient_subtype", "linear")
    direction = settings.get("direction", "to bottom")
    rshape = settings.get("radial_shape", "ellipse")
    rpos = settings.get("radial_position", "center")
    cpos = settings.get("conic_position", "center")
    repeat = settings.get("gradient_repeat", False)
    prefix = "repeating-" if repeat else ""
    if gtype == "linear":
        return f"{prefix}linear-gradient({direction}, {colors_str})"
    elif gtype == "radial":
        return f"{prefix}radial-gradient({rshape} at {rpos}, {colors_str})"
    elif gtype == "conic":
        return f"{prefix}conic-gradient(from 0deg at {cpos}, {colors_str})"
    return f"linear-gradient({direction}, {colors_str})"


def _get_animation_name(bg_type, anim_type, has_image):
    if has_image or bg_type == "image":
        m = {"ken_burns": "advKenBurns", "slow_zoom": "advSlowZoom",
             "slow_pan": "advSlowPan", "pulse": "advImgPulse",
             "hue_rotate": "advImgHue"}
        return m.get(anim_type, "")
    if bg_type == "gradient":
        m = {"flow": "advGradientFlow", "hue_rotate": "advHueRotate", "pulse": "advGradPulse"}
        return m.get(anim_type, "")
    if bg_type == "solid":
        m = {"pulse": "advSolidPulse", "breathe": "advBreathe", "shimmer": "advShimmer"}
        return m.get(anim_type, "")
    if bg_type == "pattern":
        m = {"scroll": "advPatternScroll", "pulse": "advPatternPulse", "flow": "advPatternFlow"}
        return m.get(anim_type, "")
    if bg_type == "video":
        m = {"pulse": "advVideoPulse", "hue_rotate": "advVideoHue"}
        return m.get(anim_type, "")
    return ""


def _get_animation_keyframes(bg_type, anim_type, has_image):
    if has_image or bg_type == "image":
        if anim_type == "ken_burns":
            return [
                "@keyframes advKenBurns {",
                "  0% { background-size: 100%; background-position: center; }",
                "  50% { background-size: 115%; background-position: center; }",
                "  100% { background-size: 100%; background-position: center; }",
                "}"]
        if anim_type == "slow_zoom":
            return [
                "@keyframes advSlowZoom {",
                "  0% { background-size: 100%; }",
                "  100% { background-size: 110%; }",
                "}"]
        if anim_type == "slow_pan":
            return [
                "@keyframes advSlowPan {",
                "  0% { background-position: 0% 50%; }",
                "  50% { background-position: 100% 50%; }",
                "  100% { background-position: 0% 50%; }",
                "}"]
        if anim_type == "pulse":
            return [
                "@keyframes advImgPulse {",
                "  0%, 100% { opacity: 1; }",
                "  50% { opacity: 0.85; }",
                "}"]
        if anim_type == "hue_rotate":
            return [
                "@keyframes advImgHue {",
                "  0% { filter: hue-rotate(0deg); }",
                "  100% { filter: hue-rotate(360deg); }",
                "}"]
    if bg_type == "gradient":
        if anim_type == "flow":
            return [
                "@keyframes advGradientFlow {",
                "  0% { background-position: 0% 50%; }",
                "  50% { background-position: 100% 50%; }",
                "  100% { background-position: 0% 50%; }",
                "}"]
        if anim_type == "hue_rotate":
            return [
                "@keyframes advHueRotate {",
                "  0% { filter: hue-rotate(0deg); }",
                "  100% { filter: hue-rotate(360deg); }",
                "}"]
        if anim_type == "pulse":
            return [
                "@keyframes advGradPulse {",
                "  0%, 100% { opacity: 1; }",
                "  50% { opacity: 0.85; }",
                "}"]
    if bg_type == "solid":
        if anim_type == "pulse":
            return [
                "@keyframes advSolidPulse {",
                "  0%, 100% { filter: brightness(1); }",
                "  50% { filter: brightness(1.12); }",
                "}"]
        if anim_type == "breathe":
            return [
                "@keyframes advBreathe {",
                "  0%, 100% { opacity: 1; }",
                "  50% { opacity: 0.8; }",
                "}"]
        if anim_type == "shimmer":
            return [
                "@keyframes advShimmer {",
                "  0% { background-position: -200% 0%, 0% 0%; }",
                "  100% { background-position: 200% 0%, 0% 0%; }",
                "}"]
    if bg_type == "pattern":
        if anim_type == "scroll":
            return [
                "@keyframes advPatternScroll {",
                "  0% { background-position: 0 0; }",
                "  100% { background-position: 40px 40px; }",
                "}"]
        if anim_type == "pulse":
            return [
                "@keyframes advPatternPulse {",
                "  0%, 100% { opacity: 1; }",
                "  50% { opacity: 0.65; }",
                "}"]
        if anim_type == "flow":
            return [
                "@keyframes advPatternFlow {",
                "  0% { background-position: 0% 0%; }",
                "  50% { background-position: 100% 100%; }",
                "  100% { background-position: 0% 0%; }",
                "}"]
    if bg_type == "video":
        if anim_type == "pulse":
            return [
                "@keyframes advVideoPulse {",
                "  0%, 100% { opacity: 1; }",
                "  50% { opacity: 0.7; }",
                "}"]
        if anim_type == "hue_rotate":
            return [
                "@keyframes advVideoHue {",
                "  0% { filter: hue-rotate(0deg); }",
                "  100% { filter: hue-rotate(360deg); }",
                "}"]
    return []


def convert_to_webp(input_path, output_dir):
    """Convert image to WebP using ffmpeg libwebp encoder.
    Returns (success, output_path)."""
    import subprocess, shutil, os
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False, "ffmpeg not found — install ffmpeg to convert images"
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{basename}.webp")
    cmd = [
        ffmpeg, "-y",
        "-i", input_path,
        "-c:v", "libwebp",
        "-lossless", "0",
        "-q:v", "85",
        output_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and os.path.exists(output_path):
            return True, output_path
        else:
            err = result.stderr.strip()[-200:] if result.stderr else "unknown error"
            return False, f"ffmpeg error: {err}"
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out after 2 minutes"
    except Exception as e:
        return False, str(e)


def convert_to_webm(input_path, output_dir):
    """Convert video to VP9 WebM with no audio for smaller file sizes.
    Returns (success, output_path)."""
    import subprocess, shutil, os
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False, "ffmpeg not found — install ffmpeg to convert videos"
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{basename}.webm")
    cmd = [
        ffmpeg, "-y",
        "-i", input_path,
        "-an",
        "-c:v", "libvpx-vp9",
        "-crf", "35",
        "-b:v", "0",
        output_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0 and os.path.exists(output_path):
            return True, output_path
        else:
            err = result.stderr.strip()[-200:] if result.stderr else "unknown error"
            return False, f"ffmpeg error: {err}"
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out after 5 minutes"
    except Exception as e:
        return False, str(e)


def load():
    path = _adv_json()
    if not path or not os.path.exists(path):
        save(DEFAULT)
        return dict(DEFAULT)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT)
        _deep_merge(merged, data)
        return merged
    except Exception:
        return dict(DEFAULT)


def save(data):
    path = _adv_json()
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
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
        pattern = backgrounds.get("pattern", "none")
        animation = backgrounds.get("animation", "none")
        anim_speed = backgrounds.get("animation_speed", 4)
        anim_easing = backgrounds.get("animation_easing", "ease")
        has_bg_image = bool(backgrounds.get("bg_image", ""))

        root_vars.append(f"  --adv-animation-speed: {anim_speed}s;")
        root_vars.append(f"  --adv-animation-easing: {anim_easing};")

        if bg_type == "gradient" and len(light_cols) >= 2:
            lc = ", ".join(light_cols)
            dc = ", ".join(dark_cols) if len(dark_cols) >= 2 else lc
            grad_func = _build_gradient_function(backgrounds, lc)
            grad_func_dark = _build_gradient_function(backgrounds, dc)
            root_vars.append(f"  --adv-bg: {grad_func};")
            dark_vars.append(f"  --adv-bg: {grad_func_dark};")

        elif bg_type == "pattern":
            pat = PATTERN_CSS.get(pattern, "")
            if pat:
                pc = backgrounds.get("pattern_color", "#000000")
                po = backgrounds.get("pattern_opacity", 15)
                psize = backgrounds.get("pattern_size", 20)
                lc = light_cols[0] if light_cols else "var(--body-bg)"
                dc = dark_cols[0] if dark_cols else "var(--body-bg)"
                root_vars.append(f"  --adv-pattern-color: {pc};")
                dark_vars.append("  --adv-pattern-color: var(--text);")
                root_vars.append(f"  --adv-pattern-opacity: {po / 100.0};")
                root_vars.append(f"  --adv-bg: {lc};")
                dark_vars.append(f"  --adv-bg: {dc};")
                root_vars.append(f"  --adv-bg-image: {pat};")
                root_vars.append(f"  --adv-bg-size: {psize}px {psize}px;")
        elif bg_type == "image":
            root_vars.append("  --adv-bg: transparent;")
        elif bg_type == "video":
            root_vars.append("  --adv-bg: transparent;")
            vo = backgrounds.get("video_opacity", 100)
            root_vars.append(f"  --adv-video-opacity: {max(0, min(100, vo)) / 100.0};")
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
            selectors.append(".ck-content img:not([style*=\"float\"])")

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
            (".ck-content img", "image"),
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
        has_bg_image = bool(backgrounds.get("bg_image", ""))
        blend = backgrounds.get("blend_mode", "normal")
        bg_opacity = backgrounds.get("bg_opacity", 100)
        image_filter = backgrounds.get("image_filter", "none")
        filter_val = backgrounds.get("image_filter_value", 50)
        bg_repeat = backgrounds.get("bg_repeat", "no-repeat")
        bg_attach = backgrounds.get("bg_attachment", "scroll")
        bg_pos = backgrounds.get("bg_position", "center")
        light_cols = backgrounds.get("light_colors", [])

        lines.append("body {")

        # --- Base background ---
        if has_bg_image or bg_type == "image":
            img_path = backgrounds.get("bg_image", "")
            if img_path:
                overlay_type = backgrounds.get("image_overlay", "none")
                overlay_color = backgrounds.get("image_overlay_color", "#000000")
                overlay_opacity_raw = backgrounds.get("image_overlay_opacity", 30)
                overlay_opacity = max(0, min(100, overlay_opacity_raw)) / 100.0
                if overlay_type == "color":
                    r = int(overlay_color[1:3], 16) if len(overlay_color) >= 7 else 0
                    g = int(overlay_color[3:5], 16) if len(overlay_color) >= 7 else 0
                    b = int(overlay_color[5:7], 16) if len(overlay_color) >= 7 else 0
                    ocss = f"rgba({r},{g},{b},{overlay_opacity})"
                    lines.append(f"  background-image: linear-gradient({ocss}, {ocss}), url('{img_path}') !important;")
                elif overlay_type == "gradient":
                    lc_str = ", ".join(light_cols[:3]) if len(light_cols) >= 2 else f"rgba(0,0,0,{overlay_opacity})"
                    dc_str = ", ".join(dark_cols[:3]) if len(dark_cols) >= 2 else lc_str
                    ov_grad = _build_gradient_function(backgrounds, lc_str)
                    ov_grad_dark = _build_gradient_function(backgrounds, dc_str)
                    lines.append(f"  background-image: {ov_grad}, url('{img_path}') !important;")
                else:
                    lines.append(f"  background-image: url('{img_path}') !important;")
                lines.append(f"  background-size: {backgrounds.get('bg_size', 'cover')};")
                lines.append(f"  background-position: {bg_pos};")
                lines.append(f"  background-repeat: {bg_repeat};")
                lines.append(f"  background-attachment: {bg_attach};")

        elif bg_type == "pattern" and pattern != "none":
            lines.append("  background-color: var(--adv-bg) !important;")
            lines.append("  background-image: var(--adv-bg-image);")
            lines.append("  background-size: var(--adv-bg-size);")

        elif bg_type == "gradient":
            if animation in ("flow", "hue_rotate"):
                lines.append("  background-image: var(--adv-bg) !important;")
                lines.append("  background-position: 0% 50%;")
                lines.append("  background-size: 400% 400%;")
            elif animation == "pulse":
                lines.append("  background: var(--adv-bg) !important;")
            else:
                lines.append("  background: var(--adv-bg) !important;")

        elif bg_type == "solid":
            if animation == "shimmer":
                lines.append("  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 50%, transparent 100%), var(--adv-bg);")
                lines.append("  background-size: 200% 100%, 100%;")
                lines.append("  background-repeat: no-repeat;")
            else:
                lines.append("  background: var(--adv-bg) !important;")

        elif bg_type == "video":
            lines.append("  background: transparent !important;")
            has_fallback = bool(backgrounds.get("video_fallback", ""))
            if has_fallback:
                lines.append(f"  background-image: url('{backgrounds['video_fallback']}') !important;")
                lines.append("  background-size: cover;")
                lines.append("  background-position: center;")
            else:
                lines.append("  background-image: none !important;")

        else:
            lines.append("  background: var(--adv-bg) !important;")

        # --- Animation ---
        if bg_type != "video":
            if animation != "none" and not (has_bg_image or bg_type == "image"):
                anim_name = _get_animation_name(bg_type, animation, False)
                if anim_name:
                    lines.append(f"  animation: {anim_name} var(--adv-animation-speed) var(--adv-animation-easing) infinite;")
            elif animation != "none" and (has_bg_image or bg_type == "image"):
                anim_name = _get_animation_name(bg_type, animation, True)
                if anim_name:
                    lines.append(f"  animation: {anim_name} var(--adv-animation-speed) var(--adv-animation-easing) infinite;")

        # --- Blend mode ---
        if blend != "normal":
            lines.append(f"  background-blend-mode: {blend};")

        # --- Opacity ---
        if bg_opacity < 100:
            lines.append(f"  opacity: {bg_opacity / 100.0};")

        # --- Filter ---
        if image_filter != "none" and (has_bg_image or bg_type == "image"):
            filter_map = {
                "grayscale": f"grayscale({filter_val}%)",
                "sepia": f"sepia({filter_val}%)",
                "blur": f"blur({max(filter_val // 10, 1)}px)",
                "brightness": f"brightness({50 + filter_val // 2}%)",
                "contrast": f"contrast({50 + filter_val}%)",
                "hue_rotate": f"hue-rotate({filter_val}deg)",
            }
            fv = filter_map.get(image_filter, "")
            if fv:
                lines.append(f"  filter: {fv};")

        lines.append("  transition: background 0.3s;")
        lines.append("}")
        lines.append("")

        # Dark-mode override for image overlay gradient
        if (has_bg_image or bg_type == "image") and len(dark_cols) >= 2:
            img_path = backgrounds.get("bg_image", "")
            ov_type = backgrounds.get("image_overlay", "none")
            if img_path and ov_type == "gradient":
                dc_str = ", ".join(dark_cols[:3])
                ov_grad_dark = _build_gradient_function(backgrounds, dc_str)
                lc_str = ", ".join(light_cols[:3]) if len(light_cols) >= 2 else ""
                if dc_str != lc_str:
                    lines.append("body.dark-mode {")
                    lines.append(f"  background-image: {ov_grad_dark}, url('{img_path}') !important;")
                    lines.append("}")
                    lines.append("")

        # --- Video background element CSS ---
        if bg_type == "video":
            has_video = bool(backgrounds.get("bg_video", ""))
            if has_video:
                lines.append("#bg-video-container {")
                lines.append("  position: fixed;")
                lines.append("  top: 0; left: 0;")
                lines.append("  width: 100%; height: 100%;")
                lines.append("  z-index: -1;")
                lines.append("  overflow: hidden;")
                lines.append("}")
                lines.append("")
                lines.append("#bg-video {")
                lines.append("  width: 100%;")
                lines.append("  height: 100%;")
                lines.append("  object-fit: cover;")
                if animation == "none":
                    lines.append("  opacity: var(--adv-video-opacity, 1);")
                lines.append("}")
                lines.append("")
                ov_type = backgrounds.get("video_overlay", "none")
                if ov_type != "none":
                    lines.append("#bg-video-container::after {")
                    lines.append("  content: '';")
                    lines.append("  position: absolute;")
                    lines.append("  top: 0; left: 0;")
                    lines.append("  width: 100%; height: 100%;")
                    lines.append("  z-index: 1;")
                    if ov_type == "color":
                        oc = backgrounds.get("video_overlay_color", "#000000")
                        oo = backgrounds.get("video_overlay_opacity", 30)
                        r = int(oc[1:3], 16) if len(oc) >= 7 else 0
                        g = int(oc[3:5], 16) if len(oc) >= 7 else 0
                        b = int(oc[5:7], 16) if len(oc) >= 7 else 0
                        lines.append(f"  background: rgba({r},{g},{b},{max(0, min(100, oo)) / 100.0});")
                    elif ov_type == "gradient":
                        lc = backgrounds.get("light_colors", ["#000", "#000"])
                        dc = backgrounds.get("dark_colors", ["#000", "#000"])
                        ov_grad_fn = _build_gradient_function(backgrounds, ", ".join(lc[:3]))
                        ov_grad_dark = _build_gradient_function(backgrounds, ", ".join(dc[:3]))
                        lines.append(f"  background: {ov_grad_fn};")
                    lines.append("}")
                    lines.append("")
                    if ov_type == "gradient" and ", ".join(dc[:3]) != ", ".join(lc[:3]):
                        lines.append("body.dark-mode #bg-video-container::after {")
                        lines.append(f"  background: {ov_grad_dark};")
                        lines.append("}")
                        lines.append("")
                # Animation on video element
                if animation != "none":
                    anim_name = _get_animation_name("video", animation, False)
                    if anim_name:
                        lines.append("#bg-video {")
                        lines.append(f"  animation: {anim_name} var(--adv-animation-speed) var(--adv-animation-easing) infinite;")
                        lines.append("}")
                        lines.append("")

        # --- Keyframes ---
        if animation != "none":
            kf = _get_animation_keyframes(bg_type, animation, has_bg_image or bg_type == "image")
            for k in kf:
                lines.append(k)
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
                "zoom": ".ck-content img:not([style*=\"float\"]) { transition: transform 0.3s; } .ck-content img:not([style*=\"float\"]):hover { transform: scale(1.03); }",
                "overlay": ".ck-content img:not([style*=\"float\"]) { position: relative; } .ck-content img:not([style*=\"float\"]):hover { filter: brightness(1.1); }",
                "grayscale": ".ck-content img:not([style*=\"float\"]) { filter: grayscale(0); transition: filter 0.3s; } .ck-content img:not([style*=\"float\"]):hover { filter: grayscale(0); }",
            }
            if image_hover in effects:
                lines.append(effects[image_hover])
                lines.append("")

        if hover_effects.get("smooth_scroll", True):
            lines.append("html { scroll-behavior: smooth; }")
            lines.append("")

        if scroll_reveal:
            lines.append(""".home-card, .comment, .ck-content img, .ck-content blockquote {
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
body, .ck-content {
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
            lines.append(".ck-content a { color: var(--adv-link-color, var(--accent)); }")
        elif ls == "underline":
            lines.append(".ck-content a { text-decoration: underline; }")
        elif ls == "animated":
            lines.append(""".ck-content a {
  background-image: linear-gradient(var(--accent), var(--accent));
  background-size: 0 2px;
  background-repeat: no-repeat;
  background-position: left bottom;
  transition: background-size 0.3s;
  text-decoration: none;
}
.ck-content a:hover {
  background-size: 100% 2px;
}
""")

        if bq == "icon":
            lines.append(""".ck-content blockquote {
  border-left: none;
  padding-left: 3rem;
  position: relative;
}
.ck-content blockquote::before {
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
            lines.append(""".ck-content blockquote {
  border-left: none;
  background: var(--card-bg);
  border-radius: var(--adv-radius-card, 8px);
  padding: 1rem 1.5rem;
}
""")
        elif bq == "stylized":
            lines.append(""".ck-content blockquote {
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
    path = _adv_css()
    if not path:
        return False
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(css)
        return True
    except Exception as e:
        print(f"Error writing advanced.css: {e}")
        return False
