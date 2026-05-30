function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}
function toggleCategory(header) {
  header.classList.toggle('active');
  header.querySelector('.arrow').classList.toggle('open');
  header.nextElementSibling.classList.toggle('open');
}
function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  var b = document.body.classList.contains('dark-mode');
  localStorage.setItem('theme', b ? 'dark' : 'light');
  document.querySelector('.theme-toggle').textContent = b ? '\u{1F319}' : '\u2600\uFE0F';
}
(function() {
  var btn = document.querySelector('.theme-toggle');
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    if (btn) btn.textContent = '\u{1F319}';
  }
})();
