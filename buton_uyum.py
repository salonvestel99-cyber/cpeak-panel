#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buton_uyum.py — Login sayfasındaki "Geri" butonunu
"Ana Sayfa" butonuyla aynı görünüme kavuşturur.

login.html'e yeni bir <style> bloğu ekler (idempotent).
Kullanım: py buton_uyum.py [--no-git] [--dry-run]
"""

import argparse, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
LOGIN = KOK / "templates" / "login.html"
YED_DIR = KOK / "backups"

MARKER = "cpk-back-theme-fix"

CSS_BLOK = '''
<style id="cpk-back-theme-fix">
/* cpk: "Geri" (ml11-back) butonunu "Ana Sayfa" (cpk-back-home) ile
   aynı dark-glass görünüme getirir. Sadece login form ekranında. */
@media (max-width: 768px) {

  body.login-page.ml11-form-active .ml11-back {
    background: rgba(0, 0, 0, .42) !important;
    -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
    backdrop-filter: blur(14px) saturate(160%) !important;
    border: 1px solid rgba(255, 255, 255, .18) !important;
    color: #fff !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, .22) !important;
    font-weight: 500 !important;
    padding: 8px 13px !important;
    font-size: .78rem !important;
    gap: 6px !important;
  }

  body.login-page.ml11-form-active .ml11-back:hover,
  body.login-page.ml11-form-active .ml11-back:focus-visible {
    background: rgba(180, 83, 9, .55) !important;
    border-color: rgba(180, 83, 9, .85) !important;
    transform: translateY(-1px);
  }

  body.login-page.ml11-form-active .ml11-back:active {
    transform: translateY(0);
  }

  body.login-page.ml11-form-active .ml11-back svg {
    width: 14px !important;
    height: 14px !important;
    stroke-width: 2.4 !important;
  }
}
</style>
'''

COMMIT_MSG = """ui(login): Geri butonu Ana Sayfa ile aynı görünüme getirildi

- login.html'e #cpk-back-theme-fix style bloğu eklendi (idempotent)
- ml11-back artık dark-glass stiline sahip (cpk-back-home ile aynı)
- Sadece mobil form ekranında geçerli (@media max-width: 768px)
- İşlevler aynı: Geri → splash, Ana Sayfa → /
- Otomatik yama: buton_uyum.py [cpk-back-theme-fix]"""


def login_patch(html: str) -> str:
    if MARKER in html:
        return html
    # body bloğunun sonundaki {% endblock %} öncesine ekle
    idx = html.rfind("{% endblock %}")
    if idx == -1:
        raise RuntimeError("login.html'de {% endblock %} bulunamadı")
    return html[:idx] + CSS_BLOK + "\n" + html[idx:]


def git_kok_bul(p):
    p = p.resolve()
    for u in [p] + list(p.parents):
        if (u / ".git").exists():
            return u
    return None


def git_calistir(kok, *a, sessiz=False):
    r = subprocess.run(
        ["git"] + list(a), cwd=str(kok),
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    if not sessiz:
        if r.stdout.strip():
            print("    " + r.stdout.strip().replace("\n", "\n    "))
        if r.stderr.strip():
            print("    " + r.stderr.strip().replace("\n", "\n    "))
    return r


def git_commit_push(*yollar):
    print("\n[GIT] Başlatılıyor...")
    kok = None
    for y in yollar:
        kok = git_kok_bul(y)
        if kok:
            break
    if kok is None:
        print("[GIT] .git yok — atlandı."); return False
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except Exception:
        print("[GIT] git kurulu değil — atlandı."); return False

    rels = []
    for y in yollar:
        try:
            rels.append(str(y.resolve().relative_to(kok)))
        except ValueError:
            pass
    if not rels:
        print("[GIT] repo dışı — atlandı."); return False

    print(f"[GIT] Repo: {kok}")
    for r in rels:
        print(f"[GIT] + {r}")

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

    if not LOGIN.exists():
        print(f"[HATA] {LOGIN} bulunamadı."); sys.exit(1)

    html = LOGIN.read_text(encoding="utf-8")
    print(f"[OK] login.html okundu ({len(html)} karakter)")

    if MARKER in html:
        print(f"[BİLGİ] '{MARKER}' zaten var — dokunulmadı.")
        return

    if args.dry_run:
        print(f"[DRY-RUN] +{len(CSS_BLOK)} byte style bloğu eklenecek")
        return

    yeni = login_patch(html)

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
    print("  2) Telefonda /giris aç → 'Hoş geldin' ekranına geç")
    print("  3) Sağ üstte 'Geri' ve 'Ana Sayfa' YAN YANA/YIĞIN halde")
    print("     ama İKİSİ DE DARK GLASS — aynı stil")
    print("  4) 'Geri' → splash'a döner")
    print("  5) 'Ana Sayfa' → '/'a gider")
    print("  6) Masaüstünde hiçbir değişiklik yok")


if __name__ == "__main__":
    main()