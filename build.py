#!/usr/bin/env python3
"""Build Site Tools as a standalone executable for your current OS.

For cross-platform builds (Windows exe from Linux, or vice versa),
push to GitHub — the .github/workflows/build.yml workflow will build
both Linux and Windows executables automatically and upload them as
build artifacts.

Usage:
  python build.py          # builds for current OS, bundling everything
  python build.py --clean  # removes old build artifacts
"""
import os, sys, platform, subprocess, shutil, argparse, tarfile, urllib.request, urllib.error, zipfile, stat, time

SITE_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = platform.system() == "Windows"
EXE_NAME = "SiteTools.exe" if IS_WINDOWS else "SiteTools"
VENV_DIR = os.path.join(SITE_DIR, "build_venv")
BIN_DIR = "Scripts" if IS_WINDOWS else "bin"
PYINSTALLER = os.path.join(VENV_DIR, BIN_DIR, "pyinstaller")
PIP = os.path.join(VENV_DIR, BIN_DIR, "pip")

# Git
MINGIT_URL = "https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/MinGit-2.48.1-64-bit.zip"
MINGIT_ZIP = os.path.join(SITE_DIR, "mingit.zip")
MINGIT_DIR = os.path.join(SITE_DIR, "mingit")

LINUX_GIT_URL = "https://github.com/darkvertex/static-git/releases/latest/download/git-binaries.linux-64bit.tar.gz"
LINUX_GIT_TGZ = os.path.join(SITE_DIR, "git-linux.tar.gz")
LINUX_GIT_DIR = os.path.join(SITE_DIR, "bundled-git")

# FFmpeg
FFMPEG_WIN_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_WIN_ZIP = os.path.join(SITE_DIR, "ffmpeg-win.zip")
FFMPEG_WIN_DIR = os.path.join(SITE_DIR, "ffmpeg")

FFMPEG_LINUX_URL = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
FFMPEG_LINUX_TAR = os.path.join(SITE_DIR, "ffmpeg-linux.tar.xz")
FFMPEG_LINUX_DIR = os.path.join(SITE_DIR, "ffmpeg")

_RETRY_DELAYS = [2, 5, 15, 30]


def _download_with_retry(url, dst, label=""):
    """Download url to dst with retries on failure. Returns True on success."""
    prefix = f"  {label}: " if label else "  "
    for attempt, delay in enumerate(_RETRY_DELAYS):
        try:
            urllib.request.urlretrieve(url, dst)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"{prefix}404 — {url}")
                return False
            print(f"{prefix}HTTP {e.code}, retry {attempt+1}/{len(_RETRY_DELAYS)} in {delay}s...")
        except (urllib.error.URLError, OSError) as e:
            print(f"{prefix}{e}, retry {attempt+1}/{len(_RETRY_DELAYS)} in {delay}s...")
        time.sleep(delay)
    print(f"{prefix}Failed after {len(_RETRY_DELAYS)} attempts")
    return False


def clean():
    for d in ["build", "dist", "__pycache__"]:
        p = os.path.join(SITE_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    for f in ["SiteTools.spec", "SiteTools", "SiteTools.exe"]:
        p = os.path.join(SITE_DIR, f)
        if os.path.exists(p):
            os.remove(p)
    for p in [MINGIT_ZIP, MINGIT_DIR, LINUX_GIT_TGZ, LINUX_GIT_DIR,
              FFMPEG_WIN_ZIP, FFMPEG_WIN_DIR, FFMPEG_LINUX_TAR, FFMPEG_LINUX_DIR]:
        if os.path.exists(p):
            os.remove(p) if os.path.isfile(p) else shutil.rmtree(p)
    if os.path.exists(VENV_DIR):
        shutil.rmtree(VENV_DIR)
    print("Cleaned build artifacts.")


def setup_venv():
    if os.path.exists(PYINSTALLER):
        return
    print("Creating build venv and installing PyInstaller + PyQt6...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    subprocess.run([PIP, "install", "pyinstaller", "PyQt6", "PyQt6-WebEngine"], check=True)


def download_mingit():
    if os.path.exists(MINGIT_DIR):
        return
    print("Downloading MinGit for Windows bundling...")
    if not _download_with_retry(MINGIT_URL, MINGIT_ZIP, "MinGit"):
        print("WARNING: MinGit download failed — git operations will require system git")
        return
    os.makedirs(MINGIT_DIR, exist_ok=True)
    with zipfile.ZipFile(MINGIT_ZIP, "r") as z:
        z.extractall(MINGIT_DIR)
    os.remove(MINGIT_ZIP)
    print(f"MinGit extracted to {MINGIT_DIR}")


def _strip_mingit():
    """Remove bloat from MinGit to reduce executable size."""
    if not os.path.exists(MINGIT_DIR):
        return
    mingit_bin = os.path.join(MINGIT_DIR, "mingw64", "bin")
    if not os.path.exists(mingit_bin):
        return

    removed_bytes = 0
    def _rm(path):
        nonlocal removed_bytes
        if not os.path.exists(path):
            return
        if os.path.isfile(path):
            removed_bytes += os.path.getsize(path)
            os.remove(path)
        elif os.path.isdir(path):
            for dp, dn, fn in os.walk(path):
                for f in fn:
                    fp = os.path.join(dp, f)
                    try:
                        removed_bytes += os.path.getsize(fp)
                        os.remove(fp)
                    except OSError:
                        pass
            shutil.rmtree(path, ignore_errors=True)

    # Remove GCM (Git Credential Manager) — ~28 MB
    for f in list(os.listdir(mingit_bin)):
        if f.startswith("git-credential-manager"):
            _rm(os.path.join(mingit_bin, f))

    # Remove GCM-related DLLs (Avalonia, SkiaSharp, MSAL, etc.)
    gcm_prefixes = ("Avalonia", "SkiaSharp", "HarfBuzzSharp", "Microsoft.",
                    "System.", "gcmcore", "GitHub.", "GitLab.", "Atlassian.",
                    "MicroCom.", "msalruntime", "MSAL")
    for f in list(os.listdir(mingit_bin)):
        if any(f.startswith(p) for p in gcm_prefixes):
            _rm(os.path.join(mingit_bin, f))

    # Remove scalar.exe (14.6 MB) and headless-git.exe
    _rm(os.path.join(mingit_bin, "scalar.exe"))
    _rm(os.path.join(mingit_bin, "headless-git.exe"))
    _rm(os.path.join(MINGIT_DIR, "cmd", "scalar.exe"))
    _rm(os.path.join(MINGIT_DIR, "cmd", "tig.exe"))

    # Remove cmd/ wrappers (we use mingw64/bin/git.exe directly)
    _rm(os.path.join(MINGIT_DIR, "cmd"))

    # Remove MSYS2 usr/ (not needed for git builtins on Windows)
    _rm(os.path.join(MINGIT_DIR, "usr"))

    # Remove etc/ssh (not needed for HTTPS)
    _rm(os.path.join(MINGIT_DIR, "etc", "ssh"))

    # Remove libexec/git-core scripts and mergetools
    _rm(os.path.join(MINGIT_DIR, "mingw64", "libexec"))

    # Remove docs, licenses, share
    for d in ("doc", "share"):
        _rm(os.path.join(MINGIT_DIR, "mingw64", d))
    _rm(os.path.join(MINGIT_DIR, "LICENSE.txt"))

    # Remove non-essential standalone utilities
    for f in ("brotli.exe", "psl.exe", "proxy-lookup.exe",
              "blocked-file-util.exe", "c_rehash",
              "git-update-git-for-windows", "git-askpass.exe",
              "git-askyesno.exe",
              "git-credential-helper-selector.exe"):
        _rm(os.path.join(mingit_bin, f))

    remaining = sum(os.path.getsize(os.path.join(dp, f))
                    for dp, dn, fn in os.walk(MINGIT_DIR) for f in fn)
    print(f"  Stripped MinGit: removed ~{removed_bytes / 1024 / 1024:.0f} MB, "
          f"{remaining / 1024 / 1024:.0f} MB remaining")


def download_linux_git():
    if os.path.exists(LINUX_GIT_DIR):
        return
    print("Downloading static git for Linux bundling...")
    if not _download_with_retry(LINUX_GIT_URL, LINUX_GIT_TGZ, "Linux git"):
        print("WARNING: Linux git download failed — git operations will require system git")
        return
    os.makedirs(LINUX_GIT_DIR, exist_ok=True)
    with tarfile.open(LINUX_GIT_TGZ, "r:gz") as t:
        for member in t.getmembers():
            if member.isfile():
                base = os.path.basename(member.name)
                if base:
                    member.name = base
                    t.extract(member, LINUX_GIT_DIR)
                    dst = os.path.join(LINUX_GIT_DIR, base)
                    st = os.stat(dst)
                    os.chmod(dst, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    os.remove(LINUX_GIT_TGZ)
    print(f"Static git extracted to {LINUX_GIT_DIR}")


def _strip_linux_git():
    """Keep only the git binary from bundled static git; remove the rest."""
    if not os.path.exists(LINUX_GIT_DIR):
        return
    keep = {"git"}
    removed_bytes = 0
    for f in list(os.listdir(LINUX_GIT_DIR)):
        if f not in keep:
            fp = os.path.join(LINUX_GIT_DIR, f)
            if os.path.isfile(fp):
                removed_bytes += os.path.getsize(fp)
                os.remove(fp)
    remaining = sum(os.path.getsize(os.path.join(LINUX_GIT_DIR, f))
                    for f in os.listdir(LINUX_GIT_DIR) if os.path.isfile(os.path.join(LINUX_GIT_DIR, f)))
    print(f"  Stripped Linux git: removed ~{removed_bytes / 1024 / 1024:.0f} MB, "
          f"{remaining / 1024 / 1024:.0f} MB remaining")


def download_fonts():
    """Download bundled fonts defined in themes.BUNDLED_FONTS."""
    fonts_dir = os.path.join(SITE_DIR, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    try:
        sys.path.insert(0, SITE_DIR)
        from themes import BUNDLED_FONTS
    except Exception:
        print("Warning: could not import BUNDLED_FONTS, skipping font download")
        return
    for name, info in BUNDLED_FONTS.items():
        fn = info.get("filename", "")
        if not fn:
            continue
        dst = os.path.join(fonts_dir, fn)
        if os.path.exists(dst):
            continue
        url = info.get("url", "")
        if url:
            print(f"Downloading {name}...")
            if not _download_with_retry(url, dst, name):
                print(f"  Skipping {name}")
        else:
            print(f"  No download URL for {name}. Place {fn} in site/fonts/ manually.")


def download_ckeditor():
    ckeditor_dir = os.path.join(SITE_DIR, "ckeditor")
    os.makedirs(ckeditor_dir, exist_ok=True)
    umd_path = os.path.join(ckeditor_dir, "ckeditor5.umd.js")
    css_path = os.path.join(ckeditor_dir, "ckeditor5.css")
    if os.path.exists(umd_path) and os.path.exists(css_path):
        return
    print("Downloading CKEditor...")
    if not os.path.exists(umd_path):
        _download_with_retry(
            "https://cdn.ckeditor.com/ckeditor5/42.0.0/ckeditor5.umd.js", umd_path, "ckeditor5.umd.js")
    if not os.path.exists(css_path):
        _download_with_retry(
            "https://cdn.ckeditor.com/ckeditor5/42.0.0/ckeditor5.css", css_path, "ckeditor5.css")
    print(f"CKEditor files saved to {ckeditor_dir}")


def download_ffmpeg():
    if IS_WINDOWS:
        if os.path.exists(os.path.join(FFMPEG_WIN_DIR, "ffmpeg.exe")):
            return
        print("Downloading FFmpeg for Windows bundling...")
        if not _download_with_retry(FFMPEG_WIN_URL, FFMPEG_WIN_ZIP, "FFmpeg"):
            print("WARNING: FFmpeg download failed — image/video conversion will require system ffmpeg")
            return
        os.makedirs(FFMPEG_WIN_DIR, exist_ok=True)
        with zipfile.ZipFile(FFMPEG_WIN_ZIP, "r") as z:
            for member in z.namelist():
                if member.endswith("ffmpeg.exe"):
                    z.extract(member, FFMPEG_WIN_DIR)
                    src = os.path.join(FFMPEG_WIN_DIR, member)
                    dst = os.path.join(FFMPEG_WIN_DIR, "ffmpeg.exe")
                    if src != dst:
                        shutil.move(src, dst)
                    break
        os.remove(FFMPEG_WIN_ZIP)
        if os.path.exists(os.path.join(FFMPEG_WIN_DIR, "ffmpeg.exe")):
            print(f"FFmpeg extracted to {FFMPEG_WIN_DIR}")
        else:
            print("WARNING: could not find ffmpeg.exe in downloaded archive")
    else:
        if os.path.exists(os.path.join(FFMPEG_LINUX_DIR, "ffmpeg")):
            return
        print("Downloading FFmpeg for Linux bundling...")
        ok = _download_with_retry(FFMPEG_LINUX_URL, FFMPEG_LINUX_TAR, "FFmpeg (johnvansickle)")
        if not ok:
            print("  Primary URL failed, trying fallback (BtbN GitHub)...")
            FFMPEG_LINUX_FALLBACK = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-latest-linux64-gpl-7.1.tar.xz"
            FFMPEG_LINUX_TAR_ALT = os.path.join(SITE_DIR, "ffmpeg-linux-btbn.tar.xz")
            ok = _download_with_retry(FFMPEG_LINUX_FALLBACK, FFMPEG_LINUX_TAR_ALT, "FFmpeg (BtbN)")
            if ok:
                if os.path.exists(FFMPEG_LINUX_TAR):
                    os.remove(FFMPEG_LINUX_TAR)
                os.rename(FFMPEG_LINUX_TAR_ALT, FFMPEG_LINUX_TAR)
        if not ok:
            print("WARNING: FFmpeg download failed — image/video conversion will require system ffmpeg")
            return
        os.makedirs(FFMPEG_LINUX_DIR, exist_ok=True)
        with tarfile.open(FFMPEG_LINUX_TAR, "r:xz") as t:
            for member in t.getmembers():
                if member.name.endswith("ffmpeg") and "/" in member.name:
                    member.name = "ffmpeg"
                    t.extract(member, FFMPEG_LINUX_DIR)
                    dst = os.path.join(FFMPEG_LINUX_DIR, "ffmpeg")
                    st = os.stat(dst)
                    os.chmod(dst, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    break
        os.remove(FFMPEG_LINUX_TAR)
        if os.path.exists(os.path.join(FFMPEG_LINUX_DIR, "ffmpeg")):
            print(f"FFmpeg extracted to {FFMPEG_LINUX_DIR}")
        else:
            print("WARNING: could not find ffmpeg binary in downloaded archive")


def build():
    os.chdir(SITE_DIR)
    dist_dir = os.path.join(SITE_DIR, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    cmd = [
        PYINSTALLER,
        "--onefile",
        "--name", "SiteTools",
        "--distpath", dist_dir,
        "--workpath", os.path.join(SITE_DIR, "build"),
        "--specpath", SITE_DIR,
        "--optimize", "2",
        "--hidden-import", "PyQt6.sip",
        "--hidden-import", "PyQt6.QtWebEngineWidgets",
        "--hidden-import", "PyQt6.QtWebEngineCore",
        "--hidden-import", "docx2html",
        "--hidden-import", "sidebar_util",
        "--hidden-import", "first_run",
        "--hidden-import", "advanced_theme",
        "--hidden-import", "git_util",
        "--hidden-import", "bootstrap",
        "app.py",
    ]

    for mod in ("tkinter", "test", "distutils", "idlelib", "ensurepip",
                "lib2to3", "unittest", "pydoc", "xmlrpc",
                "turtledemo", "zipapp", "http.server"):
        cmd.extend(["--exclude-module", mod])

    if IS_WINDOWS:
        download_mingit()
        _strip_mingit()
        cmd.extend(["--add-data", f"mingit{os.pathsep}mingit"])
        cmd.extend(["--add-data", f"ckeditor{os.pathsep}ckeditor"])
        ico = os.path.join(SITE_DIR, "logo.ico")
        if os.path.exists(ico):
            cmd.extend(["--icon", "logo.ico"])
        ver = os.path.join(SITE_DIR, "version_info.txt")
        if os.path.exists(ver):
            cmd.extend(["--version-file", "version_info.txt"])
    else:
        download_linux_git()
        _strip_linux_git()
        cmd.extend(["--add-data", f"bundled-git{os.pathsep}bundled-git"])
        cmd.extend(["--add-data", f"ckeditor{os.pathsep}ckeditor"])
        cmd.extend(["--icon", "logo.png"])

    download_ffmpeg()
    ffmpeg_dir = FFMPEG_WIN_DIR if IS_WINDOWS else FFMPEG_LINUX_DIR
    if os.path.exists(ffmpeg_dir):
        cmd.extend(["--add-data", f"ffmpeg{os.pathsep}ffmpeg"])

    download_ckeditor()
    download_fonts()

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    src = os.path.join(dist_dir, EXE_NAME)
    dst = os.path.join(SITE_DIR, EXE_NAME)
    shutil.copy(src, dst)
    # Clean up downloaded bundles
    for p in [MINGIT_DIR, MINGIT_ZIP, LINUX_GIT_DIR, LINUX_GIT_TGZ,
              FFMPEG_WIN_DIR, FFMPEG_WIN_ZIP, FFMPEG_LINUX_DIR, FFMPEG_LINUX_TAR]:
        if os.path.exists(p):
            os.remove(p) if os.path.isfile(p) else shutil.rmtree(p)
    print(f"\nDone! Executable: {dst}")
    print(f"Size: {os.path.getsize(dst) / 1024 / 1024:.0f} MB")
    print(f"Place it in your site directory and run{' ./' if not IS_WINDOWS else ' '}{EXE_NAME}")


def main():
    parser = argparse.ArgumentParser(description="Build Site Tools executable")
    parser.add_argument("--clean", action="store_true", help="Remove old build artifacts")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    setup_venv()
    build()


if __name__ == "__main__":
    main()
