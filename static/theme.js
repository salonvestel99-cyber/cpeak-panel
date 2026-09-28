/* =========================================================
   THEME — Koyu / Aydınlık Mod Toggle
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
    document.documentElement.setAttribute("data-theme", t);
  }

  // Başlangıç: kaydedilmiş tema varsa uygula
  var saved = get();
  if (saved) apply(saved);

  // Toggle butonlarını bağla
  document.addEventListener("DOMContentLoaded", function () {
    var btns = document.querySelectorAll("[data-theme-toggle]");
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        var cur = document.documentElement.getAttribute("data-theme") || "light";
        var next = cur === "light" ? "dark" : "light";
        apply(next);
        set(next);
      });
    });
  });

  // OS tercihini dinle (kullanıcı seçim yapmadıysa)
  if (!saved && window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.matches) apply("dark");
    // Değişirse otomatik uygula (kullanıcı manuel seçmediyse)
    var handler = function (e) {
      if (!get()) apply(e.matches ? "dark" : "light");
    };
    if (mq.addEventListener) mq.addEventListener("change", handler);
    else if (mq.addListener) mq.addListener(handler);
  }
})();
