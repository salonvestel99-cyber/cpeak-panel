/* ============================================================
   C-Peak · UX FIX v1
   1) Toast / alert otomatik kaybolur
   2) Logout link'leri history'yi kirletmez (location.replace)
   3) bfcache geri dönüşünde sayfa yenilenir
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakUxFix) return;
  window.__cpeakUxFix = true;

  /* ========================================================
     1) TOAST / ALERT — OTOMATİK KAYBOLMA
     ======================================================== */
  var TOAST_SEC = {
    ".toast": 4,
    "[data-toast]": 4,
    ".mpro-toast": 4,
    ".uyari-toast": 5,
    ".flash-mesaj": 5,
    ".flash": 5,
    ".bildirim-toast": 5
    /* .alert'lere dokunmuyoruz — bazıları kalıcı olabilir */
  };

  function kaldir(el, ms) {
    if (!el || el.__uxAuto) return;
    el.__uxAuto = true;
    /* İçinde kapatma butonu varsa süreyi uzatma — yine kaldıracağız */
    setTimeout(function () {
      if (!el.parentNode) return;
      el.style.transition = "opacity .34s ease, transform .34s ease";
      el.style.opacity = "0";
      el.style.transform = "translateY(-8px)";
      setTimeout(function () {
        if (el.parentNode) el.parentNode.removeChild(el);
      }, 360);
    }, ms);
  }

  function tara(kok) {
    if (!kok) return;
    if (kok.nodeType === 1) {
      for (var sel in TOAST_SEC) {
        try {
          if (kok.matches && kok.matches(sel)) kaldir(kok, TOAST_SEC[sel] * 1000);
        } catch (e) {}
      }
    }
    if (!kok.querySelectorAll) return;
    for (var sel2 in TOAST_SEC) {
      try {
        var bulunanlar = kok.querySelectorAll(sel2);
        for (var i = 0; i < bulunanlar.length; i++) {
          kaldir(bulunanlar[i], TOAST_SEC[sel2] * 1000);
        }
      } catch (e) {}
    }
  }

  function observerBaslat() {
    var mo = new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        for (var i = 0; i < m.addedNodes.length; i++) {
          tara(m.addedNodes[i]);
        }
      });
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      tara(document.body);
      observerBaslat();
    });
  } else {
    tara(document.body);
    observerBaslat();
  }

  /* ========================================================
     2) LOGOUT — HISTORY KİRLETMESİN
     ======================================================== */
  function logoutMu(el) {
    if (!el || !el.getAttribute) return false;

    /* data-logout özniteliği → kesin logout */
    if (el.hasAttribute && el.hasAttribute("data-logout")) return true;

    var href = (el.getAttribute("href") || "").toLowerCase();
    var id = (el.id || "").toLowerCase();
    var cls = (el.className || "").toString().toLowerCase();
    var txt = (el.textContent || "").toLowerCase().trim();

    if (href.indexOf("/logout") !== -1) return true;
    if (href.indexOf("/cikis") !== -1) return true;
    if (id.indexOf("logout") !== -1) return true;
    if (id.indexOf("cikis") !== -1) return true;
    if (cls.indexOf("logout") !== -1) return true;
    if (cls.indexOf("cikis") !== -1) return true;
    if (txt === "çıkış yap" || txt === "cikis yap" ||
        txt === "çıkış"    || txt === "cikis") return true;
    return false;
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("a, button");
    if (!el) return;
    if (!logoutMu(el)) return;

    /* Form submit butonu ise (POST logout) → history'ye zaten eklenmez */
    if (el.tagName === "BUTTON" && el.form) return;

    var href = el.getAttribute("href");
    if (!href || href === "#") return;

    e.preventDefault();
    e.stopPropagation();

    /* location.replace → logout URL'si history'ye eklenmez */
    window.location.replace(href);
  }, true);

  /* ========================================================
     3) BFCACHE — GERİ TUŞUYLA DÖNÜŞTE YENİLE
     ======================================================== */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      /* Sayfa tarayıcı cache'inden geldi → session eskimiş olabilir */
      window.location.reload();
    }
  });

})();
