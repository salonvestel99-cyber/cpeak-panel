#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_duzelt.py — Haritayı yanlış yerden kaldır, doğru yere ekle.

Önceki script schema.org JSON-LD bloğunun içine ekledi (satır 45).
Bu script:
  1) Yanlış bloku siler
  2) Doğru yere (<p>Bosna Sokak...</p> sonrası) ekler
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ADRES_TAM = "Yıldırım Mahallesi, Bosna Sokak No:29 D:a, 34045 Bayrampaşa/İstanbul"
LAT = "41.0615227"
LON = "28.9003676"

KOK = Path(__file__).resolve().parent
HEDEF = KOK / "templates" / "index.html"
YED_DIR = KOK / "backups"
MARKER = "cpk-map-embed"

COMMIT_MSG = """fix(iletişim): harita doğru yere taşındı

- Önceki script schema.org JSON-LD içine eklemişti (satır 45)
- Yanlış blok silindi
- Doğru yere eklendi: İletişim bölümü ADRES paragrafı altına
- Otomatik yama: harita_duzelt.py"""


def konum_link_uret():
    q = f"{LAT},{LON}"
    return f"https://www.google.com/maps/search/?api=1&query={quote(q)}"


def osm_embed_url():
    la, lo = float(LAT), float(LON)
    d = 0.0015
    bbox = f"{lo-d},{la-d},{lo+d},{la+d}"
    return (
        "https://www.openstreetmap.org/export/embed.html"
        f"?bbox={bbox}&layer=mapnik&marker={la},{lo}"
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


def duzelt(html: str):
    """(yeni_html, degisti, mesaj)"""
    if MARKER not in html:
        return html, False, "harita bloğu yok"

    # 1) Mevcut bloğu bul ve sil (DOTALL ile, <a>...<style>...</style> arası)
    sil_pattern = re.compile(
        r'<a class="cpk-map" id="' + re.escape(MARKER) + r'".*?'
        r'<style id="' + re.escape(MARKER) + r'-style">.*?</style>',
        re.DOTALL,
    )
    m_sil = sil_pattern.search(html)
    if not m_sil:
        return html, False, "mevcut blok bulunamadı (regex eşleşmedi)"

    silinen_yer = html[:m_sil.start()].count("\n") + 1
    html = html[:m_sil.start()] + html[m_sil.end():]
    print(f"[BİLGİ] Eski blok silindi (satır {silinen_yer} civarı)")

    # 2) Doğru yere ekle: <p>...Bosna Sokak...</p> sonrası
    ekle_pattern = re.compile(
        r'<p>[^<]*Bosna\s+Sokak[^<]*(?:<[^>]+>[^<]*)*?</p>',
        re.DOTALL,
    )
    m = ekle_pattern.search(html)
    if not m:
        return html, False, "doğru ekleme noktası bulunamadı"

    ekle_satir = html[:m.end()].count("\n") + 1
    yeni = html[:m.end()] + HARITA_BLOK + html[m.end():]
    return yeni, True, f"doğru yere eklendi (satır {ekle_satir})"


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

    yeni, degisti, mesaj = duzelt(html)
    if not degisti:
        print(f"[ATLA] {mesaj}."); return

    print(f"[BİLGİ] {mesaj}")
    print(f"[BİLGİ] Karakter: {len(html)} → {len(yeni)} "
          f"({len(yeni)-len(html):+d})")

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

    # Doğrulama
    print("\n[DOĞRULAMA]")
    for i, s in enumerate(yeni.split("\n")):
        if "cpk-map-embed" in s and "<a" in s:
            print(f"  ✓ satır {i+1}: harita <a> bloğu")
        if "Bosna Sokak" in s and "<p>" in s:
            print(f"  ✓ satır {i+1}: adres paragrafı")
    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Ana sayfa → İletişim → harita görünür")
    print("  3) Tıkla → Google Maps açılır")


if __name__ == "__main__":
    main()