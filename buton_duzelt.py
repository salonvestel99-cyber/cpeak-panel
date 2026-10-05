#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buton_duzelt.py — Login'deki Geri ve Ana Sayfa butonlarını
piksel piksel aynı hale getirir (oval + dark glass + aynı boyut).

Idempotent — bir daha çalıştırılırsa dokunmaz.
Kullanım:
  py buton_duzelt.py --dry-run
  py buton_duzelt.py --no-git
  py buton_duzelt.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
LOGIN = KOK / "templates" / "login.html"
YED_DIR = KOK / "backups"
MARKER = "cpk-btn-unify"

COMMIT_MSG = """ui(login): Geri ve Ana Sayfa butonları tek tip oval

- ml11-back border-radius: 999px (önce 999px, sonra kare kalmıştı)
- İki buton da aynı padding, font, yükseklik
- Aynı dark glass görünüm, aynı hover rengi
- Otomatik yama: buton_duzelt.py"""


CSS_BLOK = '''
<style id="cpk-btn-unify">
/* cpk: Geri ve Ana Sayfa — tek tip oval butonlar (login) */
@media (max-width: 768px) {

  /* ORTAK: her iki buton aynı ölçü ve görünüm */
  body.login-page .cpk-back-home,
  body.login-page.ml11-form-active .ml11-back {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 8px 14px !important;
    border-radius: 999px !important;
    min-height: 36px !important;
    box-sizing: border-box !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: .78rem !important;
    font-weight: 600 !important;
    letter-spacing: .01em !important;
    text-decoration: none !important;
    cursor: pointer !important;
    transition: background .18s ease, border-color .18s ease, transform .18s ease !important;
    background: rgba(0, 0, 0, .42) !important;
    -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
    backdrop-filter: blur(14px) saturate(160%) !important;
    border: 1px solid rgba(255, 255, 255, .18) !important;
    color: #fff !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, .22) !important;
  }

  body.login-page .cpk-back-home:hover,
  body.login-page .cpk-back-home:focus-visible,
  body.login-page.ml11-form-active .ml11-back:hover,
  body.login-page.ml11-form-active .ml11-back:focus-visible {
    background: rgba(180, 83, 9, .55) !important;
    border-color: rgba(180, 83, 9, .85) !important;
    transform: translateY(-1px) !important;
    color: #fff !important;
    outline: none !important;
  }

  body.login-page .cpk-back-home:active,
  body.login-page.ml11-form-active .ml11-back:active {
    transform: translateY(0) !important;
  }

  body.login-page .cpk-back-home svg,
  body.login-page.ml11-form-active .ml11-back svg {
    width: 14px !important;
    height: 14px !important;
    stroke-width: 2.4 !important;
    stroke: currentColor !important;
    fill: none !important;
    flex-shrink: 0 !important;
  }

  /* Konumlar: ikisi sol üstte, alt alta */
  body.login-page .cpk-back-home {
    top: max(12px, env(safe-area-inset-top)) !important;
    left: max(12px, env(safe-area-inset-left)) !important;
    right: auto !important;
  }
  body.login-page.ml11-form-active .ml11-back {
    top: max(12px, env(safe-area-inset-top)) !important;
    left: 12px !important;
    right: auto !important;
  }
  /* Form aktifken Ana Sayfa, Geri'nin altına insin */
  body.login-page.ml11-form-active .cpk-back-home {
    top: calc(max(12px, env(safe-area-inset-top)) + 48px) !important;
  }
}
</style>
'''


def patch(html: str):
    if MARKER in html:
        return html, False, "zaten var"

    # {% endblock %} öncesine ekle
    idx = html.rfind("{% endblock %}")
    if idx == -1:
        return html, False, "{% endblock %} bulunamadı"

    yeni = html[:idx] + CSS_BLOK + "\n" + html[idx:]
    return yeni, True, "buton birleştirme CSS'i eklendi"


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

    rels = []
    for y in yollar:
        try: rels.append(str(y.resolve().relative_to(kok)))
        except ValueError: pass
    if not rels: print("[GIT] repo dışı — atlandı."); return False

    print(f"[GIT] Repo: {kok}")
    for r in rels: print(f"[GIT] + {r}")

    if git_calistir(kok,"add",*rels).returncode != 0:
        print("[GIT] add başarısız."); return False
    if git_calistir(kok,"diff","--cached","--quiet",sessiz=True).returncode == 0:
        print("[GIT] Değişiklik yok."); return False
    if git_calistir(kok,"commit","-m",COMMIT_MSG).returncode != 0:
        print("[GIT] commit başarısız."); return False
    if git_calistir(kok,"push").returncode != 0:
        print("[GIT] UYARI: push başarısız."); return False
    print("[GIT] ✓ commit + push tamam."); return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not LOGIN.exists():
        print(f"[HATA] {LOGIN} bulunamadı."); sys.exit(1)

    html = LOGIN.read_text(encoding="utf-8")
    print(f"[OK] login.html okundu ({len(html)} karakter)")

    yeni, degisti, mesaj = patch(html)
    print(f"[{'✓' if degisti else '·'}] {mesaj}")

    if not degisti:
        return

    if args.dry_run:
        print(f"\n[DRY-RUN] +{len(yeni)-len(html)} karakter eklenecek.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"login.html.{stamp}.bak"
    shutil.copy2(LOGIN, yed)
    print(f"[YEDEK] backups/{yed.name}")

    LOGIN.write_text(yeni, encoding="utf-8")
    print(f"[OK] login.html güncellendi (+{len(yeni)-len(html)} karakter)")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(LOGIN)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Telefonda /giris → form ekranı")
    print("  3) 'Geri' ve 'Ana Sayfa' butonları:")
    print("     • İkisi de OVAL (pill) olmalı")
    print("     • Aynı boyut, aynı font, aynı görünüm")
    print("     • Alt alta, sol üstte")


if __name__ == "__main__":
    main()