/* ============================================================
   C-Peak · Geri onayı V2
   Geri tuşu → "Çıkış yapmak istiyor musunuz?" modal'ı
   Tüm stiller inline, hiçbir CSS'e bağımlı değil.
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakGeriOnayV2) return;
  window.__cpeakGeriOnayV2 = true;

  function log() {
    try {
      var a = Array.prototype.slice.call(arguments);
      a.unshift("%c[GeriOnay]", "color:#f59e0b;font-weight:bold");
      console.log.apply(console, a);
    } catch (e) {}
  }

  /* Login sayfasında devre dışı */
  function loginMi() {
    return document.body && document.body.classList.contains("login-page");
  }
  if (loginMi()) { log("login sayfası — devre dışı"); return; }

  log("V2 yüklendi");

  var MODAL_ID = "cpeak-geri-onay-v2";
  var ACIK = false;

  /* ---------------- MODAL ---------------- */
  function modalOlustur() {
    var m = document.getElementById(MODAL_ID);
    if (m) return m;

    m = document.createElement("div");
    m.id = MODAL_ID;
    m.setAttribute("role", "dialog");
    m.setAttribute("aria-modal", "true");
    m.style.cssText = [
      "position:fixed",
      "inset:0",
      "z-index:2147483600",
      "background:rgba(0,0,0,.55)",
      "display:none",
      "align-items:center",
      "justify-content:center",
      "padding:20px",
      "backdrop-filter:blur(6px)",
      "-webkit-backdrop-filter:blur(6px)",
      "opacity:0",
      "transition:opacity .22s ease",
      "font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    ].join(";");

    m.innerHTML =
      '<div class="cpeak-go-kart" style="' +
        'background:var(--surface,#ffffff);' +
        'color:var(--ink,#18181b);' +
        'border-radius:18px;' +
        'padding:26px 22px;' +
        'max-width:400px;' +
        'width:100%;' +
        'box-shadow:0 24px 60px rgba(0,0,0,.35);' +
        'transform:translateY(14px);' +
        'transition:transform .26s cubic-bezier(.22,.9,.28,1);' +
        'border:1px solid rgba(0,0,0,.06);' +
        '">' +
        '<div style="width:40px;height:4px;background:rgba(0,0,0,.14);' +
          'border-radius:4px;margin:0 auto 14px;"></div>' +
        '<h3 style="margin:0 0 8px;' +
          "font-family:'Fraunces',Georgia,serif;" +
          'font-size:1.22rem;font-weight:600;' +
          'letter-spacing:-0.015em;line-height:1.25;">' +
          'Çıkış yapmak istiyor musunuz?' +
        '</h3>' +
        '<p style="margin:0 0 22px;font-size:.9rem;line-height:1.55;' +
          'color:#71717a;">' +
          'Devam ederseniz oturumunuz kapanacak ve giriş ekranına döneceksiniz.' +
        '</p>' +
        '<div style="display:flex;flex-direction:column;gap:10px;">' +
          '<button type="button" data-go-karar="hayir" style="' +
            'width:100%;padding:14px 18px;border-radius:12px;' +
            'background:#18181b;color:#fff;border:none;' +
            'font-family:inherit;font-size:.98rem;font-weight:600;' +
            'cursor:pointer;-webkit-tap-highlight-color:transparent;' +
            'transition:transform .12s ease;' +
          '">Vazgeç</button>' +
          '<button type="button" data-go-karar="evet" style="' +
            'width:100%;padding:14px 18px;border-radius:12px;' +
            'background:transparent;color:#dc2626;' +
            'border:1px solid rgba(220,38,38,.32);' +
            'font-family:inherit;font-size:.98rem;font-weight:600;' +
            'cursor:pointer;-webkit-tap-highlight-color:transparent;' +
            'transition:transform .12s ease;' +
          '">Evet, Çıkış Yap</button>' +
        '</div>' +
      '</div>';

    document.body.appendChild(m);

    /* Butonlar */
    m.addEventListener("click", function (e) {
      var btn = e.target.closest && e.target.closest("[data-go-karar]");
      if (btn) {
        e.preventDefault();
        var karar = btn.getAttribute("data-go-karar");
        log("karar:", karar);
        if (karar === "evet") {
          gizle();
          var url = "/logout";
          var a = document.querySelector('[data-logout], a[href*="logout"], a[href*="cikis"]');
          if (a) {
            var u = a.getAttribute("href") || a.getAttribute("data-href");
            if (u) url = u;
          }
          log("çıkış →", url);
          window.location.replace(url);
        } else {
          gizle();
        }
        return;
      }
      /* Backdrop tıklaması */
      if (e.target === m) {
        gizle();
      }
    });

    /* ESC */
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && ACIK) gizle();
    });

    return m;
  }

  function goster() {
    var m = modalOlustur();
    m.style.display = "flex";
    ACIK = true;
    /* Animasyon için küçük gecikme */
    requestAnimationFrame(function () {
      m.style.opacity = "1";
      var k = m.querySelector(".cpeak-go-kart");
      if (k) k.style.transform = "translateY(0)";
    });
    log("modal açıldı");
  }

  function gizle() {
    var m = document.getElementById(MODAL_ID);
    if (!m) return;
    ACIK = false;
    m.style.opacity = "0";
    var k = m.querySelector(".cpeak-go-kart");
    if (k) k.style.transform = "translateY(14px)";
    setTimeout(function () {
      if (!ACIK) m.style.display = "none";
    }, 240);
    log("modal kapandı");
  }

  /* ---------------- HISTORY GUARD ---------------- */
  function guard() {
    try {
      history.pushState({ cpeakGuard: Date.now() }, "", location.href);
      log("guard kuruldu →", location.pathname);
    } catch (e) {
      log("guard hatası:", e);
    }
  }

  /* İlk guard: DOM hazır olduğunda + biraz gecikmeyle */
  function ilkGuard() {
    guard();
    /* Bazı tarayıcılarda login redirect sonrası gecikmeli gerekir */
    setTimeout(guard, 300);
    setTimeout(guard, 1200);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ilkGuard);
  } else {
    ilkGuard();
  }

  /* ---------------- POPSTATE ---------------- */
  window.addEventListener("popstate", function (e) {
    log("popstate yakalandı");
    /* Hemen guard'ı yeniden kur → tekrar geri basılırsa yine yakalanır */
    guard();
    /* Modal açıkken tekrar açma */
    if (ACIK) return;
    goster();
  });

  /* ---------------- BFCACHE ---------------- */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      log("bfcache'ten dönüş");
      /* Modal açıksa gizle (sayfa yeniden yüklendi) */
      if (ACIK) gizle();
      /* Guard'ı yeniden kur */
      setTimeout(guard, 100);
    }
  });

  log("hazır");
})();
