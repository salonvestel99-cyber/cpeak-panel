#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_v6.py — CartoDB API anahtarı + tasarım iyileştirmeleri

1) Tile URL'ine api_key eklenir (filigran kalkar)
2) Harita daha büyük ve dengeli hale gelir
3) Pin daha görünür (parmak dostu)
4) Zoom kontrolleri 44px (Apple/Google standardı)
5) Adres başlığı sadeleşir

Kullanım:
  py harita_v6.py --dry-run
  py harita_v6.py --no-git
  py harita_v6.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
INDEX = KOK / "templates" / "index.html"
YED_DIR = KOK / "backups"

API_KEY = "cb1_49pw_1_84f5c0fd5f2acc5f8f492556"
MARKER_TUNE = "cpk-map-tune-v2"

COMMIT_MSG = """feat(harita): CartoDB API key + tasarım iyileştirmeleri

- Tile URL'ine api_key eklendi → filigran kalkar
- Harita büyütüldü: min-height 280px, mobil 4/3, masaüstü 16/10
- Pin büyütüldü: 20px dot, 52px pulse (parmak dostu)
- Zoom kontrolleri 44px (iOS HIG uyumlu)
- Kart başlığı sadeleşti: tam adres alt satırda
- Otomatik yama: harita_v6.py"""


TUNE_CSS = f'''
<style id="{MARKER_TUNE}">
/* --- Harita: boyut + pin + zoom iyileştirmeleri --- */

.cpk-map-canvas {{
  min-height: 300px;
}}

.cpk-map-canvas .leaflet-control-zoom {{
  margin: 14px !important;
}}
.cpk-map-canvas .leaflet-control-zoom a {{
  width: 44px !important;
  height: 44px !important;
  line-height: 42px !important;
  font-size: 24px !important;
  font-weight: 500 !important;
}}
.cpk-map-canvas .leaflet-control-zoom a:first-child {{
  border-radius: 12px 12px 0 0 !important;
}}
.cpk-map-canvas .leaflet-control-zoom a:last-child {{
  border-radius: 0 0 12px 12px !important;
}}

.cpk-map-pin-dot {{
  width: 22px !important;
  height: 22px !important;
  border: 3px solid #18181b !important;
  box-shadow:
    0 0 0 3px rgba(245,158,11,.4),
    0 6px 20px rgba(0,0,0,.6) !important;
}}
.cpk-map-pin-pulse {{
  width: 56px !important;
  height: 56px !important;
}}

.cpk-map-head {{
  padding: 18px 22px !important;
}}
.cpk-map-addr {{
  font-size: .92rem !important;
  line-height: 1.5 !important;
}}

@media (max-width: 640px) {{
  .cpk-map-canvas {{
    aspect-ratio: 4 / 3 !important;
    min-height: 280px !important;
  }}
  .cpk-map-head {{
    padding: 14px 16px !important;
    gap: 10px !important;
  }}
  .cpk-map-addr {{
    font-size: .86rem !important;
  }}
  .cpk-map-cta {{
    padding: 10px 16px !important;
    font-size: .82rem !important;
    flex: 1 1 auto;
    justify-content: center;
  }}
  .cpk-map-canvas .leaflet-control-zoom a {{
    width: 40px !important;
    height: 40px !important;
    line-height: 38px !important;
    font-size: 22px !important;
  }}
}}
</style>
'''


def tile_url_guncelle(html: str):
    """Tile URL'ine api_key ekle."""
    eski = (
        '"https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"'
    )
    yeni = (
        f'"https://{{s}}.basemaps.cartocdn.com/dark_all/'
        f'{{z}}/{{x}}/{{y}}{{r}}.png?api_key={API_KEY}"'
    )

    if API_KEY in html:
        return html, False, "api_key zaten ekli"

    if eski not in html:
        return html, False, "tile URL'i bulunamadı"

    yeni_html = html.replace(eski, yeni, 1)
    return yeni_html, True, "api_key tile URL'ine eklendi"


def tune_ekle(html: str):
    """Tasarım iyileştirmelerini ekle."""
    if MARKER_TUNE in html:
        return html, False, "tune zaten var"

    # </head> öncesine ekle
    idx = html.rfind("</head>")
    if idx == -1:
        # yoksa cpk-map-embed-style'in hemen ardına koy
        m = re.search(r'<style id="cpk-map-embed-style">.*?</style>', html, re.DOTALL)
        if not m:
            return html, False, "ekleme noktası yok"
        yeni = html[:m.end()] + TUNE_CSS + html[m.end():]
        return yeni, True, "tune bloğu eklendi (embed-style sonrası)"

    yeni = html[:idx] + TUNE_CSS + "\n" + html[idx:]
    return yeni, True, "tune bloğu eklendi (</head> öncesi)"


def adres_sadelestir(html: str):
    """Kart başlığındaki adresi sadeleştir."""
    # ADRES_L1 + ADRES_L2 -> sadece kısa adres
    eski = (
        "Yıldırım Mahallesi, Bosna Sokak No: 29/A<br>\n"
        "        Bayrampaşa / İstanbul"
    )
    yeni = (
        "Bosna Sokak No: 29/A, Bayrampaşa<br>\n"
        "        İstanbul"
    )
    if eski in html:
        return html.replace(eski, yeni, 1), True, "adres sadeleştirildi"
    # Alternatif format
    eski2 = "Yıldırım Mahallesi, Bosna Sokak No: 29/A<br>Bayrampaşa / İstanbul"
    yeni2 = "Bosna Sokak No: 29/A, Bayrampaşa<br>İstanbul"
    if eski2 in html:
        return html.replace(eski2, yeni2, 1), True, "adres sadeleştirildi"
    return html, False, "adres formatı bulunamadı (atlandı)"


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

    # 1) API key
    html, d1, m1 = tile_url_guncelle(html)
    print(f"[{'✓' if d1 else '·'}] API key: {m1}")

    # 2) Tune CSS
    html, d2, m2 = tune_ekle(html)
    print(f"[{'✓' if d2 else '·'}] Tune CSS: {m2}")

    # 3) Adres
    html, d3, m3 = adres_sadelestir(html)
    print(f"[{'✓' if d3 else '·'}] Adres: {m3}")

    if not (d1 or d2 or d3):
        print("\n[ATLA] Değişiklik yok."); return

    if args.dry_run:
        print(f"\n[DRY-RUN] Yazılmadı. Toplam +{len(html)} karakter eklenecek.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"index.html.{stamp}.bak"
    shutil.copy2(INDEX, yed)
    print(f"[YEDEK] backups/{yed.name}")

    INDEX.write_text(html, encoding="utf-8")
    print(f"[OK] index.html güncellendi ({len(html)} karakter)")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(INDEX)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Ana sayfa → İletişim → harita:")
    print("     • 'API key required' filigranı KAYBOLDU mu?")
    print("     • Harita daha büyük ve dengeli mi?")
    print("     • Pin daha görünür mü?")
    print("     • Zoom tuşları daha büyük mü (44px)?")


if __name__ == "__main__":
    main()