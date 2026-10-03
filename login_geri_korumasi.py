#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
login_geri_korumasi.py — Giriş sonrası geri tuşu koruması
  • base.html'e "cpeak-login-guard" script'i ekler (idempotent)
  • login.html'e sessionStorage flag script'i ekler (idempotent)
  • Login → dashboard geçişinde geri tuşu artık login'e döndürmez
  • 'Çıkmak için menüden Çıkış Yap' toast uyarısı
  • Diğer sayfalar arası geri gezinmesi normal çalışır
Kullanım: py login_geri_korumasi.py [--no-git] [--dry-run]
"""

import argparse, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
BASE = KOK / "templates" / "base.html"
LOGIN = KOK / "templates" / "login.html"
YED_DIR = KOK / "backups"

GUARD_ID = "cpeak-login-guard"
FLAG_ID = "cpeak-login-visit-flag"

COMMIT_MSG = """mobil(giriş): login sonrası geri tuşu koruması

- base.html'e cpeak-login-guard script'i eklendi (idempotent)
- login.html'e cpeak-login-visit-flag script'i eklendi
- Login → dashboard geçişinde geri tuşu artık login'e döndürmez
- Çıkmak için menüden 'Çıkış Yap' kullanılmalı
- Diğer sayfalar arası geri gezinmesi normal çalışır
- Masaüstü + mobil
- Otomatik yama: login_geri_korumasi.py [CPEAK_LOGIN_GUARD]"""

GUARD_SCRIPT = '''<script id="cpeak-login-guard">
/* ============================================================
   C-Peak · Login Sonrası Geri Tuşu Koruması
   Amaç: Login → dashboard geçişinde geri tuşu login sayfasına
   dönmesin. Kullanıcı geri basarsa panelde kalır + uyarı görür.
   Sadece login'den hemen sonra aktif olur; normal gezinme bozulmaz.
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakLoginGuard) return;
  window.__cpeakLoginGuard = true;

  /* Login sayfasında çalışmasın */
  if (document.body && document.body.classList.contains("login-page")) return;

  /* Login'den hemen sonra mı geldik? */
  var ref = document.referrer || "";
  var refLogin = /\\/login(\\?|$|\\/|#)/i.test(ref)
               || /\\/giris(\\?|$|\\/|#)/i.test(ref);
  var flag = null;
  try { flag = sessionStorage.getItem("cpeak_login_visit"); } catch (e) {}
  try { sessionStorage.removeItem("cpeak_login_visit"); } catch (e) {}

  if (!refLogin && !flag) return;  /* Login'den gelmediyse karışma */

  /* Yaş kontrolü: flag 30 dakikadan eskiyse sayma */
  if (!refLogin && flag) {
    var t = parseInt(flag, 10);
    if (!isNaN(t) && (Date.now() - t) > 30 * 60 * 1000) return;
  }

  /* --- GUARD KUR --- */
  var GUARD_STATE = { cpeakGuard: 1 };
  try {
    history.pushState(GUARD_STATE, "", location.href);
  } catch (e) { return; }

  function gosterToast() {
    var t = document.getElementById("cpeak-guard-toast");
    if (!t) {
      t = document.createElement("div");
      t.id = "cpeak-guard-toast";
      t.setAttribute("role", "status");
      t.style.cssText = [
        "position:fixed",
        "left:50%",
        "bottom:calc(env(safe-area-inset-bottom, 0px) + 24px)",
        "transform:translateX(-50%) translateY(16px)",
        "background:rgba(24,24,27,.94)",
        "color:#fafaf9",
        "padding:12px 20px",
        "border-radius:999px",
        "font-family:Inter,system-ui,-apple-system,sans-serif",
        "font-size:13.5px",
        "font-weight:500",
        "letter-spacing:.01em",
        "box-shadow:0 12px 30px rgba(0,0,0,.32), 0 2px 6px rgba(0,0,0,.18)",
        "z-index:2147483647",
        "opacity:0",
        "pointer-events:none",
        "transition:opacity .22s ease, transform .22s ease",
        "max-width:calc(100vw - 40px)",
        "text-align:center",
        "line-height:1.35",
        "backdrop-filter:blur(10px)",
        "-webkit-backdrop-filter:blur(10px)"
      ].join(";");
      document.body.appendChild(t);
    }
    t.textContent = "Çıkmak için menüden Çıkış Yap\\u2019ı kullanın";
    void t.offsetWidth;
    t.style.opacity = "1";
    t.style.transform = "translateX(-50%) translateY(0)";
    clearTimeout(t._tm);
    t._tm = setTimeout(function () {
      t.style.opacity = "0";
      t.style.transform = "translateX(-50%) translateY(16px)";
    }, 2400);
  }

  window.addEventListener("popstate", function (e) {
    /* Zaten guard state'indeyse karışma */
    if (e.state && e.state.cpeakGuard) return;

    /* Guard'ı yeniden kur + kullanıcıya bildir */
    try {
      history.pushState(GUARD_STATE, "", location.href);
    } catch (err) { return; }
    gosterToast();
  });
})();
</script>
'''

FLAG_SCRIPT = '''<script id="cpeak-login-visit-flag">
/* Login sayfası ziyaretini işaretle — geri tuşu koruması için */
(function () {
  try {
    sessionStorage.setItem("cpeak_login_visit", String(Date.now()));
  } catch (e) {}
})();
</script>
'''


def base_patch(html):
    if GUARD_ID in html:
        return html, False
    idx = html.rfind("</body>")
    if idx == -1:
        raise RuntimeError("base.html'de </body> bulunamadı")
    html = html[:idx] + GUARD_SCRIPT + "\n" + html[idx:]
    return html, True


def login_patch(html):
    if FLAG_ID in html:
        return html, False
    # login.html'de son {% endblock %} (body bloğunun kapanışı) öncesine ekle
    idx = html.rfind("{% endblock %}")
    if idx == -1:
        raise RuntimeError("login.html'de {% endblock %} bulunamadı")
    html = html[:idx] + FLAG_SCRIPT + "\n" + html[idx:]
    return html, True


def git_kok_bul(p):
    p = p.resolve()
    for u in [p] + list(p.parents):
        if (u / ".git").exists(): return u
    return None


def git_calistir(kok, *a, sessiz=False):
    r = subprocess.run(["git"]+list(a), cwd=str(kok), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if not sessiz:
        if r.stdout.strip(): print("    " + r.stdout.strip().replace("\n","\n    "))
        if r.stderr.strip(): print("    " + r.stderr.strip().replace("\n","\n    "))
    return r


def git_commit_push(*yollar):
    print("\n[GIT] Başlatılıyor...")
    kok = None
    for y in yollar:
        kok = git_kok_bul(y)
        if kok: break
    if kok is None: print("[GIT] .git yok — atlandı."); return False
    try: subprocess.run(["git","--version"], capture_output=True, check=True)
    except Exception: print("[GIT] git kurulu değil — atlandı."); return False
    rels = []
    for y in yollar:
        try: rels.append(str(y.resolve().relative_to(kok)))
        except ValueError: pass
    if not rels: print("[GIT] repo dışı — atlandı."); return False
    print(f"[GIT] Repo: {kok}")
    for r in rels: print(f"[GIT] + {r}")
    if git_calistir(kok, "add", *rels).returncode != 0:
        print("[GIT] add başarısız."); return False
    if git_calistir(kok, "diff", "--cached", "--quiet", sessiz=True).returncode == 0:
        print("[GIT] Değişiklik yok."); return False
    if git_calistir(kok, "commit", "-m", COMMIT_MSG).returncode != 0:
        print("[GIT] commit başarısız."); return False
    if git_calistir(kok, "push").returncode != 0:
        print("[GIT] UYARI: push başarısız. Commit yerelde kaldı."); return False
    print("[GIT] ✓ commit + push tamam."); return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not BASE.exists() or not LOGIN.exists():
        print("[HATA] base.html veya login.html yok."); sys.exit(1)

    base_html = BASE.read_text(encoding="utf-8")
    login_html = LOGIN.read_text(encoding="utf-8")
    print(f"[OK] base.html  ({len(base_html)} karakter)")
    print(f"[OK] login.html ({len(login_html)} karakter)")

    try:
        yeni_base, base_degisti = base_patch(base_html)
    except Exception as e:
        print(f"[HATA] base patch: {e}"); sys.exit(1)
    try:
        yeni_login, login_degisti = login_patch(login_html)
    except Exception as e:
        print(f"[HATA] login patch: {e}"); sys.exit(1)

    if args.dry_run:
        print(f"[DRY-RUN] base değişir: {base_degisti}")
        print(f"[DRY-RUN] login değişir: {login_degisti}")
        return

    if not base_degisti and not login_degisti:
        print("[ATLA] Her ikisi de zaten korumalı.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if base_degisti:
        shutil.copy2(BASE, YED_DIR / f"base.html.{stamp}.bak")
        print(f"[YEDEK] backups/base.html.{stamp}.bak")
        BASE.write_text(yeni_base, encoding="utf-8")
        print(f"[OK] base.html güncellendi  (+{len(yeni_base)-len(base_html)} karakter)")

    if login_degisti:
        shutil.copy2(LOGIN, YED_DIR / f"login.html.{stamp}.bak")
        print(f"[YEDEK] backups/login.html.{stamp}.bak")
        LOGIN.write_text(yeni_login, encoding="utf-8")
        print(f"[OK] login.html güncellendi (+{len(yeni_login)-len(login_html)} karakter)")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(BASE, LOGIN)

    print("\nBitti.")
    print("Test:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Tarayıcı önbelleğini temizle (Ctrl+Shift+R)")
    print("  3) Telefondan giriş yap → dashboard gelir")
    print("  4) Geri tuşuna bas → panelde kalır + uyarı çıkar")
    print("  5) Ödevler/Program gibi sayfalara git → geri normal çalışır")
    print("  6) Menüden 'Çıkış Yap' → normal logout")


if __name__ == "__main__":
    main()