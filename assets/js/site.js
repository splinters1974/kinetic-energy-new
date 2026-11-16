/* Kinetic Energy Consulting: menu and contact form */
(function () {
  'use strict';

  /* Always open a page at the top (or at the #section the link points to),
     rather than wherever the browser or the viewer was scrolled to before. */
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  function goToStart() {
    var target = location.hash ? document.getElementById(decodeURIComponent(location.hash.slice(1))) : null;
    if (target) { target.scrollIntoView({ block: 'start' }); return; }
    window.scrollTo(0, 0);
    try { document.body.scrollIntoView({ block: 'start' }); } catch (e) {}
  }
  goToStart();
  var moved = false;
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (ev) {
    window.addEventListener(ev, function () { moved = true; }, { once: true, passive: true });
  });
  window.addEventListener('load', function () { if (!moved) goToStart(); }, { once: true });

  /* Pick one of four zoom-and-pan moves for the hero, so pages don't all move the same way */
  var media = document.querySelector('.hero-media');
  if (media) {
    var h = 0, p = location.pathname;
    for (var i = 0; i < p.length; i++) h = (h * 31 + p.charCodeAt(i)) >>> 0;
    media.classList.add('kb-' + (h % 4 + 1));
  }

  var nav = document.querySelector('.site-nav');
  var toggle = document.querySelector('.nav-toggle');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  document.querySelectorAll('.nav-drop-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.parentElement;
      var open = !li.classList.contains('open');
      document.querySelectorAll('.nav-links > li.open').forEach(function (o) {
        if (o !== li) { o.classList.remove('open'); o.querySelector('.nav-drop-btn').setAttribute('aria-expanded', 'false'); }
      });
      li.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-links > li')) {
      document.querySelectorAll('.nav-links > li.open').forEach(function (o) { o.classList.remove('open'); });
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-links > li.open').forEach(function (o) { o.classList.remove('open'); });
      if (nav) nav.classList.remove('nav-open');
    }
  });

  /* Gentle reveal as sections scroll into view */
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.classList.add('js');
    var sel = '.section .head-row, .section-tight .head-row, .grid-3 > *, .grid-4 > *, .grid-2 > *, .split > *, .problems > div, .steps > .step, .areas > .area, .shots > *, .shot-wide, .case-cols > *, .compare-row, .tools > *, .founder > *, .contact-grid > *';
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in'); io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll(sel).forEach(function (el) {
      var i = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.classList.add('rv'); el.style.transitionDelay = Math.min(i, 3) * 70 + 'ms';
      io.observe(el);
    });
    /* Safety net: never leave content hidden */
    setTimeout(function () { document.querySelectorAll('.rv:not(.in)').forEach(function (el) {
      var r = el.getBoundingClientRect(); if (r.top < window.innerHeight) el.classList.add('in'); }); }, 1500);
  }

  /* Back to top button on long pages */
  var top = document.createElement('button');
  top.className = 'to-top'; top.type = 'button'; top.setAttribute('aria-label', 'Back to top'); top.textContent = '↑';
  document.body.appendChild(top);
  top.addEventListener('click', function () { window.scrollTo(0, 0); try { document.body.scrollIntoView({ block: 'start' }); } catch (e) {} });
  window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 900); }, { passive: true });

  /* Contact form: posts to Formspree without leaving the page */
  document.querySelectorAll('form[data-formspree]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    var btn = form.querySelector('button[type="submit"]');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (status) { status.className = 'form-status'; status.textContent = ''; }
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error('bad');
          form.reset();
          if (status) { status.className = 'form-status ok'; status.textContent = 'Thanks, your message is on its way. We will come back to you soon.'; }
        })
        .catch(function () {
          if (status) { status.className = 'form-status err'; status.innerHTML = 'Sorry, that did not send. Please email <a href="mailto:martynsheridan@gmail.com">martynsheridan@gmail.com</a> instead.'; }
        })
        .finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = 'Send message'; }
        });
    });
  });
})();
