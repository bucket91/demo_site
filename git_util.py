"""Bundled git helper — uses system git on Linux, bundled MinGit on Windows."""
import os, sys, subprocess


def get_git_path():
    if getattr(sys, 'frozen', False) and sys.platform == "win32":
        meipass = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(sys.argv[0]))
        candidate = os.path.join(meipass, "mingit", "bin", "git.exe")
        if os.path.exists(candidate):
            return candidate
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
