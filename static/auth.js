// Client-side oturum yönetimi. Sunucu yok, sessionStorage yeter.

const OTURUM_KEY = "cpeak_oturum";

function girisYap(tc, sifre) {
  const k = VERI.kullanicilar.find(u => u.tc === tc && u.sifre === sifre);
  if (!k) return null;
  sessionStorage.setItem(OTURUM_KEY, JSON.stringify(k));
  return k;
}

function aktifKullanici() {
  const raw = sessionStorage.getItem(OTURUM_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

function cikisYap() {
  sessionStorage.removeItem(OTURUM_KEY);
  window.location.href = "index.html";
}

function korumaliSayfa() {
  // Sadece panel.html gibi korumalı sayfalarda çağrılır.
  const k = aktifKullanici();
  if (!k) { window.location.href = "index.html"; return null; }
  return k;
}

// ---- Giriş sayfası kontrolü (varsa) ----
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  if (!form) return;

  // Zaten giriş yapılmışsa direkt panele gönder
  if (aktifKullanici()) {
    window.location.href = "panel.html";
    return;
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const tc = document.getElementById("tcInput").value.trim();
    const sifre = document.getElementById("sifreInput").value;
    const err = document.getElementById("loginError");

    const k = girisYap(tc, sifre);
    if (!k) {
      err.textContent = "T.C. kimlik no veya şifre hatalı.";
      err.hidden = false;
      return;
    }
    err.hidden = true;
    window.location.href = "panel.html";
  });
});
