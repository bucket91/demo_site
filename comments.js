const SUPABASE_URL = {url!r};
const SUPABASE_ANON_KEY = {key!r};

(function() {
  var section = document.getElementById('comments-section');
  var page = section ? section.getAttribute('data-page') : '/';

  async function loadComments() {
    var res = await fetch(
      SUPABASE_URL + '/rest/v1/comments?page=eq.' + encodeURIComponent(page) + '&order=created_at.desc',
      { headers: { apikey: SUPABASE_ANON_KEY } }
    );
    if (!res.ok) return;
    var comments = await res.json();
    var list = document.getElementById('comments-list');
    if (!list) return;
    if (comments.length === 0) {
      list.innerHTML = '<p class="no-comments">No comments yet.</p>';
      return;
    }
    list.innerHTML = comments.map(function(c) {
      return '<div class="comment">' +
        '<div class="comment-header">' +
          '<strong>' + esc(c.name) + '</strong>' +
          '<span class="comment-date">' + new Date(c.created_at).toLocaleDateString() + '</span>' +
        '</div>' +
        '<p>' + esc(c.body) + '</p>' +
      '</div>';
    }).join('');
  }

  async function submitComment(e) {
    e.preventDefault();
    var nameInput = document.getElementById('comment-name');
    var bodyInput = document.getElementById('comment-body');
    var name = nameInput.value.trim();
    var body = bodyInput.value.trim();
    if (!name || !body) return;
    var btn = e.target.querySelector('button');
    btn.disabled = true;
    await fetch(SUPABASE_URL + '/rest/v1/comments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: SUPABASE_ANON_KEY,
        Prefer: 'return=representation'
      },
      body: JSON.stringify({ page: page, name: name, body: body })
    });
    nameInput.value = '';
    bodyInput.value = '';
    btn.disabled = false;
    loadComments();
  }

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('comment-form');
    if (form) {
      form.addEventListener('submit', submitComment);
      loadComments();
    }
  });
})();
