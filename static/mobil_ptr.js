/* ============================================================
   C-Peak · PULL TO REFRESH
   Aşağı çekince sayfayı yeniler. Login'de çalışmaz.
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakPtrInit) return;
  window.__cpeakPtrInit = true;

  function isMobile() {
    return window.matchMedia && window.matchMedia("(max-width: 900px)").matches;
  }

  /* Login splash/form'da çalışmasın */
  function kapaliMi() {
    if (!isMobile()) return true;
    if (document.body.classList.contains("login-page")) return true;
    return false;
  }

  var THRESHOLD = 70;    /* yenileme eşiği (px) */
  var MAX_PULL  = 120;   /* en fazla esneme */
  var DAMPING   = 0.5;   /* sürtünme */

  var startY   = 0;
  var pulled   = 0;
  var tracking = false;
  var ptr      = null;

  function ptrOlustur() {
    if (ptr) return ptr;
    ptr = document.createElement("div");
    ptr.className = "mpro-ptr";
    ptr.setAttribute("aria-hidden", "true");
    ptr.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' +
      '<polyline points="6 9 12 15 18 9"/></svg>';
    document.body.appendChild(ptr);
    return ptr;
  }

  function scrollUstteMi() {
    var y = window.pageYOffset ||
            document.documentElement.scrollTop ||
            document.body.scrollTop || 0;
    return y <= 0;
  }

  function hedefiAtla(t) {
    if (!t || !t.closest) return false;
    /* Drawer / sheet / modal açık */
    if (document.body.classList.contains("mpro-drawer-open") ||
        document.body.classList.contains("mpro-sheet-open")) return true;
    if (t.closest(".mpro-drawer")) return true;
    if (t.closest(".modal:not([hidden])")) return true;
    /* Yatay scroll alanları */
    if (t.closest(".table-wrap, .admin-tabs, .bl-tabs, .mpro-tabbar")) return true;
    /* Input alanı */
    if (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT") return true;
    return false;
  }

  function sifirla() {
    document.body.classList.remove("mpro-ptr-visible", "mpro-ptr-ready");
    if (ptr) ptr.style.transform = "";
    var ic = ptr && ptr.querySelector("svg");
    if (ic) ic.style.transform = "";
    pulled = 0;
  }

  document.addEventListener("touchstart", function (e) {
    if (kapaliMi()) return;
    if (e.touches.length !== 1) { tracking = false; return; }
    if (!scrollUstteMi()) { tracking = false; return; }
    if (hedefiAtla(e.target)) { tracking = false; return; }
    startY = e.touches[0].clientY;
    pulled = 0;
    tracking = true;
  }, { passive: true });

  document.addEventListener("touchmove", function (e) {
    if (kapaliMi() || !tracking) return;
    var y = e.touches[0].clientY;
    var dy = y - startY;

    /* Yukarı kaydırıyor → iptal */
    if (dy <= 0) {
      tracking = false;
      sifirla();
      return;
    }

    /* Sayfa üstten uzaklaşmışsa iptal */
    if (!scrollUstteMi()) {
      tracking = false;
      sifirla();
      return;
    }

    ptrOlustur();

    pulled = Math.min(MAX_PULL, dy * DAMPING);

    if (pulled > 4) {
      document.body.classList.add("mpro-ptr-visible");
    }

    /* Gösterge konumu */
    var ty = Math.min(pulled, MAX_PULL * 0.9) - 40;
    if (ptr) ptr.style.transform =
      "translateX(-50%) translateY(" + ty + "px)";

    /* İkon dönüşü */
    var oran = Math.min(1, pulled / THRESHOLD);
    var ic = ptr && ptr.querySelector("svg");
    if (ic) ic.style.transform = "rotate(" + (oran * 180) + "deg)";

    if (pulled >= THRESHOLD) {
      document.body.classList.add("mpro-ptr-ready");
    } else {
      document.body.classList.remove("mpro-ptr-ready");
    }

    /* Sayfa scroll'unu engelle */
    if (e.cancelable) e.preventDefault();
  }, { passive: false });

  document.addEventListener("touchend", function () {
    if (!tracking) return;
    tracking = false;

    if (pulled >= THRESHOLD) {
      document.body.classList.add("mpro-ptr-loading");
      document.body.classList.remove("mpro-ptr-ready");
      if (ptr) {
        ptr.style.transform = "translateX(-50%) translateY(20px)";
      }
      /* Yenilemeden önce görsel feedback */
      setTimeout(function () {
        window.location.reload();
      }, 300);
    } else {
      sifirla();
    }
    pulled = 0;
  }, { passive: true });

  document.addEventListener("touchcancel", function () {
    if (!tracking) return;
    tracking = false;
    sifirla();
  }, { passive: true });

})();
