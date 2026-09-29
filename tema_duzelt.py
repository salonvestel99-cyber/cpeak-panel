# -*- coding: utf-8 -*-
"""Tema senkronizasyonu: tek anahtar (cpeak_theme) + data-theme ve dark class birlikte."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(KOK, "templates", "base.html")
TJS = os.path.join(KOK, "static", "theme.js")
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================
# 1) theme.js - bastan yaz
# ============================================================
shutil.copy2(TJS, os.path.join(YED, f"theme.js.{stamp}.bak"))
print(f"[YEDEK] backups/theme.js.{stamp}.bak")

YENI_TJS = '''/* =========================================================
   THEME - Koyu / Aydinlik Mod Toggle (tek anahtar: cpeak_theme)
   ========================================================= */
(function () {
  "use strict";

  var KEY = "cpeak_theme";

  function get() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function set(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }
  function apply(t) {
    var h = document.documentElement;
    h.setAttribute("data-theme", t);
    h.classList.toggle("dark", t === "dark");
    // Diger bilesenlere haber ver
    try {
      window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: t } }));
    } catch (e) {}
  }

  // Baslangic: kaydedilmis tema varsa uygula, yoksa OS tercihine bak
  var saved = get();
  if (saved) {
    apply(saved);
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    apply("dark");
  }

  // Tum toggle butonlarini bagla (tek sefer, capture phase ile)
  function bagla() {
    var btns = document.querySelectorAll("[data-theme-toggle], #udThemeToggle");
    btns.forEach(function (b) {
      if (b.__temaBagli) return;
      b.__temaBagli = true;
      b.addEventListener("click", function (e) {
        e.stopImmediatePropagation();
        e.preventDefault();
        var h = document.documentElement;
        var cur = h.getAttribute("data-theme")
                  || (h.classList.contains("dark") ? "dark" : "light");
        var next = cur === "light" ? "dark" : "light";
        apply(next);
        set(next);
      }, true);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bagla);
  } else {
    bagla();
  }
  // Bazi butonlar sonradan olusabilir
  setTimeout(bagla, 300);
  setTimeout(bagla, 1200);

  // OS tercihini dinle (kullanici manuel secim yapmadiysa)
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var handler = function (e) {
      if (!get()) apply(e.matches ? "dark" : "light");
    };
    if (mq.addEventListener) mq.addEventListener("change", handler);
    else if (mq.addListener) mq.addListener(handler);
  }
})();
'''

with open(TJS, "w", encoding="utf-8") as f:
    f.write(YENI_TJS)
print("[OK] static/theme.js yeniden yazildi (tek anahtar + dark class)")


# ============================================================
# 2) base.html duzeltmeleri
# ============================================================
shutil.copy2(TPL, os.path.join(YED, f"base.html.{stamp}.bak"))
print(f"[YEDEK] backups/base.html.{stamp}.bak")

with open(TPL, "r", encoding="utf-8") as f:
    html = f.read()

degisiklik = 0

# --- 2.1) Kullanici menusundeki yanlis anahtari duzelt ---
# localStorage.setItem("theme", ...)  ->  localStorage.setItem("cpeak_theme", ...)
onceki = html
html = re.sub(
    r'localStorage\.setItem\(\s*["\']theme["\']\s*,',
    'localStorage.setItem("cpeak_theme",',
    html
)
if html != onceki:
    print("[OK] UDTEMA-JS icindeki 'theme' anahtari 'cpeak_theme' yapildi")
    degisiklik += 1
else:
    print("[ATLA] 'theme' anahtari bulunamadi (belki zaten duzeltilmis)")

# --- 2.2) Baslangic inline script'ini guncelle (dark class da eklensin) ---
# Mevcut: sadece setAttribute("data-theme", t) yapiyor
# Yeni: hem setAttribute hem classList.toggle
ESKI_INIT_PATTERN = re.compile(
    r'var t = localStorage\.getItem\("cpeak_theme"\);.*?'
    r'else if \(window\.matchMedia[^;]+?'
    r'document\.documentElement\.setAttribute\("data-theme"[^\)]*\);\s*\}',
    re.DOTALL
)

YENI_INIT = '''var t = localStorage.getItem("cpeak_theme");
  if (!t && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    t = "dark";
  }
  if (t) {
    document.documentElement.setAttribute("data-theme", t);
    document.documentElement.classList.toggle("dark", t === "dark");
  }'''

if ESKI_INIT_PATTERN.search(html):
    html = ESKI_INIT_PATTERN.sub(YENI_INIT, html, count=1)
    print("[OK] baslangic inline script'i guncellendi (dark class eklendi)")
    degisiklik += 1
else:
    print("[ATLA] inline init pattern bulunamadi (elle kontrol gerekebilir)")

with open(TPL, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n[BITTI] {degisiklik} degisiklik yapildi")
print("""
============================================================
SIMDI:
1. git add static/theme.js templates/base.html
2. git commit -m "Tema senkronizasyonu: tek anahtar + dark class"
3. git push
4. Render deploy'unu bekle
5. Tarayicida test et:
   - Ana menu -> tema degistir
   - Baska sayfaya git (ders programi)
   - Geri gel -> ayni tema korunmali
   - Tarayiciyi kapat/ac -> tema korunmali
============================================================
""")