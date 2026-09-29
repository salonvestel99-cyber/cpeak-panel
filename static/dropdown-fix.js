/* ============================================================
   Dropdown Duzeltmesi
   - Toggle butonuna basinca: acik ise kapat, kapali ise ac
   - Bos yere tiklayinca: kapat
   - ESC tusu: kapat
   Mevcut toggle kodunu override eder.
   ============================================================ */
(function () {
  'use strict';

  var TOGGLE_SEL = [
    '[data-dropdown-toggle]',
    '[data-toggle="dropdown"]',
    '[data-bs-toggle="dropdown"]',
    '.dropdown-toggle',
    '.user-menu-toggle',
    '.profile-toggle',
    '.menu-toggle',
    '[aria-haspopup="true"]'
  ].join(',');

  var MENU_SEL = [
    '[data-dropdown]',
    '.dropdown-menu',
    '.user-menu',
    '.profile-menu',
    '.menu-dropdown',
    '.menu-panel'
  ].join(',');

  function menuBul(btn) {
    var id = btn.getAttribute('aria-controls');
    if (id) {
      var m = document.getElementById(id);
      if (m) return m;
    }
    var target = btn.getAttribute('data-target') || btn.getAttribute('data-bs-target');
    if (target) {
      try { var m2 = document.querySelector(target); if (m2) return m2; } catch (e) {}
    }
    if (btn.parentElement) {
      var m3 = btn.parentElement.querySelector(MENU_SEL);
      if (m3) return m3;
    }
    if (btn.nextElementSibling && btn.nextElementSibling.matches &&
        btn.nextElementSibling.matches(MENU_SEL)) {
      return btn.nextElementSibling;
    }
    return null;
  }

  function acikMi(menu) {
    if (!menu) return false;
    return menu.classList.contains('show') ||
           menu.classList.contains('open') ||
           menu.classList.contains('active') ||
           menu.classList.contains('visible') ||
           menu.style.display === 'block';
  }

  function ac(menu, btn) {
    menu.classList.add('show');
    if (btn) btn.setAttribute('aria-expanded', 'true');
  }

  function kapat(menu, btn) {
    menu.classList.remove('show', 'open', 'active', 'visible');
    if (menu.style.display === 'block') menu.style.display = '';
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }

  function hepsiniKapat(haric) {
    document.querySelectorAll(MENU_SEL).forEach(function (m) {
      if (m === haric) return;
      if (acikMi(m)) kapat(m);
    });
  }

  /* Toggle butonlari - capture phase'de mevcut kodu blokla */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest(TOGGLE_SEL);
    if (!btn) return;
    var menu = menuBul(btn);
    if (!menu) return;

    e.stopImmediatePropagation();
    e.preventDefault();

    if (acikMi(menu)) {
      kapat(menu, btn);
    } else {
      hepsiniKapat(menu);
      ac(menu, btn);
    }
  }, true);

  /* Disina tiklayinca kapat */
  document.addEventListener('click', function (e) {
    var icerde = e.target.closest &&
                 e.target.closest(TOGGLE_SEL + ',' + MENU_SEL);
    if (iceride) return;
    hepsiniKapat(null);
  });

  /* ESC ile kapat */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.keyCode === 27) {
      hepsiniKapat(null);
    }
  });
})();
