/* Shared behaviour for every page: scale-to-fit, reveal once rendered,
   animated page transitions, keyboard and swipe navigation. */
(function () {
  'use strict';
  var W = 1194, H = 834, DUR = 260;
  var de = document.documentElement;
  var leaving = false, revealed = false;

  function fit() {
    var d = document.getElementById('dc-root');
    if (!d) return;
    var vw = window.innerWidth, vh = window.innerHeight;
    var k = Math.min(vw / W, vh / H);
    d.style.transform = 'translate(' + Math.round((vw - W * k) / 2) + 'px,' + Math.round((vh - H * k) / 2) + 'px) scale(' + k + ')';
  }

  function reveal() {
    if (revealed) return;
    revealed = true;
    fit();
    try {
      var dir = sessionStorage.getItem('rl-dir');
      sessionStorage.removeItem('rl-dir');
      if (dir) de.setAttribute('data-dir', dir);
    } catch (e) {}
    de.classList.add('ready');
  }

  // Wait until the runtime has rendered the page and the font is ready, so the
  // first thing the reader sees is the finished page (no unstyled flash).
  function whenRendered() {
    var fontsReady = (document.fonts && document.fonts.load)
      ? Promise.race([document.fonts.load('600 20px "Baloo 2"'), new Promise(function (r) { setTimeout(r, 1500); })])
      : Promise.resolve();
    function check() {
      var d = document.getElementById('dc-root');
      if (d && d.firstElementChild) { fontsReady.then(function () { requestAnimationFrame(reveal); }); return true; }
      return false;
    }
    if (check()) return;
    var mo = new MutationObserver(function () { if (check()) mo.disconnect(); });
    mo.observe(document.body, { childList: true, subtree: true });
    setTimeout(function () { mo.disconnect(); reveal(); }, 4000); // never leave the reader on a blank screen
  }

  function labelHref(label) {
    var a = document.querySelector('a[aria-label="' + label + '"]');
    return a ? a.getAttribute('href') : null;
  }

  function go(href, dir) {
    if (!href || leaving) return;
    leaving = true;
    try { sessionStorage.setItem('rl-dir', dir); } catch (e) {}
    de.setAttribute('data-leave', dir);
    de.classList.add('leaving');
    setTimeout(function () { location.href = href; }, DUR);
  }
  function next() { go(labelHref('Página siguiente') || labelHref('Empezar el libro') || labelHref('Leer el libro otra vez'), 'next'); }
  function prev() { go(labelHref('Página anterior'), 'prev'); }

  // Intercept the in-page arrows so they animate too.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var href = a.getAttribute('href');
    if (!/^[\w-]+\.html$/.test(href)) return;
    e.preventDefault();
    go(href, a.getAttribute('aria-label') === 'Página anterior' ? 'prev' : 'next');
  }, true);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight' || e.key === 'PageDown') next();
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') prev();
  });

  var x0 = null, y0 = null;
  document.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
  document.addEventListener('touchend', function (e) {
    if (x0 == null) return;
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    x0 = null;
    if (Math.abs(dx) > 90 && Math.abs(dx) > Math.abs(dy) * 2) { if (dx < 0) next(); else prev(); }
  }, { passive: true });

  // Back/forward cache restores the page frozen in its "leaving" state: undo it.
  window.addEventListener('pageshow', function (e) {
    if (!e.persisted) return;
    leaving = false;
    de.classList.remove('leaving', 'ready');
    de.removeAttribute('data-leave');
    revealed = false;
    void de.offsetWidth;
    reveal();
  });

  window.addEventListener('resize', fit);
  window.addEventListener('orientationchange', function () { setTimeout(fit, 150); });

  var hint = document.createElement('div');
  hint.id = 'rot';
  hint.textContent = '↻ Gira el dispositivo para ver mejor';
  document.body.appendChild(hint);

  whenRendered();
})();
