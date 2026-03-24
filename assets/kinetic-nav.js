/* =============================================
   Kinetic Strategy Consulting – Navigation JS
   Fallback for Squarespace burger & folder menus
   ============================================= */
(function () {
  'use strict';

  function init() {

    /* ── Burger / mobile overlay ─────────────── */
    var burger = document.querySelector('[data-test="header-burger"]');
    var overlay = document.querySelector('.header-menu-overlay');

    if (burger && overlay) {
      burger.addEventListener('click', function () {
        var isOpen = overlay.classList.contains('header-menu-overlay--open');
        if (isOpen) {
          overlay.classList.remove('header-menu-overlay--open');
          burger.setAttribute('aria-expanded', 'false');
          document.body.style.overflow = '';
        } else {
          overlay.classList.add('header-menu-overlay--open');
          burger.setAttribute('aria-expanded', 'true');
          document.body.style.overflow = 'hidden';
        }
      });
    }

    /* ── Desktop: folder dropdown on hover/focus ─ */
    var folderItems = document.querySelectorAll('.header-nav-item--folder');
    folderItems.forEach(function (item) {
      var btn = item.querySelector('.header-nav-folder-title');
      var content = item.querySelector('.header-nav-folder-content');
      if (!btn || !content) return;

      // Desktop hover
      item.addEventListener('mouseenter', function () {
        btn.setAttribute('aria-expanded', 'true');
      });
      item.addEventListener('mouseleave', function () {
        btn.setAttribute('aria-expanded', 'false');
      });

      // Keyboard / click (mobile overlay)
      btn.addEventListener('click', function (e) {
        var expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      });
    });

    /* ── Mobile overlay back buttons ────────────── */
    var backBtns = document.querySelectorAll('[data-test="header-back-btn"], .header-nav-folder-back');
    backBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var parentFolder = btn.closest('.header-nav-folder-content');
        if (parentFolder) {
          var folderTitle = parentFolder.previousElementSibling;
          if (folderTitle) folderTitle.setAttribute('aria-expanded', 'false');
        }
      });
    });

  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
