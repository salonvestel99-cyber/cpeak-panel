#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hakkimizda_guncelle.py — Hakkımızda sayfasındaki Hikayemiz metnini yeniler.

Yaptığı:
  1) <h2>Hikayemiz</h2> ... <h2>Misyonumuz</h2> arası 2 paragrafı
     3 paragraflık yeni metinle değiştirir.
  2) Meta description / og:description / twitter:description içindeki
     "İstanbul Yıldırım'da" ibaresini "İstanbul'da" yapar.
  3) Idempotent — yeni metin zaten varsa atlar.

Kullanım:
  py hakkimizda_guncelle.py --dry-run     # sadece göster
  py hakkimizda_guncelle.py --no-git      # yaz, git'e gönderme
  py hakkimizda_guncelle.py               # yaz + commit + push
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
HEDEF = KOK / "templates" / "hakkimizda.html"
YED_DIR = KOK / "backups"

YENI_METIN_IMZASI = "İstanbul'da küçük bir sınıfta büyük bir fikirle başladı"

COMMIT_MSG = """içerik(hakkimizda): Hikayemiz metni yenilendi

- Hikayemiz bölümü 3 paragraflık yeni metinle değiştirildi
- "İstanbul Yıldırım'da" → "İstanbul'da" (meta + og + twitter)
- Otomatik yama: hakkimizda_guncelle.py"""


YENI_HIKAYE = '''<h2>Hikayemiz</h2>
      <p>
        C-Peak English, İstanbul'da küçük bir sınıfta büyük bir fikirle başladı:
        İngilizce, kalabalığa değil, kişiye anlatılan bir dildir.
      </p>
      <p>
        Bu yüzden her öğrencimizi tanıyor, seviyesini ölçüyor ve hedefine göre bir yol
        çiziyoruz. Derslerde sıra beklemek yok, kalabalıkta kaybolmak yok.
      </p>
      <p>
        Amacımız sadece sınav kazandırmak değil — İngilizceyi günlük hayatta, işte, seyahatte,
        telefonda rahatça kullanabilen biri olman. Bunun için konuşmaya, dinlemeye ve
        denemeye yer açıyoruz. Hata yapmadan öğrenilmiyor; biz o hataya yer açan tarafız.
      </p>

      
'''


def icerik_guncelle(html: str):
    """(yeni_html, degisti, mesaj) döner."""
    # Idempotent kontrol
    if YENI_METIN_IMZASI in html:
        return html, False, "yeni metin zaten mevcut"

    # Hikayemiz bloğunu değiştir
    pattern = re.compile(
        r'<h2>Hikayemiz</h2>.*?(?=<h2>Misyonumuz</h2>)',
        re.DOTALL,
    )
    yeni, n = pattern.subn(YENI_HIKAYE, html, count=1)

    if n == 0:
        raise RuntimeError(
            "'<h2>Hikayemiz</h2> ... <h2>Misyonumuz</h2>' "
            "bölümü bulunamadı — dosya yapısı değişmiş olabilir."
        )

    # Yıldırım ibaresini kaldır
    onceki = yeni
    yeni = yeni.replace("İstanbul Yıldırım'da", "İstanbul'da")
    yildirim_sayisi = onceki.count("İstanbul Yıldırım'da")

    if yeni == html:
        return html, False, "değişiklik yok"

    mesaj = f"Hikayemiz güncellendi ({n} blok)"
    if yildirim_sayisi:
        mesaj += f" + {yildirim_sayisi} 'Yıldırım' ibaresi kaldırıldı"
    return yeni, True, mesaj


# ============================================================
# GIT
# ============================================================
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


# ============================================================
# ANA
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not HEDEF.exists():
        print(f"[HATA] {HEDEF} bulunamadı."); sys.exit(1)

    html = HEDEF.read_text(encoding="utf-8")
    print(f"[OK] hakkimizda.html okundu ({len(html)} karakter)")

    try:
        yeni, degisti, mesaj = icerik_guncelle(html)
    except RuntimeError as e:
        print(f"[HATA] {e}"); sys.exit(1)

    if not degisti:
        print(f"[ATLA] {mesaj}. Değişiklik yapılmadı.")
        return

    print(f"[BİLGİ] {mesaj}")
    print(f"[BİLGİ] Karakter: {len(html)} → {len(yeni)} "
          f"({len(yeni) - len(html):+d})")

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı. Önizleme:")
        print("-" * 60)
        # Yeni Hikayemiz bloğunu göster
        m = re.search(
            r'<h2>Hikayemiz</h2>.*?(?=<h2>Misyonumuz</h2>)',
            yeni, re.DOTALL,
        )
        if m:
            print(m.group(0).rstrip())
        print("-" * 60)
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"hakkimizda.html.{stamp}.bak"
    shutil.copy2(HEDEF, yed)
    print(f"[YEDEK] backups/{yed.name}")

    HEDEF.write_text(yeni, encoding="utf-8")
    print(f"[OK] hakkimizda.html güncellendi")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(HEDEF)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) /hakkimizda → 'Hikayemiz' bölümü yeni metni gösteriyor")
    print("  3) Sayfa kaynağında 'Yıldırım' hiç geçmiyor")
    print("  4) Meta description / og:description İstanbul'da olarak güncellendi")


if __name__ == "__main__":
    main()