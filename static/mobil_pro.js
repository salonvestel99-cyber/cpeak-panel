/* ============================================================
   C-Peak · MOBİL PRO KATMANI v1
   Hamburger drawer, bottom tab bar, bottom sheet, loading,
   klavye yönetimi, tablo kart dönüşümü.
   Masaüstünde: hepsi erken çıkar (isMobile() guard).
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakMProInit) return;
  window.__cpeakMProInit = true;

  /* ---------- yardımcılar ---------- */
  function isMobile() {
    return window.matchMedia && window.matchMedia("(max-width: 900px)").matches;
  }

  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "class") e.className = attrs[k];
      else if (k === "html") e.innerHTML = attrs[k];
      else if (k === "text") e.textContent = attrs[k];
      else if (k.indexOf("on") === 0 && typeof attrs[k] === "function")
        e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    }
    if (children) children.forEach(function (c) { if (c) e.appendChild(c); });
    return e;
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function svgIcon(name) {
    var icons = {
      menu:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="3" y1="7" x2="21" y2="7"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="17" x2="21" y2="17"/></svg>',
      home:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></svg>',
      book:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h11a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3V4z"/><path d="M4 4v13a3 3 0 0 0 3 3h11"/></svg>',
      calendar:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="8" y1="3" x2="8" y2="7"/><line x1="16" y1="3" x2="16" y2="7"/></svg>',
      bell:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>',
      user:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/></svg>',
      logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
      mail:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="3 7 12 13 21 7"/></svg>',
      panel:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>'
    };
    return icons[name] || icons.panel;
  }

  /* Bağlantıya uygun ikon seç */
  function ikonSec(href, text) {
    var h = (href || "").toLowerCase();
    var t = (text || "").toLowerCase();
    if (h.indexOf("dashboard") !== -1 || t.indexOf("panel") !== -1) return "home";
    if (h.indexOf("odev") !== -1 || t.indexOf("ödev") !== -1) return "book";
    if (h.indexOf("program") !== -1 || t.indexOf("program") !== -1) return "calendar";
    if (h.indexOf("bildirim") !== -1 || t.indexOf("bildirim") !== -1) return "bell";
    if (h.indexOf("mail") !== -1 || t.indexOf("mail") !== -1) return "mail";
    if (h.indexOf("logout") !== -1 || t.indexOf("çıkış") !== -1) return "logout";
    return "panel";
  }

  /* ========================================================
     1) HAMBURGER + DRAWER
     ======================================================== */
  function drawerKur() {
    var nav = document.querySelector(".topbar-nav");
    var inner = document.querySelector(".topbar-inner");
    if (!nav || !inner) return;   /* login gibi sayfalarda yok */
    document.body.classList.add("mpro-has-nav");

    /* Hamburger */
    if (!document.querySelector(".mpro-hamburger")) {
      var hb = el("button", {
        class: "mpro-hamburger",
        "aria-label": "Menüyü aç",
        type: "button",
        html: svgIcon("menu")
      });
      hb.addEventListener("click", function (e) {
        e.preventDefault();
        document.body.classList.toggle("mpro-drawer-open");
      });
      inner.insertBefore(hb, inner.firstChild);
    }

    /* Backdrop */
    if (!document.querySelector(".mpro-backdrop")) {
      var bd = el("div", { class: "mpro-backdrop" });
      bd.addEventListener("click", function () {
        document.body.classList.remove("mpro-drawer-open");
        document.body.classList.remove("mpro-sheet-open");
      });
      document.body.appendChild(bd);
    }

    /* Drawer */
    if (!document.querySelector(".mpro-drawer")) {
      var dr = el("aside", { class: "mpro-drawer", role: "navigation" });

      /* Başlık: marka */
      var head = el("div", { class: "mpro-drawer-head" }, [
        el("img", { src: "/static/logochrome.png", alt: "C-Peak" }),
        el("span", { class: "mpro-drawer-title", html: "C-Peak<span class=\"mpro-drawer-sub\">English</span>" })
      ]);
      dr.appendChild(head);

      /* Nav linkleri */
      var links = nav.querySelectorAll("a, button");
      links.forEach(function (a) {
        if (a.classList.contains("topbar-brand")) return;
        var copy = el("a", {
          href: a.getAttribute("href") || "#",
          class: a.className && a.className.indexOf("active") !== -1 ? "mpro-active" : ""
        });
        var ik = ikonSec(a.getAttribute("href") || "", a.textContent || "");
        copy.innerHTML = svgIcon(ik) + "<span>" + escapeHtml((a.textContent || "").trim()) + "</span>";
        if (a.tagName === "BUTTON") {
          copy = el("button", { class: "mpro-drawer-item", type: "button" });
          copy.innerHTML = svgIcon(ik) + "<span>" + escapeHtml((a.textContent || "").trim()) + "</span>";
          copy.addEventListener("click", function () { a.click(); });
        }
        dr.appendChild(copy);
      });

      /* Ayraç + çıkış */
      dr.appendChild(el("div", { class: "mpro-drawer-sep" }));
      var cikis = nav.querySelector("[data-logout], [href*='logout'], [href*='cikis']");
      if (cikis) {
        var c = el("a", { href: cikis.getAttribute("href") || "#", class: "mpro-drawer-item" });
        c.innerHTML = svgIcon("logout") + "<span>Çıkış Yap</span>";
        dr.appendChild(c);
      }

      document.body.appendChild(dr);
    }
  }

  /* ========================================================
     2) BOTTOM TAB BAR
     ======================================================== */
  function tabbarKur() {
    var nav = document.querySelector(".topbar-nav");
    if (!nav) return;
    var links = Array.from(nav.querySelectorAll("a")).filter(function (a) {
      return a.getAttribute("href") && a.getAttribute("href") !== "#";
    });
    /* En fazla 4 link al */
    if (!links.length) return;
    var secili = links.slice(0, 4);

    /* Zaten var mı? */
    if (document.querySelector(".mpro-tabbar")) {
      document.body.classList.add("mpro-has-tab");
      return;
    }

    var cur = (location.pathname || "/").replace(/\/$/, "");
    var tb = el("nav", { class: "mpro-tabbar", role: "navigation" });
    var inner = el("div", { class: "mpro-tabbar-inner" });

    secili.forEach(function (a) {
      var href = a.getAttribute("href");
      var text = (a.textContent || "").trim();
      var ik = ikonSec(href, text);
      var aktif = href && href !== "#" && (cur === href.replace(/\/$/, "") ||
                                          cur.indexOf(href.replace(/\/$/, "")) === 0);
      var tab = el("a", {
        href: href,
        class: "mpro-tab" + (aktif && text ? " mpro-active" : ""),
        html: svgIcon(ik) + "<span>" + text + "</span>"
      });
      inner.appendChild(tab);
    });

    tb.appendChild(inner);
    document.body.appendChild(tb);
    document.body.classList.add("mpro-has-tab");
  }

  /* ========================================================
     3) MODAL → BOTTOM SHEET
     ======================================================== */
  function sheetKur() {
    var modals = document.querySelectorAll(".modal");
    if (!modals.length) return;
    modals.forEach(function (m) {
      var card = m.querySelector(".modal-card");
      if (!card) return;
      if (!card.querySelector(".mpro-sheet-handle")) {
        var h = el("div", { class: "mpro-sheet-handle" });
        card.insertBefore(h, card.firstChild);
      }
    });

    /* hidden değişimini izle → body.mpro-sheet-open toggle */
    var mo = new MutationObserver(function () {
      var acik = false;
      modals.forEach(function (m) {
        if (!m.hasAttribute("hidden")) acik = true;
      });
      document.body.classList.toggle("mpro-sheet-open", acik);
    });
    modals.forEach(function (m) {
      mo.observe(m, { attributes: true, attributeFilter: ["hidden"] });
    });
  }

  /* ========================================================
     4) TABLO → KART (otomatik data-mpro-card)
     ======================================================== */
  function tabloKur() {
    var tablolar = document.querySelectorAll(".table-wrap table, .table");
    tablolar.forEach(function (t) {
      if (t.hasAttribute("data-mpro-card")) return;
      var basliklar = Array.from(t.querySelectorAll("thead th")).map(function (th) {
        return (th.textContent || "").trim();
      });
      if (!basliklar.length) return;
      /* Çok küçük tablolar (1-2 sütun) karta gerek yok */
      if (basliklar.length <= 2) return;

      t.setAttribute("data-mpro-card", "1");
      var satirlar = t.querySelectorAll("tbody tr");
      satirlar.forEach(function (tr) {
        var tds = tr.querySelectorAll("td");
        tds.forEach(function (td, i) {
          if (!td.hasAttribute("data-label") && basliklar[i]) {
            td.setAttribute("data-label", basliklar[i]);
          }
        });
      });
    });
  }

  /* ========================================================
     5) FORM LOADING STATE
     ======================================================== */
  function formLoadingKur() {
    document.addEventListener("submit", function (e) {
      var f = e.target;
      if (!f || f.tagName !== "FORM") return;
      var btn = f.querySelector("button[type='submit'], .btn-primary[type='submit']");
      if (btn && !btn.classList.contains("mpro-loading")) {
        btn.classList.add("mpro-loading");
        /* 8sn sonra otomatik kaldır (hata vs.) */
        setTimeout(function () { btn.classList.remove("mpro-loading"); }, 8000);
      }
    }, true);
  }

  /* ========================================================
     6) iOS KLAVYE — focus'ta scrollIntoView
     ======================================================== */
  function klavyeKur() {
    document.addEventListener("focusin", function (e) {
      var t = e.target;
      if (!t || !isMobile()) return;
      if (t.tagName !== "INPUT" && t.tagName !== "SELECT" && t.tagName !== "TEXTAREA") return;
      setTimeout(function () {
        try { t.scrollIntoView({ block: "center", behavior: "smooth" }); }
        catch (err) { t.scrollIntoView(); }
      }, 240);
    });
  }

  /* ========================================================
     7) RESIZE — mobil ↔ masaüstü geçişinde temizlik
     ======================================================== */
  function resizeTemizle() {
    var sonMobil = isMobile();
    window.addEventListener("resize", function () {
      var simdi = isMobile();
      if (simdi === sonMobil) return;
      sonMobil = simdi;
      if (!simdi) {
        /* Masaüstüne geçti: drawer/sheet açık kalmasın */
        document.body.classList.remove("mpro-drawer-open");
        document.body.classList.remove("mpro-sheet-open");
      }
    });
  }

  /* ---------- BAŞLAT ---------- */
  function baslat() {
    if (!isMobile()) { resizeTemizle(); return; }
    drawerKur();
    tabbarKur();
    sheetKur();
    tabloKur();
    formLoadingKur();
    klavyeKur();
    resizeTemizle();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(baslat, 60); });
  } else {
    setTimeout(baslat, 60);
  }
  /* Bazı bileşenler geç yüklenebilir */
  setTimeout(function () { if (isMobile()) { tabbarKur(); tabloKur(); sheetKur(); } }, 500);
  setTimeout(function () { if (isMobile()) { tabbarKur(); tabloKur(); } }, 1400);

  /* Sayfa değişimi (tam sayfa reload yoksa) */
  window.addEventListener("pageshow", function () {
    if (isMobile()) { setTimeout(function(){ tabbarKur(); }, 100); }
  });
})();
