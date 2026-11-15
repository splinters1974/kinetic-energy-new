/* Kinetic Energy Consulting: menu and contact form */
(function () {
  'use strict';

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
