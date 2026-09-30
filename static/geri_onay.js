/* ============================================================
   C-Peak · Geri onayı V3
   Geri tuşu → mevcut #logoutModal'ı açar.
   Dropdown ile birebir aynı modal.
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakGeriOnayV3) return;
  window.__cpeakGeriOnayV3 = true;

  function log() {
    try {
      var a = Array.prototype.slice.call(arguments);
      a.unshift("%c[GeriOnay]", "color:#f59e0b;font-weight:bold");
      console.log.apply(console, a);
    } catch (e) {}
  }

  /* Login sayfasında devre dışı */
  if (document.body && document.body.classList.contains("login-page")) {
    log("login sayfası — devre dışı");
    return;
  }

  log("V3 yüklendi");

  /* Eski V2 modal'ı varsa DOM'dan kaldır */
  var eski = document.getElementById("cpeak-geri-onay-v2");
  if (eski && eski.parentNode) eski.parentNode.removeChild(eski);
  eski = document.getElementById("cpeak-geri-onay");
  if (eski && eski.parentNode) eski.parentNode.removeChild(eski);

  /* ---------------- MODAL ---------------- */
  function modalBul() {
    return document.getElementById("logoutModal");
  }

  function goster() {
    var m = modalBul();
    if (!m) {
      log("logoutModal bulunamadı");
      return false;
    }
    /* Zaten açıksa tekrar açma */
    if (m.classList.contains("active")) {
      log("modal zaten açık");
      return true;
    }
    m.classList.add("active");
    log("modal açıldı (mevcut #logoutModal)");
    return true;
  }

  /* ---------------- HISTORY GUARD ---------------- */
  function guard() {
    try {
      history.pushState({ cpeakGuard: Date.now() }, "", location.href);
    } catch (e) {
      log("guard hatası:", e);
    }
  }

  function ilkGuard() {
    guard();
    setTimeout(guard, 300);
    setTimeout(guard, 1200);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ilkGuard);
  } else {
    ilkGuard();
  }

  /* ---------------- POPSTATE → GERİ ---------------- */
  window.addEventListener("popstate", function () {
    log("popstate yakalandı");
    guard();           /* guard'ı hemen yenile */
    goster();          /* mevcut modal'ı aç */
  });

  /* ---------------- MODAL KAPANINCA GUARD YENİLE ---------------- */
  function modalIzle() {
    var m = modalBul();
    if (!m) {
      log("modal izleme: logoutModal yok, 1sn sonra tekrar denenecek");
      setTimeout(modalIzle, 1000);
      return;
    }
    log("modal izleme başladı");
    var mo = new MutationObserver(function (muts) {
      muts.forEach(function (mut) {
        if (mut.attributeName !== "class") return;
        if (!m.classList.contains("active")) {
          /* Vazgeç / backdrop tıklaması → guard'ı yeniden kur */
          log("modal kapandı → guard yenilendi");
          guard();
        }
      });
    });
    mo.observe(m, { attributes: true, attributeFilter: ["class"] });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", modalIzle);
  } else {
    modalIzle();
  }

  /* ---------------- BFCACHE ---------------- */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      log("bfcache dönüşü");
      setTimeout(guard, 100);
    }
  });

  log("hazır");
})();
