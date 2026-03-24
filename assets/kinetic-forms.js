/* =============================================
   Kinetic Strategy Consulting – Formspree Handler
   Async form submission with status messages
   ============================================= */
(function () {
  'use strict';

  function handleForm(form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      e.stopPropagation();

      var btn = form.querySelector('.form-submit-btn');
      var successMsg = form.querySelector('.form-status--success');
      var errorMsg = form.querySelector('.form-status--error');

      // Hide previous messages
      if (successMsg) successMsg.style.display = 'none';
      if (errorMsg) errorMsg.style.display = 'none';

      // Disable button during submission
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Sending…';
      }

      try {
        var data = new FormData(form);
        var response = await fetch(form.action, {
          method: 'POST',
          body: data,
          headers: { 'Accept': 'application/json' }
        });

        if (response.ok) {
          form.reset();
          if (successMsg) successMsg.style.display = 'block';
          if (btn) {
            btn.disabled = false;
            btn.textContent = 'Send';
          }
        } else {
          var json = await response.json();
          if (errorMsg) {
            errorMsg.style.display = 'block';
          }
          if (btn) {
            btn.disabled = false;
            btn.textContent = 'Send';
          }
        }
      } catch (err) {
        if (errorMsg) errorMsg.style.display = 'block';
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Send';
        }
      }
    });
  }

  function init() {
    var forms = document.querySelectorAll('.kinetic-formspree');
    forms.forEach(handleForm);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
