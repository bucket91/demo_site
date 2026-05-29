"""Bundled git helper — finds bundled git first, falls back to system git."""
import os, sys, subprocess


def get_git_path():
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(sys.argv[0]))
        candidates = [
            os.path.join(meipass, "bundled-git", "git"),
            os.path.join(meipass, "mingit", "cmd", "git.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
    return "git"


def is_git_available():
    try:
        subprocess.run([get_git_path(), "--version"], capture_output=True)
        return True
    except FileNotFoundError:
        return False


def git_run(args, cwd=None, **kwargs):
    try:
        return subprocess.run([get_git_path()] + args, cwd=cwd, **kwargs)
    except FileNotFoundError:
        return None
