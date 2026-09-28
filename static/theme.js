/* =========================================================
   THEME - Koyu / Aydinlik Mod Toggle (tek anahtar: cpeak_theme)
   ========================================================= */
(function () {
  "use strict";

  var KEY = "cpeak_theme";

  function get() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function set(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }
  function apply(t) {
    var h = document.documentElement;
    h.setAttribute("data-theme", t);
    h.classList.toggle("dark", t === "dark");
    // Diger bilesenlere haber ver
    try {
      window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: t } }));
    } catch (e) {}
  }

  // Baslangic: kaydedilmis tema varsa uygula, yoksa OS tercihine bak
  var saved = get();
  if (saved) {
    apply(saved);
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    apply("dark");
  }

  // Tum toggle butonlarini bagla (tek sefer, capture phase ile)
  function bagla() {
    var btns = document.querySelectorAll("[data-theme-toggle], #udThemeToggle");
    btns.forEach(function (b) {
      if (b.__temaBagli) return;
      b.__temaBagli = true;
      b.addEventListener("click", function (e) {
        e.stopImmediatePropagation();
        e.preventDefault();
        var h = document.documentElement;
        var cur = h.getAttribute("data-theme")
                  || (h.classList.contains("dark") ? "dark" : "light");
        var next = cur === "light" ? "dark" : "light";
        apply(next);
        set(next);
      }, true);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bagla);
  } else {
    bagla();
  }
  // Bazi butonlar sonradan olusabilir
  setTimeout(bagla, 300);
  setTimeout(bagla, 1200);

  // OS tercihini dinle (kullanici manuel secim yapmadiysa)
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var handler = function (e) {
      if (!get()) apply(e.matches ? "dark" : "light");
    };
    if (mq.addEventListener) mq.addEventListener("change", handler);
    else if (mq.addListener) mq.addListener(handler);
  }
})();
