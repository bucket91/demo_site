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
import os, sys, platform, subprocess, shutil, argparse, tarfile, urllib.request, zipfile, stat

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = platform.system() == "Windows"
EXE_NAME = "SiteTools.exe" if IS_WINDOWS else "SiteTools"
VENV_DIR = os.path.join(SITE_DIR, "build_venv")
BIN_DIR = "Scripts" if IS_WINDOWS else "bin"
PYINSTALLER = os.path.join(VENV_DIR, BIN_DIR, "pyinstaller")
PIP = os.path.join(VENV_DIR, BIN_DIR, "pip")

MINGIT_URL = "https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/MinGit-2.48.1-64-bit.zip"
MINGIT_ZIP = os.path.join(SITE_DIR, "mingit.zip")
MINGIT_DIR = os.path.join(SITE_DIR, "mingit")

LINUX_GIT_URL = "https://github.com/darkvertex/static-git/releases/latest/download/git-binaries.linux-64bit.tar.gz"
LINUX_GIT_TGZ = os.path.join(SITE_DIR, "git-linux.tar.gz")
LINUX_GIT_DIR = os.path.join(SITE_DIR, "bundled-git")


def clean():
    for d in ["build", "dist", "__pycache__"]:
        p = os.path.join(SITE_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    for f in ["SiteTools.spec", "SiteTools", "SiteTools.exe"]:
        p = os.path.join(SITE_DIR, f)
        if os.path.exists(p):
            os.remove(p)
    for p in [MINGIT_ZIP, MINGIT_DIR, LINUX_GIT_TGZ, LINUX_GIT_DIR]:
        if os.path.exists(p):
            os.remove(p) if os.path.isfile(p) else shutil.rmtree(p)
    if os.path.exists(VENV_DIR):
        shutil.rmtree(VENV_DIR)
    print("Cleaned build artifacts.")


def setup_venv():
    if os.path.exists(PYINSTALLER):
        return
    print("Creating build venv and installing PyInstaller + PyQt5...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    subprocess.run([PIP, "install", "pyinstaller", "PyQt5"], check=True)


def download_mingit():
    if os.path.exists(MINGIT_DIR):
        return
    print("Downloading MinGit for Windows bundling...")
    urllib.request.urlretrieve(MINGIT_URL, MINGIT_ZIP)
    os.makedirs(MINGIT_DIR, exist_ok=True)
    with zipfile.ZipFile(MINGIT_ZIP, "r") as z:
        z.extractall(MINGIT_DIR)
    os.remove(MINGIT_ZIP)
    print(f"MinGit extracted to {MINGIT_DIR}")


def download_linux_git():
    if os.path.exists(LINUX_GIT_DIR):
        return
    print("Downloading static git for Linux bundling...")
    urllib.request.urlretrieve(LINUX_GIT_URL, LINUX_GIT_TGZ)
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
        "app.py",
    ]

    if IS_WINDOWS:
        download_mingit()
        cmd.extend(["--add-data", f"mingit{os.pathsep}mingit"])
    else:
        download_linux_git()
        cmd.extend(["--add-data", f"bundled-git{os.pathsep}bundled-git"])

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    src = os.path.join(dist_dir, EXE_NAME)
    dst = os.path.join(SITE_DIR, EXE_NAME)
    shutil.copy2(src, dst)
    # Clean up git bundle after build
    for p in [MINGIT_DIR, MINGIT_ZIP, LINUX_GIT_DIR, LINUX_GIT_TGZ]:
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
