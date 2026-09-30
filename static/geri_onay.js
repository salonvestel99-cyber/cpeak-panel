/* ============================================================
   C-Peak · Geri tuşu çıkış onayı
   Panelde geri basınca uygulamadan çıkmak yerine
   "Çıkış yapmak istiyor musunuz?" modal'ı gösterir.
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakGeriOnay) return;
  window.__cpeakGeriOnay = true;

  /* Login sayfasında çalışmasın (kendi splash/form akışı var) */
  if (document.body.classList.contains("login-page")) return;

  var MODAL_ID = "cpeak-geri-onay";
  var bizimModal = null;
  var guardKurulu = false;

  /* ---------------- MODAL ---------------- */
  function mevcutModalAra() {
    var adaylar = [
      "#logoutModal", "#cikisModal",
      "#logout-modal", "#cikis-modal",
      ".logout-modal", ".cikis-modal",
      "[data-logout-modal]"
    ];
    for (var i = 0; i < adaylar.length; i++) {
      try {
        var m = document.querySelector(adaylar[i]);
        if (m) return m;
      } catch (e) {}
    }
    return null;
  }

  function kendiModalimiziOlustur() {
    if (bizimModal && bizimModal.parentNode) return bizimModal;

    bizimModal = document.createElement("div");
    bizimModal.id = MODAL_ID;
    bizimModal.className = "modal";
    bizimModal.setAttribute("hidden", "");
    bizimModal.setAttribute("role", "dialog");
    bizimModal.setAttribute("aria-modal", "true");
    bizimModal.innerHTML =
      '<div class="modal-card">' +
        '<div class="mpro-sheet-handle"></div>' +
        '<h3 style="margin:0 0 6px;' +
          'font-family:Fraunces,Georgia,serif;font-size:1.2rem;' +
          'font-weight:600;letter-spacing:-0.015em;' +
          'color:var(--ink,#18181b);">Çıkış yapmak istiyor musunuz?</h3>' +
        '<p style="margin:0 0 20px;font-size:.9rem;line-height:1.55;' +
          'color:var(--muted,#71717a);">' +
          'Devam ederseniz oturumunuz kapanacak ve giriş ekranına döneceksiniz.' +
        '</p>' +
        '<div style="display:flex;flex-direction:column;gap:10px;">' +
          '<button type="button" class="btn-primary" data-geri-karar="evet" ' +
            'style="width:100%;">Evet, Çıkış Yap</button>' +
          '<button type="button" class="btn-ghost" data-geri-karar="hayir" ' +
            'style="width:100%;">Vazgeç</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(bizimModal);
    return bizimModal;
  }

  function modalAl() {
    var m = mevcutModalAra();
    if (m) return { el: m, bizim: false };
    return { el: kendiModalimiziOlustur(), bizim: true };
  }

  function goster() {
    var r = modalAl();
    r.el.removeAttribute("hidden");
    document.body.classList.add("mpro-sheet-open");
    /* Focus yönetimi (erişilebilirlik) */
    setTimeout(function () {
      var btn = r.el.querySelector('[data-geri-karar="hayir"]') ||
                r.el.querySelector("button");
      if (btn) { try { btn.focus({ preventScroll: true }); } catch (e) {} }
    }, 60);
  }

  function gizle() {
    var r = modalAl();
    r.el.setAttribute("hidden", "");
    document.body.classList.remove("mpro-sheet-open");
  }

  /* ---------------- ÇIKIŞ ---------------- */
  function logoutUrlBul() {
    /* 1) data-logout işaretli */
    var el = document.querySelector("[data-logout]");
    if (el) {
      var u = el.getAttribute("href") || el.getAttribute("data-href");
      if (u) return u;
    }
    /* 2) href'inde logout/cikis geçen */
    var a = document.querySelector('a[href*="logout"], a[href*="cikis"]');
    if (a) return a.getAttribute("href");
    /* 3) fallback */
    return "/logout";
  }

  function cikisYap() {
    var url = logoutUrlBul();
    /* location.replace → logout URL'si history'ye eklenmez */
    window.location.replace(url);
  }

  /* ---------------- HISTORY GUARD ---------------- */
  function guardKur() {
    if (guardKurulu) return;
    try {
      history.pushState({ cpeakGuard: Date.now() }, "", location.href);
      guardKurulu = true;
    } catch (e) {
      guardKurulu = false;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      setTimeout(guardKur, 40);
    });
  } else {
    setTimeout(guardKur, 40);
  }

  window.addEventListener("popstate", function () {
    /* Geri basıldı → guard tekrar kur + onay modal'ı aç */
    guardKurulu = false;
    guardKur();
    goster();
  });

  /* ---------------- MODAL ETKİLEŞİM ---------------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("[data-geri-karar]");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();

    var karar = btn.getAttribute("data-geri-karar");
    if (karar === "evet") {
      gizle();
      cikisYap();
    } else {
      gizle();
    }
  }, true);

  /* Backdrop tıklaması → vazgeç */
  document.addEventListener("click", function (e) {
    var r = modalAl();
    if (!r.bizim) return;
    if (r.el.hasAttribute("hidden")) return;
    if (e.target === r.el) {
      gizle();
    }
  });

  /* ESC tuşu → vazgeç */
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var r = modalAl();
    if (r.el.hasAttribute("hidden")) return;
    gizle();
  });

})();
