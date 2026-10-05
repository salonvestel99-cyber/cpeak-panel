#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jsonld_zenginlestir.py — index.html'deki JSON-LD'yi Google
Local Business standartlarına yükselt.

Eklenenler:
  - @type: ["EducationalOrganization", "LocalBusiness"]
  - geo (koordinatlar)
  - hasMap (Google Maps linki)
  - openingHoursSpecification (çalışma saatleri)
  - priceRange, areaServed, paymentAccepted
  - addressRegion / addressLocality / postalCode ayrı ayrı
  - description "Bayrampaşa"ya göre güncellendi
  - sameAs'e hasMap eklendi

Kullanım:
  py jsonld_zenginlestir.py --dry-run
  py jsonld_zenginlestir.py --no-git
  py jsonld_zenginlestir.py
"""

import argparse, json, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
INDEX = KOK / "templates" / "index.html"
YED_DIR = KOK / "backups"

COMMIT_MSG = """seo(jsonld): LocalBusiness + geo + hours + hasMap

- @type: EducationalOrganization + LocalBusiness (çift tip)
- geo koordinatları (Bayrampaşa)
- hasMap (Google Maps linki) + sameAs'e eklendi
- openingHoursSpecification (hafta içi 09-21, cumartesi 10-18)
- priceRange ₺₺, areaServed İstanbul, paymentAccepted
- addressRegion/Locality/PostalCode ayrıldı
- description "Bayrampaşa"ya göre güncellendi
- Otomatik yama: jsonld_zenginlestir.py"""


YENI_JSONLD = '''{
  "@context": "https://schema.org",
  "@type": ["EducationalOrganization", "LocalBusiness"],
  "name": "C-Peak English",
  "alternateName": "C-Peak İngilizce Kursu",
  "url": "https://www.cpeakenglish.com",
  "logo": "https://www.cpeakenglish.com/static/logochrome.png",
  "image": [
    "https://www.cpeakenglish.com/static/logochrome.png"
  ],
  "description": "İstanbul Bayrampaşa'da küçük sınıflarda, birebir ilgiyle İngilizce eğitimi veren modern bir dil okulu.",
  "slogan": "İngilizce, kalabalığa değil, kişiye anlatılan bir dildir.",
  "telephone": "+905421808402",
  "email": "cpeakenglish@gmail.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Yıldırım Mahallesi, Bosna Sokak No: 29/A",
    "addressLocality": "Bayrampaşa",
    "addressRegion": "İstanbul",
    "postalCode": "34045",
    "addressCountry": "TR"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 41.0615227,
    "longitude": 28.9003676
  },
  "hasMap": "https://share.google/hyruLgcpDnjdChhOb",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "21:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": "Saturday",
      "opens": "10:00",
      "closes": "18:00"
    }
  ],
  "priceRange": "₺₺",
  "paymentAccepted": "Nakit, Kredi Kartı, Havale",
  "currenciesAccepted": "TRY",
  "areaServed": {
    "@type": "City",
    "name": "İstanbul"
  },
  "sameAs": [
    "https://www.instagram.com/c_peak_english",
    "https://www.youtube.com/@c-peak-english",
    "https://share.google/hyruLgcpDnjdChhOb"
  ]
}'''


def jsonld_degistir(html: str):
    """Eski JSON-LD bloğunu yeni ile değiştir."""

    # Marker kontrolü — idempotent
    if "hasMap" in html and "41.0615227" in html:
        return html, False, "JSON-LD zaten zengin"

    # JSON-LD blok(lar)ını bul
    pat = re.compile(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        re.DOTALL,
    )
    bulunanlar = list(pat.finditer(html))
    if not bulunanlar:
        return html, False, "JSON-LD bloğu bulunamadı"

    # İlk bloğu değiştir
    m = bulunanlar[0]

    # Doğrulama: gerçekten JSON mu?
    icerik = m.group(1).strip()
    try:
        json.loads(icerik)
    except json.JSONDecodeError as e:
        return html, False, f"mevcut JSON geçersiz: {e}"

    # Yeni blok
    yeni_blok = (
        '<script type="application/ld+json">\n'
        + YENI_JSONLD + "\n"
        + "</script>"
    )

    yeni_html = html[:m.start()] + yeni_blok + html[m.end():]

    # Yeni blok geçerli JSON mu kontrol et
    try:
        json.loads(YENI_JSONLD)
    except json.JSONDecodeError as e:
        return html, False, f"yeni JSON geçersiz (bug!): {e}"

    return yeni_html, True, "JSON-LD zenginleştirildi"


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

    if not INDEX.exists():
        print(f"[HATA] {INDEX} bulunamadı."); sys.exit(1)

    html = INDEX.read_text(encoding="utf-8")
    print(f"[OK] index.html okundu ({len(html)} karakter)")

    yeni, degisti, mesaj = jsonld_degistir(html)
    print(f"[{'✓' if degisti else '·'}] {mesaj}")

    if not degisti:
        return

    print(f"[BİLGİ] Karakter: {len(html)} → {len(yeni)} "
          f"({len(yeni)-len(html):+d})")

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı. Önizleme:")
        print("-" * 60)
        m = re.search(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
            yeni, re.DOTALL,
        )
        if m:
            print(m.group(1).strip()[:800])
            print("...")
        print("-" * 60)
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"index.html.{stamp}.bak"
    shutil.copy2(INDEX, yed)
    print(f"[YEDEK] backups/{yed.name}")

    INDEX.write_text(yeni, encoding="utf-8")
    print(f"[OK] index.html güncellendi")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(INDEX)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) https://search.google.com/test/rich-results aç")
    print("     → URL yapıştır: https://www.cpeakenglish.com/")
    print("     → 'Test URL' tıkla → LocalBusiness algılanmış olmalı")
    print("  3) https://validator.schema.org → JSON'u yapıştır")


if __name__ == "__main__":
    main()