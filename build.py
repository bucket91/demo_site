#!/usr/bin/env python3
"""Build Site Tools as a standalone executable for your current OS.

For cross-platform builds (Windows exe from Linux, or vice versa),
push to GitHub — the .github/workflows/build.yml workflow will build
both Linux and Windows executables automatically and upload them as
build artifacts.

Usage:
  python build.py          # builds for current OS
  python build.py --clean  # removes old build artifacts
"""
import os, sys, platform, subprocess, shutil, argparse

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = platform.system() == "Windows"
EXE_NAME = "SiteTools.exe" if IS_WINDOWS else "SiteTools"
VENV_DIR = os.path.join(SITE_DIR, "build_venv")
BIN_DIR = "Scripts" if IS_WINDOWS else "bin"
PYINSTALLER = os.path.join(VENV_DIR, BIN_DIR, "pyinstaller")
PIP = os.path.join(VENV_DIR, BIN_DIR, "pip")
PYTHON = os.path.join(VENV_DIR, BIN_DIR, "python" + (".exe" if IS_WINDOWS else ""))


def clean():
    for d in ["build", "dist", "__pycache__"]:
        p = os.path.join(SITE_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    for f in ["SiteTools.spec", "SiteTools", "SiteTools.exe"]:
        p = os.path.join(SITE_DIR, f)
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(VENV_DIR):
        shutil.rmtree(VENV_DIR)
    print("Cleaned build artifacts.")


def setup_venv():
    if os.path.exists(PYINSTALLER):
        return
    print("Creating build venv and installing PyInstaller + PyQt5...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    subprocess.run([PIP, "install", "pyinstaller", "PyQt5"], check=True)


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
        "--hidden-import", "PyQt5.sip",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        "app.py",
    ]
    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    src = os.path.join(dist_dir, EXE_NAME)
    dst = os.path.join(SITE_DIR, EXE_NAME)
    shutil.copy2(src, dst)
    print(f"\nDone! Executable: {dst}")
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
