#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_v3.py — Talisman CSP'sine frame-src ekle.

Sorun: İki CSP header var. Talisman'ın CSP'si frame-src içermiyor,
bu yüzden default-src 'self''e düşüyor ve OSM iframe bloklanıyor.

Çözüm: security.py'deki csp dict'ine frame-src satırı ekle.

Kullanım:
  py harita_v3.py --dry-run
  py harita_v3.py --no-git
  py harita_v3.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
SEC = KOK / "security.py"
YED_DIR = KOK / "backups"

FRAME_SRC_VALUE = (
    "'self' https://www.openstreetmap.org https://www.google.com"
)

COMMIT_MSG = """fix(csp): Talisman frame-src — OSM haritası yüklenebilsin

- security.py Talisman csp sözlüğüne frame-src eklendi
- Önceden iki CSP çakışıyordu, en kısıtlayıcı (Talisman) kazanıyordu
- Bu yüzden OSM iframe bloklanıyordu
- Otomatik yama: harita_v3.py"""


def patch(ic: str):
    """(yeni_ic, degisti, mesaj)"""

    if "openstreetmap.org" in ic:
        return ic, False, "Talisman CSP'de OSM zaten var"

    # csp = { ... } bloğunu bul
    m = re.search(r'(\bcsp\s*=\s*\{)', ic)
    if not m:
        return ic, False, "security.py'de 'csp = {' bulunamadı"

    ekle_noktasi = m.end(1)  # '{' karakterinden hemen sonra
    # Girinti tespit et
    satir_basi = ic.rfind("\n", 0, m.start()) + 1
    girinti = ""
    for ch in ic[satir_basi:m.start()]:
        if ch in " \t":
            girinti += ch
        else:
            break
    # İç girinti bir fazla
    ic_girinti = girinti + "    "

    yeni_satir = (
        f'\n{ic_girinti}"frame-src": "{FRAME_SRC_VALUE}",'
    )
    yeni = ic[:ekle_noktasi] + yeni_satir + ic[ekle_noktasi:]

    # Çift eklemeyi engelle
    if yeni.count('"frame-src"') > 1:
        return ic, False, "birden fazla frame-src olur — iptal"

    return yeni, True, "Talisman CSP'ye frame-src eklendi"


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

    if not SEC.exists():
        print(f"[HATA] {SEC} bulunamadı."); sys.exit(1)

    ic = SEC.read_text(encoding="utf-8")
    print(f"[OK] security.py okundu ({len(ic)} karakter)")

    yeni, degisti, mesaj = patch(ic)
    print(f"[BİLGİ] {mesaj}")

    if not degisti:
        return

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı. Yeni csp bloğu:")
        m = re.search(r'\bcsp\s*=\s*\{[^}]*\}', yeni, re.DOTALL)
        if m:
            print("-" * 60)
            print(m.group(0)[:1200])
            print("-" * 60)
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"security.py.{stamp}.bak"
    shutil.copy2(SEC, yed)
    print(f"[YEDEK] backups/{yed.name}")

    SEC.write_text(yeni, encoding="utf-8")
    print(f"[OK] security.py güncellendi (+{len(yeni)-len(ic)} karakter)")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(SEC)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Telefonda ana sayfa → İletişim → harita yüklenmeli")
    print("  3) Hâlâ gri kutuysa: Chrome DevTools > Network > ana istek")
    print("     Response Headers'ta KAÇ tane Content-Security-Policy var?")


if __name__ == "__main__":
    main()