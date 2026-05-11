/* ParkEase main.js */

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('mainContent');
  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('open');
  } else {
    const collapsed = sidebar.style.width === '60px';
    sidebar.style.width = collapsed ? '240px' : '60px';
    main.style.marginLeft = collapsed ? '240px' : '60px';
    sidebar.querySelectorAll('.brand-text,.nav-section,.user-info,.logout-btn span,.sidebar-nav li .nav-link span')
      .forEach(el => el.style.display = collapsed ? '' : 'none');
  }
}

// Live clock
function updateClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-UG', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
}
setInterval(updateClock, 1000);
updateClock();

// Auto-dismiss alerts after 5s
setTimeout(() => {
  document.querySelectorAll('.alert.alert-dismissible').forEach(a => {
    try { bootstrap.Alert.getOrCreateInstance(a).close(); } catch(e) {}
  });
}, 5000);

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(e) {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
    if (!sidebar.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
      sidebar.classList.remove('open');
    }
  }
});
