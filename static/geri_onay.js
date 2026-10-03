/* ============================================================
   C-Peak · Geri onayı V4
   Sadece "ana sayfa"da (giriş sonrası ilk sayfa) geri basınca
   çıkış onayı gösterir. İç sayfalarda karışmaz.
   ============================================================ */
(function () {
  "use strict";
  
  // cpk: logged-out guard — oturum acmamis kullanicida hic calisma
  if (!document.getElementById('logoutModal')) {
    return;
  }
if (window.__cpeakGeriOnayV4) return;
  window.__cpeakGeriOnayV4 = true;

  function log() { /* production: sessiz */ }

  /* Login sayfasında devre dışı */
  if (document.body && document.body.classList.contains("login-page")) {
    log("login — devre dışı");
    return;
  }

  /* Eski versiyonların modal'larını temizle */
  ["cpeak-geri-onay", "cpeak-geri-onay-v2"].forEach(function (id) {
    var e = document.getElementById(id);
    if (e && e.parentNode) e.parentNode.removeChild(e);
  });

  var ENTRY_KEY = "cpeak_entry_path";
  var path = location.pathname;
  var entry = null;

  try { entry = sessionStorage.getItem(ENTRY_KEY); } catch (e) {}

  /* Referrer kontrolü: login/cikis'ten gelindiyse bu yeni giriş */
  var ref = document.referrer || "";
  var yeniGiris =
    ref.indexOf("/login") !== -1 ||
    ref.indexOf("/cikis") !== -1 ||
    ref.indexOf("/logout") !== -1 ||
    !entry;

  if (yeniGiris) {
    try { sessionStorage.setItem(ENTRY_KEY, path); } catch (e) {}
    entry = path;
    log("yeni giriş noktası:", path);
  }

  /* SADECE entry sayfasında guard kur */
  if (path !== entry) {
    log("iç sayfa — guard yok:", path);
    return;
  }

  log("ana sayfa — guard kurulacak:", path);

  /* ---------------- MODAL ---------------- */
  function modalBul() {
    return document.getElementById("logoutModal");
  }

  function goster() {
    var m = modalBul();
    if (!m) { log("logoutModal bulunamadı"); return false; }
    if (m.classList.contains("active")) return true;
    m.classList.add("active");
    log("modal açıldı");
    return true;
  }

  /* ---------------- HISTORY GUARD ---------------- */
  var guardli = false;

  function guard() {
    if (guardli) return;
    try {
      history.pushState({ cpeakGuard: Date.now() }, "", location.href);
      guardli = true;
    } catch (e) {
      log("guard hatası:", e);
    }
  }

  function guardBirak() {
    guardli = false;
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
    log("popstate yakalandı (ana sayfa)");
    /* Modal zaten açıksa dokunma */
    var m = modalBul();
    if (m && m.classList.contains("active")) {
      log("modal zaten açık");
      return;
    }
    /* Guard'ı yeniden kur ve modal'ı aç */
    guardBirak();
    guard();
    goster();
  });

  /* ---------------- MODAL KAPANINCA GUARD YENİLE ---------------- */
  function modalIzle() {
    var m = modalBul();
    if (!m) {
      setTimeout(modalIzle, 800);
      return;
    }
    var mo = new MutationObserver(function (muts) {
      muts.forEach(function (mut) {
        if (mut.attributeName !== "class") return;
        if (!m.classList.contains("active")) {
          log("modal kapandı → guard yenilendi");
          guardBirak();
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

  /* ---------------- LOGOUT → ENTRY TEMİZLE ---------------- */
  document.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var btn = t.closest('[data-logout], .logout-item, a[href*="/cikis"], a[href*="/logout"]');
    if (!btn) return;
    try { sessionStorage.removeItem(ENTRY_KEY); } catch (err) {}
    log("logout — entry temizlendi");
  }, true);

  /* Logout form submit */
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f || !f.action) return;
    if (f.action.indexOf("/cikis") !== -1 || f.action.indexOf("/logout") !== -1) {
      try { sessionStorage.removeItem(ENTRY_KEY); } catch (err) {}
      log("logout form — entry temizlendi");
    }
  }, true);

  /* ---------------- BFCACHE ---------------- */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      log("bfcache dönüşü");
      guardBirak();
      setTimeout(guard, 100);
    }
  });

  log("hazır (ana sayfa)");
})();
