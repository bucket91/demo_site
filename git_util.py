"""Bundled git helper — prefers system git (has HTTPS support)."""
import os, sys, subprocess, shutil


class GitError(Exception):
    pass

class NoGitRepo(GitError):
    pass

class NoCommits(GitError):
    pass

class UnrelatedHistories(GitError):
    pass

class AuthFailed(GitError):
    pass

class NetworkError(GitError):
    pass

class PushRejected(GitError):
    pass


def get_git_path():
    system = shutil.which("git")
    if system:
        return system
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(__file__))
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


def _dummy_result():
    return subprocess.CompletedProcess(args=[], returncode=-1, stdout="", stderr="")

def git_run(args, cwd=None, **kwargs):
    try:
        if kwargs.get('text') or kwargs.get('universal_newlines'):
            kwargs['encoding'] = 'utf-8'
            kwargs['errors'] = 'replace'
        return subprocess.run([get_git_path()] + args, cwd=cwd, **kwargs)
    except FileNotFoundError:
        return _dummy_result()


def _make_push_url(url, token):
    if token and url.startswith('https://'):
        after = url[8:]
        if '@' in after:
            after = after.split('@', 1)[1]
        return f'https://{token}@{after}'
    return url


def _extract_github_user(url):
    url = url.strip()
    if 'github.com/' in url:
        after = url.split('github.com/', 1)[1]
        return after.split('/')[0] if '/' in after else after
    if 'github.com:' in url:
        after = url.split('github.com:', 1)[1]
        return after.split('/')[0] if '/' in after else after
    return ""


def is_valid_git_repo(path):
    r = git_run(["rev-parse", "--git-dir"], cwd=path, capture_output=True, text=True)
    return r.returncode == 0


def has_commits(path):
    r = git_run(["rev-parse", "--verify", "HEAD"], cwd=path, capture_output=True)
    return r.returncode == 0


def ensure_branch_exists(path, branch="main"):
    if not has_commits(path):
        git_run(["add", "-A"], cwd=path, capture_output=True)
        cmd = [
            "-c", "user.name=Auto Builder",
            "-c", "user.email=auto@builder.local",
            "commit", "--allow-empty", "-m", "initial"
        ]
        r = git_run(cmd, cwd=path, capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" not in r.stdout and "nothing to commit" not in r.stderr:
            git_run(cmd, cwd=path, capture_output=True)


def ensure_on_branch(path, branch="main"):
    r = git_run(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path, capture_output=True, text=True)
    current = r.stdout.strip() if r.returncode == 0 else ""
    if current == branch:
        return branch
    if current and current != "HEAD":
        if current == "master":
            git_run(["branch", "-m", "master", branch], cwd=path, capture_output=True)
            return branch
        return current
    r = git_run(["checkout", "-b", branch], cwd=path, capture_output=True)
    if r.returncode != 0:
        r = git_run(["checkout", branch], cwd=path, capture_output=True)
    return branch


def remote_branch_exists(remote, branch, cwd):
    r = git_run(["ls-remote", "--heads", remote, branch], cwd=cwd, capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() != ""


def get_remote_default_branch(cwd):
    r = git_run(["ls-remote", "--symref", "origin", "HEAD"], cwd=cwd, capture_output=True, text=True)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            if "ref:" in line and "HEAD" in line:
                parts = line.split("ref:")[1].strip().split()
                if parts:
                    ref = parts[0].strip()
                    if ref.startswith("refs/heads/"):
                        return ref[11:]
    return "main"


def histories_unrelated(cwd):
    r = git_run(["merge-base", "HEAD", "origin/HEAD"], cwd=cwd, capture_output=True, text=True)
    return r.returncode != 0


def detect_push_error(stderr):
    if not stderr:
        return None
    if "Authentication failed" in stderr or "403" in stderr or "401" in stderr:
        return AuthFailed("Authentication failed — check your GitHub token")
    if "GH001" in stderr or "large files" in stderr:
        return PushRejected("GitHub rejected the push because a file exceeds the 100MB limit.")
    if "protected branch" in stderr or "hook declined" in stderr:
        return PushRejected("Push rejected — branch is protected.")
    if "Could not read from remote" in stderr or "resolve host" in stderr or "Connection refused" in stderr or "Network is unreachable" in stderr:
        return NetworkError("Network error — check your internet connection")
    if "rejected" in stderr and "fetch first" in stderr:
        return PushRejected("Remote has commits you don't have locally")
    if "rejected" in stderr or "failed to push" in stderr:
        return PushRejected("Push was rejected")
    return None


def safe_fetch(cwd):
    try:
        r = git_run(["fetch", "origin"], cwd=cwd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise NetworkError("Fetch timed out — check your internet connection")
    if r.returncode != 0:
        err = r.stderr
        if "Authentication failed" in err or "403" in err or "401" in err:
            raise AuthFailed("Authentication failed — check your GitHub token")
        if "Could not read from remote" in err or "resolve host" in err or "Connection refused" in err or "Network is unreachable" in err:
            raise NetworkError("Network error — check your internet connection")
        return False
    return True


def safe_pull_rebase(cwd, branch):
    r = git_run(["pull", "--rebase", "-X", "theirs", "origin", branch], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        git_run(["rebase", "--abort"], cwd=cwd, capture_output=True)
        return False
    return True
