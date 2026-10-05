#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buton_hiyerarsi.py — Login'deki Geri ve Ana Sayfa butonlarına
görsel hiyerarşi kazandırır.

- Geri: küçük daire (34px), sadece ok ikonu, ikincil
- Anasayfa: oval, ikon + metin, birincil
- Yan yana, sol üstte

Kullanım:
  py buton_hiyerarsi.py --dry-run
  py buton_hiyerarsi.py --no-git
  py buton_hiyerarsi.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
LOGIN = KOK / "templates" / "login.html"
YED_DIR = KOK / "backups"
MARKER = "cpk-btn-hierarchy"

COMMIT_MSG = """ui(login): Geri + Anasayfa butonlarına hiyerarşi

- Geri: küçük daire (34px), sadece ok ikonu, ikincil
- Anasayfa: oval, ikon + metin, birincil
- Sol üstte yan yana, küçükten büyüğe akış
- Önceki 'cpk-btn-unify' stilini ezer (idempotent)
- Otomatik yama: buton_hiyerarsi.py"""


CSS_BLOK = '''
<style id="cpk-btn-hierarchy">
/* cpk: Geri (ikincil) + Anasayfa (birincil) — yan yana */
@media (max-width: 768px) {

  /* Önce eski birleştirici bloğu etkisiz kıl */
  body.login-page #cpk-btn-unify ~ * .cpk-back-home,
  body.login-page .cpk-back-home,
  body.login-page.ml11-form-active .ml11-back {
    /* ortak konum — sol üst, yan yana */
    position: fixed !important;
    top: max(12px, env(safe-area-inset-top)) !important;
    z-index: 1300 !important;
    box-sizing: border-box !important;
  }

  /* ---------- GERİ: ikincil, küçük daire ---------- */
  body.login-page.ml11-form-active .ml11-back {
    left: 12px !important;
    width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0 !important;
    background: rgba(0, 0, 0, .32) !important;
    -webkit-backdrop-filter: blur(12px) saturate(150%) !important;
    backdrop-filter: blur(12px) saturate(150%) !important;
    border: 1px solid rgba(255, 255, 255, .12) !important;
    color: rgba(255, 255, 255, .78) !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, .18) !important;
    font-size: 0 !important; /* metni gizle */
    transition: background .18s ease, border-color .18s ease, color .18s ease, transform .18s ease !important;
    -webkit-tap-highlight-color: transparent !important;
  }
  /* İçindeki "Geri" span'ini sakla */
  body.login-page.ml11-form-active .ml11-back span {
    display: none !important;
  }
  body.login-page.ml11-form-active .ml11-back svg {
    width: 15px !important;
    height: 15px !important;
    stroke: currentColor !important;
    stroke-width: 2.4 !important;
    fill: none !important;
  }
  body.login-page.ml11-form-active .ml11-back:hover,
  body.login-page.ml11-form-active .ml11-back:focus-visible {
    background: rgba(180, 83, 9, .45) !important;
    border-color: rgba(180, 83, 9, .7) !important;
    color: #fff !important;
    transform: translateY(-1px);
    outline: none !important;
  }
  body.login-page.ml11-form-active .ml11-back:active {
    transform: scale(.94) !important;
  }

  /* ---------- ANASAYFA: birincil, oval ---------- */
  body.login-page .cpk-back-home {
    left: calc(12px + 34px + 8px) !important; /* Geri + gap */
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 7px 14px !important;
    min-height: 34px !important;
    border-radius: 999px !important;
    background: rgba(0, 0, 0, .55) !important;
    -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
    backdrop-filter: blur(14px) saturate(160%) !important;
    border: 1px solid rgba(255, 255, 255, .20) !important;
    color: #fff !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: .78rem !important;
    font-weight: 600 !important;
    letter-spacing: .01em !important;
    text-decoration: none !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, .28) !important;
    transition: background .18s ease, border-color .18s ease, transform .18s ease !important;
    -webkit-tap-highlight-color: transparent !important;
  }
  body.login-page .cpk-back-home svg {
    width: 14px !important;
    height: 14px !important;
    stroke: currentColor !important;
    stroke-width: 2.4 !important;
    fill: none !important;
    flex-shrink: 0 !important;
  }
  body.login-page .cpk-back-home:hover,
  body.login-page .cpk-back-home:focus-visible {
    background: rgba(180, 83, 9, .65) !important;
    border-color: rgba(180, 83, 9, .9) !important;
    transform: translateY(-1px);
    outline: none !important;
  }
  body.login-page .cpk-back-home:active {
    transform: translateY(0) !important;
  }

  /* Form aktifken Anasayfa'yı sıfırla (yan yana kalacak) */
  body.login-page.ml11-form-active .cpk-back-home {
    top: max(12px, env(safe-area-inset-top)) !important;
  }
}
</style>
'''


def patch(html: str):
    if MARKER in html:
        return html, False, "zaten var"
    idx = html.rfind("{% endblock %}")
    if idx == -1:
        return html, False, "{% endblock %} bulunamadı"
    return html[:idx] + CSS_BLOK + "\n" + html[idx:], True, "hiyerarşi CSS'i eklendi"


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
    print(f"[OK] login.html güncellendi")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(LOGIN)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Telefonda /giris → form ekranına geç")
    print("  3) Sol üstte şunu görmelisin:")
    print("       [←]  [← Anasayfa]")
    print("        ↑         ↑")
    print("     küçük    birincil")
    print("     ikincil  (oval, metinli)")
    print("  4) Geri → splash'a dön")
    print("  5) Anasayfa → ana sayfa açılır")


if __name__ == "__main__":
    main()