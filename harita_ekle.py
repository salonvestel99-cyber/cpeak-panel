#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_ekle.py — İletişim bölümüne tıklanabilir harita ekler.

- OpenStreetMap iframe: statik/görsel önizleme (API key gerekmez)
- Tıklanınca: Google Maps / Apple Maps uygulamasını açar
- Idempotent: marker varsa atlar
- Yedek + git commit + push

Kullanım:
  py harita_ekle.py --dry-run
  py harita_ekle.py --no-git
  py harita_ekle.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# ============================================================
# KONUM BİLGİLERİ (Google Maps linkinden alındı)
# ============================================================
ADRES_TAM = "Yıldırım Mahallesi, Bosna Sokak No:29 D:a, 34045 Bayrampaşa/İstanbul"
LAT = "41.0615227"
LON = "28.9003676"
# ============================================================

KOK = Path(__file__).resolve().parent
HEDEF = KOK / "templates" / "index.html"
YED_DIR = KOK / "backups"
MARKER = "cpk-map-embed"

COMMIT_MSG = """ui(iletişim): tıklanabilir harita eklendi

- OpenStreetMap iframe önizleme (Bayrampaşa / Yıldırım konumu)
- Tıklanınca Google Maps / Apple Maps uygulaması açılır
- Mobilde native uygulama, masaüstünde tarayıcı
- Otomatik yama: harita_ekle.py"""


def konum_link_uret():
    """Tıklanınca açılacak maps linki (mobilde native uygulamayı açar)."""
    q = f"{LAT},{LON}"
    return f"https://www.google.com/maps/search/?api=1&query={quote(q)}"


def osm_embed_url():
    """OpenStreetMap iframe src — dar bbox ile sokak seviyesinde zoom."""
    la, lo = float(LAT), float(LON)
    d = 0.0015  # ~150m yarıçap — sokak seviyesi
    bbox = f"{lo-d},{la-d},{lo+d},{la+d}"
    marker = f"{la},{lo}"
    return (
        "https://www.openstreetmap.org/export/embed.html"
        f"?bbox={bbox}&layer=mapnik&marker={marker}"
    )


HARITA_BLOK = f'''
      <a class="cpk-map" id="{MARKER}"
         href="{konum_link_uret()}"
         target="_blank" rel="noopener"
         aria-label="Konumu haritalar uygulamasında aç">
        <iframe
          class="cpk-map-frame"
          src="{osm_embed_url()}"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          title="C-Peak English konumu">
        </iframe>
        <span class="cpk-map-overlay" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
               stroke="currentColor" stroke-width="2" stroke-linecap="round"
               stroke-linejoin="round">
            <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <span>Haritalarda Aç</span>
        </span>
      </a>
<style id="{MARKER}-style">
.cpk-map {{
  display: block;
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 10;
  max-height: 360px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.08);
  background: #111;
  text-decoration: none;
  color: inherit;
  margin-top: 16px;
  transition: transform .18s ease, border-color .18s ease;
}}
.cpk-map:hover, .cpk-map:focus-visible {{
  transform: translateY(-2px);
  border-color: rgba(180,83,9,.55);
  outline: none;
}}
.cpk-map-frame {{
  width: 100%; height: 100%; border: 0; display: block;
  filter: invert(.92) hue-rotate(180deg) brightness(.92) contrast(.92);
  pointer-events: none;
}}
.cpk-map-overlay {{
  position: absolute;
  left: 50%; bottom: 14px;
  transform: translateX(-50%);
  display: inline-flex; align-items: center; gap: 8px;
  padding: 9px 16px;
  border-radius: 999px;
  background: rgba(0,0,0,.72);
  -webkit-backdrop-filter: blur(14px) saturate(160%);
  backdrop-filter: blur(14px) saturate(160%);
  border: 1px solid rgba(255,255,255,.18);
  color: #fff;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .84rem;
  font-weight: 600;
  letter-spacing: .01em;
  box-shadow: 0 6px 20px rgba(0,0,0,.35);
  pointer-events: none;
}}
.cpk-map-overlay svg {{ color: #f59e0b; }}
.cpk-map:hover .cpk-map-overlay {{
  background: rgba(180,83,9,.75);
  border-color: rgba(180,83,9,.9);
}}
@media (max-width: 640px) {{
  .cpk-map {{ aspect-ratio: 4 / 3; }}
  .cpk-map-overlay {{ font-size: .78rem; padding: 8px 14px; }}
}}
</style>
'''


def ekle(html: str):
    if MARKER in html:
        return html, False, "zaten mevcut"

    # Önce "Bosna Sokak" geçen paragrafı bul (en güvenilir)
    pattern = re.compile(
        r'(Bosna\s+Sokak[^<]*</[^>]+>)',
        re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(html)
    if m:
        ekle_noktasi = m.end(1)
        yeni = html[:ekle_noktasi] + HARITA_BLOK + html[ekle_noktasi:]
        return yeni, True, "'Bosna Sokak' paragrafından sonra eklendi"

    # Bulamazsa "ADRES" başlıklı bloğu ara
    pattern2 = re.compile(
        r'(<[^>]+>\s*ADRES\s*</[^>]+>.*?)'
        r'(</(?:div|section|article|dl|ul|aside)>)',
        re.DOTALL | re.IGNORECASE,
    )
    m2 = pattern2.search(html)
    if m2:
        ekle_noktasi = m2.end(1)
        yeni = html[:ekle_noktasi] + HARITA_BLOK + html[ekle_noktasi:]
        return yeni, True, "'ADRES' bölümünün altına eklendi"

    raise RuntimeError(
        "Uygun ekleme noktası bulunamadı. index.html'de 'Bosna Sokak' "
        "veya 'ADRES' kelimesi geçen bölümü kontrol et."
    )


# ============================================================
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

    if not HEDEF.exists():
        print(f"[HATA] {HEDEF} bulunamadı."); sys.exit(1)

    html = HEDEF.read_text(encoding="utf-8")
    print(f"[OK] index.html okundu ({len(html)} karakter)")

    try:
        yeni, degisti, mesaj = ekle(html)
    except RuntimeError as e:
        print(f"[HATA] {e}"); sys.exit(1)

    if not degisti:
        print(f"[ATLA] {mesaj}."); return

    print(f"[BİLGİ] {mesaj}")
    print(f"[BİLGİ] Karakter: {len(html)} → {len(yeni)} "
          f"({len(yeni)-len(html):+d})")
    print(f"[BİLGİ] Koordinat: {LAT}, {LON}")
    print(f"[BİLGİ] Tıklama linki: {konum_link_uret()}")

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"index.html.{stamp}.bak"
    shutil.copy2(HEDEF, yed)
    print(f"[YEDEK] backups/{yed.name}")

    HEDEF.write_text(yeni, encoding="utf-8")
    print(f"[OK] index.html güncellendi")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(HEDEF)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Ana sayfa → İletişim → harita görünür")
    print("  3) Haritaya tıkla → Google Maps açılır (mobilde native uygulama)")
    print("  4) Tema dark olduğu için harita da koyu görünür")


if __name__ == "__main__":
    main()