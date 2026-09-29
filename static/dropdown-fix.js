/* ============================================================
   Dropdown Fix - Mobil + Masaustu Toggle Destegi
   - Ayni butona basinca: ac/kapat
   - Disari tiklayinca: kapat
   - ESC tusu: kapat
   - Mobilde touchstart + click cift tetiklenme korumasi
   ============================================================ */
(function () {
  "use strict";

  var TOGGLE_SEL = [
    ".ud-t",                        // base.html kullanici dropdown
    "[data-dropdown-toggle]",
    "[data-toggle=\"dropdown\"]",
    "[data-bs-toggle=\"dropdown\"]",
    ".dropdown-toggle",
    ".user-menu-toggle",
    ".profile-toggle",
    "[aria-haspopup=\"true\"]"
  ].join(",");

  var MENU_SEL = [
    ".ud-m",                        // base.html kullanici dropdown menu
    "[data-dropdown]",
    ".dropdown-menu",
    ".user-menu",
    ".profile-menu",
    ".menu-dropdown",
    ".menu-panel"
  ].join(",");

  function menuBul(btn) {
    if (btn.parentElement) {
      var m = btn.parentElement.querySelector(MENU_SEL);
      if (m) return m;
    }
    var id = btn.getAttribute("aria-controls");
    if (id) {
      var m2 = document.getElementById(id);
      if (m2) return m2;
    }
    var t = btn.getAttribute("data-target") || btn.getAttribute("data-bs-target");
    if (t) {
      try { var m3 = document.querySelector(t); if (m3) return m3; } catch (e) {}
    }
    if (btn.nextElementSibling && btn.nextElementSibling.matches && btn.nextElementSibling.matches(MENU_SEL)) {
      return btn.nextElementSibling;
    }
    return null;
  }

  function acikMi(m) {
    if (!m) return false;
    return m.classList.contains("show") ||
           m.classList.contains("open") ||
           m.classList.contains("active") ||
           m.classList.contains("visible") ||
           m.style.display === "block";
  }

  function ac(m, b) {
    m.classList.add("show");
    if (b) b.setAttribute("aria-expanded", "true");
  }

  function kapat(m, b) {
    m.classList.remove("show", "open", "active", "visible");
    if (m.style.display === "block") m.style.display = "";
    if (b) b.setAttribute("aria-expanded", "false");
  }

  function hepsiniKapat(haric) {
    document.querySelectorAll(MENU_SEL).forEach(function (m) {
      if (m === haric) return;
      if (acikMi(m)) kapat(m);
    });
  }

  // Touch ve click cift tetiklenmesini engelle
  var sonTouch = 0;

  function toggleHandler(e) {
    var btn = e.target.closest && e.target.closest(TOGGLE_SEL);
    if (!btn) return;
    var menu = menuBul(btn);
    if (!menu) return;

    e.stopImmediatePropagation();
    if (e.cancelable) e.preventDefault();

    if (acikMi(menu)) {
      kapat(menu, btn);
    } else {
      hepsiniKapat(menu);
      ac(menu, btn);
    }
  }

  // Touch (mobil)
  document.addEventListener("touchstart", function (e) {
    sonTouch = Date.now();
    toggleHandler(e);
  }, { passive: false, capture: true });

  // Click (masaustu + touch sonrasi)
  document.addEventListener("click", function (e) {
    // touch'tan hemen sonra geldiyse atla (cift tetikleme)
    if (Date.now() - sonTouch < 350) return;
    toggleHandler(e);
  }, true);

  // Disina tiklayinca kapat
  function disTikla(e) {
    var icerde = e.target.closest && e.target.closest(TOGGLE_SEL + "," + MENU_SEL);
    if (iceride) return;
    hepsiniKapat(null);
  }
  document.addEventListener("touchstart", disTikla, { passive: true });
  document.addEventListener("click", disTikla);

  // ESC
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" || e.keyCode === 27) hepsiniKapat(null);
  });
})();
