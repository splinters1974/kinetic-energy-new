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

  /* ── Squarespace image loader replacement ────────
     site-bundle.js relied on Static.SQUARESPACE_CONTEXT
     to reveal lazy images. We replace that here by:
     1. Copying data-src → src where src is missing/blank
     2. Setting CSS variables Squarespace normally injects
        (focal point, object-fit) so images display correctly
     3. Marking every sqs-managed image as loaded so the
        Squarespace CSS unhides them (data-load="true")
     4. Using IntersectionObserver to do this lazily where
        possible, falling back to eager load otherwise.
  ─────────────────────────────────────────────────── */
  function loadSqsImages() {
    var images = document.querySelectorAll('img[data-loader="sqs"], img[data-load="false"]');

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            revealImage(entry.target);
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '400px' });

      images.forEach(function (img) { observer.observe(img); });
    } else {
      images.forEach(revealImage);
    }
  }

  function revealImage(img) {
    var dataSrc = img.getAttribute('data-src');
    if (dataSrc && (!img.src || img.src === window.location.href)) {
      img.src = dataSrc;
    }
    // Set CSS variables that Squarespace JS normally injects so images
    // using object-position/object-fit CSS vars display correctly
    var focalPoint = img.getAttribute('data-image-focal-point');
    if (focalPoint && focalPoint !== ',') {
      var parts = focalPoint.split(',');
      var x = Math.round(parseFloat(parts[0]) * 100) + '%';
      var y = Math.round(parseFloat(parts[1]) * 100) + '%';
      img.style.setProperty('--image-component-focal-point', x + ' ' + y);
    } else {
      img.style.setProperty('--image-component-focal-point', '50% 50%');
    }
    img.style.setProperty('--image-component-object-fit', 'cover');
    img.setAttribute('data-load', 'true');
  }

  /* ── Squarespace native video background replacement ──
     Squarespace's JS would create a <video> element inside
     .sqs-video-background-native__video-player using the
     alexandriaUrl from the data-config-native-video JSON.
     We instead use the locally hosted video file.
  ─────────────────────────────────────────────────── */
  function initVideoBackgrounds() {
    var players = document.querySelectorAll('.sqs-video-background-native');
    players.forEach(function (container) {
      var playerDiv = container.querySelector('.sqs-video-background-native__video-player');
      if (!playerDiv) return;

      // Get the filename from the config JSON embedded in the data attribute
      var configRaw = container.getAttribute('data-config-native-video');
      if (!configRaw) return;
      try {
        var config = JSON.parse(configRaw.replace(/&quot;/g, '"'));
        var filename = config.filename;
        if (!filename) return;
        var src = '/assets/videos/' + filename;

        var video = document.createElement('video');
        video.setAttribute('autoplay', '');
        video.setAttribute('muted', '');
        video.setAttribute('loop', '');
        video.setAttribute('playsinline', '');
        video.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;pointer-events:none;';
        var source = document.createElement('source');
        source.src = src;
        source.type = 'video/mp4';
        video.appendChild(source);
        playerDiv.appendChild(video);
        video.play().catch(function () {});
      } catch (e) {}
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      init();
      loadSqsImages();
      initVideoBackgrounds();
    });
  } else {
    init();
    loadSqsImages();
    initVideoBackgrounds();
  }

})();
