#!/usr/bin/env python3
import json, os, threading, webbrowser, io, contextlib
from http.server import HTTPServer, BaseHTTPRequestHandler

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")
PORT = 8765

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site Generator</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; background: #1a1a2e; color: #eee; display: flex; justify-content: center; padding: 2rem; }
  .card { background: #16213e; border-radius: 12px; padding: 2rem; max-width: 600px; width: 100%; }
  h1 { margin-bottom: 0.5rem; font-size: 1.5rem; }
  p.sub { color: #a8b2d1; margin-bottom: 1.5rem; font-size: 0.9rem; }
  label { display: block; margin-top: 1rem; margin-bottom: 0.3rem; color: #a8b2d1; font-size: 0.85rem; }
  input[type="text"], input[type="url"] { width: 100%; padding: 0.6rem; border: 1px solid #0f3460; border-radius: 6px; background: #0f3460; color: #eee; font-family: inherit; font-size: 0.9rem; }
  input:focus { outline: none; border-color: #533483; }
  .row { display: flex; gap: 1rem; align-items: center; margin-top: 1rem; }
  .row label { margin: 0; }
  button { background: #533483; color: #fff; border: none; padding: 0.75rem 2rem; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 600; margin-top: 1.5rem; width: 100%; }
  button:hover { background: #6c3fa3; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  pre { background: #0f3460; padding: 1rem; border-radius: 8px; margin-top: 1rem; max-height: 300px; overflow-y: auto; font-size: 0.8rem; white-space: pre-wrap; display: none; }
  .status { margin-top: 1rem; padding: 0.5rem; border-radius: 6px; display: none; }
  .status.ok { background: #1b5e20; display: block; }
  .status.err { background: #b71c1c; display: block; }
</style>
</head>
<body>
<div class="card">
  <h1>Site Generator</h1>
  <p class="sub" id="cwd">/home/mhd/site</p>

  <h2 style="margin-top:1.5rem;font-size:1rem;border-bottom:1px solid #0f3460;padding-bottom:0.5rem">Supabase</h2>

  <label>Project URL</label>
  <input type="url" id="supabase_url" placeholder="https://xxx.supabase.co">

  <label>Anon Key</label>
  <input type="text" id="supabase_anon_key" placeholder="eyJ... or sb_publishable_...">

  <div class="row">
    <input type="checkbox" id="comments_enabled" checked>
    <label for="comments_enabled">Enable comments</label>
  </div>

  <h2 style="margin-top:1.5rem;font-size:1rem;border-bottom:1px solid #0f3460;padding-bottom:0.5rem">GitHub</h2>

  <label>Remote URL</label>
  <input type="url" id="git_remote_url" placeholder="https://github.com/user/repo.git">

  <label>Git User Name</label>
  <input type="text" id="git_user_name" placeholder="Your GitHub username">

  <label>Git User Email</label>
  <input type="text" id="git_user_email" placeholder="user@users.noreply.github.com">

  <label>Commit Message</label>
  <input type="text" id="git_commit_message" placeholder="update site via generator">

  <div class="row">
    <input type="checkbox" id="git_auto_push" checked>
    <label for="git_auto_push">Auto push to GitHub</label>
  </div>

  <button id="runBtn" onclick="run()">Generate &amp; Push</button>

  <div id="status" class="status"></div>
  <pre id="output"></pre>
</div>

<script>
var loaded = false;

function loadConfig() {
  fetch('/config').then(function(r) { return r.json(); }).then(function(cfg) {
    document.getElementById('supabase_url').value = cfg.supabase_url || '';
    document.getElementById('supabase_anon_key').value = cfg.supabase_anon_key || '';
    document.getElementById('git_remote_url').value = cfg.git_remote_url || '';
    document.getElementById('git_user_name').value = cfg.git_user_name || '';
    document.getElementById('git_user_email').value = cfg.git_user_email || '';
    document.getElementById('git_commit_message').value = cfg.git_commit_message || 'update site via generator';
    document.getElementById('comments_enabled').checked = cfg.comments_enabled !== false;
    document.getElementById('git_auto_push').checked = cfg.git_auto_push !== false;
    loaded = true;
  });
}

function saveConfig() {
  return {
    supabase_url: document.getElementById('supabase_url').value,
    supabase_anon_key: document.getElementById('supabase_anon_key').value,
    git_remote_url: document.getElementById('git_remote_url').value,
    git_user_name: document.getElementById('git_user_name').value,
    git_user_email: document.getElementById('git_user_email').value,
    git_commit_message: document.getElementById('git_commit_message').value,
    comments_enabled: document.getElementById('comments_enabled').checked,
    git_auto_push: document.getElementById('git_auto_push').checked
  };
}

function log(msg) {
  var pre = document.getElementById('output');
  pre.style.display = 'block';
  pre.textContent += msg + '\\n';
  pre.scrollTop = pre.scrollHeight;
}

function status(msg, ok) {
  var s = document.getElementById('status');
  s.textContent = msg;
  s.className = 'status ' + (ok ? 'ok' : 'err');
  s.style.display = 'block';
}

function run() {
  if (!loaded) return;
  var btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.textContent = 'Running...';
  var pre = document.getElementById('output');
  pre.textContent = '';
  pre.style.display = 'none';
  document.getElementById('status').style.display = 'none';

  var cfg = saveConfig();

  fetch('/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cfg)
  }).then(function(r) { return r.json(); }).then(function(result) {
    if (result.ok) {
      status('Done! Site generated and pushed.', true);
    } else {
      status('Error: ' + (result.error || 'unknown'), false);
    }
    log(result.output || '');
    btn.disabled = false;
    btn.textContent = 'Generate & Push';
  });
}

loadConfig();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/config':
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE) as f:
                    cfg = json.load(f)
            self.send_json(cfg)
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            with open(CONFIG_FILE, 'w') as f:
                json.dump(body, f, indent=2)

            # Run generate + git in a thread so response comes after
            buf = io.StringIO()
            def log_line(msg):
                buf.write(msg + '\n')

            ok = True
            try:
                import generate
                generate.CONFIG.update(body)

                old_stdout = generate.log_func if hasattr(generate, 'log_func') else print
                generate.write_comments_js()
                if not generate.generate_all(log_func=log_line):
                    ok = False
                generate.git_commit_push(log_func=log_line)
            except Exception as e:
                log_line(f"Error: {e}")
                ok = False

            self.send_json({"ok": ok, "output": buf.getvalue()})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

def main():
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f"GUI running at http://127.0.0.1:{PORT}")
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    main()
