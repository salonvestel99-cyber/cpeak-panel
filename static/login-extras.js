/* =========================================================
   PREMIUM LOGIN EXTRAS
   - TC input: sadece rakam, max 11 hane
   - Şifre göster/gizle
   - Şifre değiştir (localStorage override)
   - Şifremi unuttum modal
   ========================================================= */
(function () {
  "use strict";

  const SIFRE_KEY = "cpeak_sifreler";
  const OTURUM_KEY = "cpeak_oturum";

  /* ---------- localStorage şifre yardımcıları ---------- */
  function sifreler() {
    try { return JSON.parse(localStorage.getItem(SIFRE_KEY) || "{}"); }
    catch { return {}; }
  }
  function sifreGetir(tc) {
    const s = sifreler();
    return s[tc] || null;
  }
  function sifreKaydet(tc, yeni) {
    const s = sifreler();
    s[tc] = yeni;
    localStorage.setItem(SIFRE_KEY, JSON.stringify(s));
  }

  /* ---------- girisYap override: localStorage'daki şifre öncelikli ---------- */
  window.girisYap = function (tc, sifre) {
    const k = VERI.kullanicilar.find(u => u.tc === tc);
    if (!k) return null;
    const aktif = sifreGetir(tc) || k.sifre;
    if (aktif !== sifre) return null;
    sessionStorage.setItem(OTURUM_KEY, JSON.stringify(k));
    return k;
  };

  /* ---------- TC input: rakam + 11 hane sınırı ---------- */
  function tcKisitla(el) {
    if (!el) return;
    el.addEventListener("input", (e) => {
      let v = e.target.value.replace(/\D/g, "");
      if (v.length > 11) v = v.slice(0, 11);
      if (v !== e.target.value) e.target.value = v;
    });
    el.addEventListener("keypress", (e) => {
      if (e.key.length === 1 && !/[0-9]/.test(e.key)) e.preventDefault();
    });
    el.addEventListener("paste", (e) => {
      const t = (e.clipboardData || window.clipboardData).getData("text");
      if (/\D/.test(t)) {
        e.preventDefault();
        const t2 = t.replace(/\D/g, "").slice(0, 11);
        el.value = t2;
      }
    });
  }

  /* ---------- Modal aç/kapat ---------- */
  function modalAc(id) { const m = document.getElementById(id); if (m) m.hidden = false; }
  function modalKapat(id) { const m = document.getElementById(id); if (m) m.hidden = true; }

  /* ---------- Sayfa hazır olduğunda ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    /* 1) TC input kısıtı */
    tcKisitla(document.getElementById("tcInput"));
    tcKisitla(document.getElementById("changeTc"));

    /* 2) Şifre göster/gizle */
    const pw = document.getElementById("sifreInput");
    const toggle = document.getElementById("togglePw");
    if (pw && toggle) {
      toggle.addEventListener("click", () => {
        const goster = pw.type === "password";
        pw.type = goster ? "text" : "password";
        toggle.classList.toggle("is-visible", goster);
        toggle.setAttribute("aria-label", goster ? "Şifreyi gizle" : "Şifreyi göster");
      });
    }

    /* 3) Modal açıcılar */
    const fBtn = document.getElementById("forgotPwBtn");
    const cBtn = document.getElementById("changePwBtn");
    if (fBtn) fBtn.addEventListener("click", () => modalAc("forgotPwModal"));
    if (cBtn) cBtn.addEventListener("click", () => modalAc("changePwModal"));

    /* 4) Modal kapatıcılar */
    document.getElementById("forgotPwClose")?.addEventListener("click", () => modalKapat("forgotPwModal"));
    document.getElementById("changePwClose")?.addEventListener("click", () => modalKapat("changePwModal"));

    /* 5) Backdrop'a tıklayınca kapat */
    document.querySelectorAll(".modal").forEach((m) => {
      m.addEventListener("click", (e) => {
        if (e.target === m) m.hidden = true;
      });
    });

    /* 6) ESC ile kapat */
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        document.querySelectorAll(".modal:not([hidden])").forEach(m => m.hidden = true);
      }
    });

    /* 7) Şifre değiştir */
    const submit = document.getElementById("changePwSubmit");
    if (submit) {
      submit.addEventListener("click", () => {
        const err = document.getElementById("changePwError");
        const ok = document.getElementById("changePwSuccess");
        err.hidden = true;
        ok.hidden = true;

        const tcV = document.getElementById("changeTc").value.replace(/\D/g, "");
        const oldP = document.getElementById("changeOld").value;
        const newP = document.getElementById("changeNew").value;
        const newP2 = document.getElementById("changeNew2").value;

        const hata = (m) => { err.textContent = m; err.hidden = false; };

        if (tcV.length !== 11) return hata("T.C. kimlik no 11 haneli olmalı.");
        if (!newP || newP.length < 5) return hata("Yeni şifre en az 5 karakter olmalı.");
        if (newP !== newP2) return hata("Yeni şifreler eşleşmiyor.");

        const k = VERI.kullanicilar.find(u => u.tc === tcV);
        if (!k) return hata("Bu T.C. numarasına kayıtlı kullanıcı bulunamadı.");

        const mevcut = sifreGetir(tcV) || k.sifre;
        if (oldP !== mevcut) return hata("Mevcut şifre hatalı.");

        sifreKaydet(tcV, newP);
        ok.textContent = "Şifreniz güncellendi. Artık yeni şifreyle giriş yapabilirsiniz.";
        ok.hidden = false;

        ["changeTc", "changeOld", "changeNew", "changeNew2"].forEach((id) => {
          const el = document.getElementById(id);
          if (el) el.value = "";
        });
      });
    }
  });
})();
