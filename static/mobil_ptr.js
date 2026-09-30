/* ============================================================
   C-Peak · Pull to Refresh (v2 — passive, scroll'a karışmaz)
   - Tüm touch listener'lar { passive: true }
   - e.preventDefault() YOK
   - Sayfa scroll'u her zaman serbest
   - Acil durum: ?noptr=1 ile tamamen kapalı
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakPtrV2) return;
  window.__cpeakPtrV2 = true;

  /* Acil durum anahtarı */
  if (/[?&]noptr=1/.test(window.location.search)) return;
  if (window.__cpeakPtrInit) {
    /* Eski sürüm hala işaretli → çalışmasın */
    window.__cpeakPtrInit = false;
  }

  function isMobile() {
    return window.matchMedia && window.matchMedia("(max-width: 900px)").matches;
  }
  function kapaliMi() {
    if (!isMobile()) return true;
    if (document.body.classList.contains("login-page")) return true;
    return false;
  }

  var THRESHOLD = 80;
  var DAMPING   = 0.5;
  var MAX_PULL  = 140;

  var startY   = 0;
  var pulled   = 0;
  var tracking = false;
  var ptr      = null;

  function ptrOlustur() {
    if (ptr && ptr.parentNode) return ptr;
    var mevcut = document.querySelector(".mpro-ptr");
    if (mevcut) { ptr = mevcut; return ptr; }
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
    var el = document.scrollingElement || document.documentElement;
    var y1 = el ? el.scrollTop : 0;
    var y2 = window.pageYOffset || 0;
    var y3 = document.body.scrollTop || 0;
    return (y1 <= 0) && (y2 <= 0) && (y3 <= 0);
  }

  function hedefiAtla(t) {
    if (!t || !t.closest) return false;
    if (document.body.classList.contains("mpro-drawer-open") ||
        document.body.classList.contains("mpro-sheet-open")) return true;
    if (t.closest(".mpro-drawer")) return true;
    if (t.closest(".modal:not([hidden])")) return true;
    if (t.closest(".table-wrap, .admin-tabs, .bl-tabs, .mpro-tabbar")) return true;
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

  /* -------- TOUCHSTART (passive) -------- */
  document.addEventListener("touchstart", function (e) {
    if (kapaliMi()) return;
    if (e.touches.length !== 1) return;
    if (!scrollUstteMi()) return;
    if (hedefiAtla(e.target)) return;
    startY = e.touches[0].clientY;
    pulled = 0;
    tracking = true;
  }, { passive: true });

  /* -------- TOUCHMOVE (passive, preventDefault YOK) -------- */
  document.addEventListener("touchmove", function (e) {
    if (!tracking || kapaliMi()) return;

    /* Scroll başladıysa iptal */
    if (!scrollUstteMi()) {
      tracking = false;
      sifirla();
      return;
    }

    var y  = e.touches[0].clientY;
    var dy = y - startY;

    /* Yukarı = normal scroll, iptal */
    if (dy <= 0) {
      tracking = false;
      sifirla();
      return;
    }

    /* Sadece görsel gösterge — preventDefault YOK */
    ptrOlustur();
    pulled = Math.min(MAX_PULL, dy * DAMPING);

    if (pulled > 4) {
      document.body.classList.add("mpro-ptr-visible");
    }

    var ty = Math.min(pulled, MAX_PULL * 0.9) - 40;
    if (ptr) ptr.style.transform = "translateX(-50%) translateY(" + ty + "px)";

    var oran = Math.min(1, pulled / THRESHOLD);
    var ic = ptr && ptr.querySelector("svg");
    if (ic) ic.style.transform = "rotate(" + (oran * 180) + "deg)";

    if (pulled >= THRESHOLD) {
      document.body.classList.add("mpro-ptr-ready");
    } else {
      document.body.classList.remove("mpro-ptr-ready");
    }
  }, { passive: true });

  /* -------- TOUCHEND (passive) -------- */
  document.addEventListener("touchend", function () {
    if (!tracking) return;
    tracking = false;

    if (pulled >= THRESHOLD) {
      document.body.classList.add("mpro-ptr-loading");
      document.body.classList.remove("mpro-ptr-ready");
      if (ptr) ptr.style.transform = "translateX(-50%) translateY(20px)";
      setTimeout(function () {
        window.location.reload();
      }, 300);
    } else {
      sifirla();
    }
    pulled = 0;
  }, { passive: true });

  /* -------- TOUCHCANCEL (passive) -------- */
  document.addEventListener("touchcancel", function () {
    if (!tracking) return;
    tracking = false;
    sifirla();
  }, { passive: true });

})();
