#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_v2.py — İki düzeltme:
  1) security_headers.py CSP'ye frame-src ekle (OSM iframe için)
  2) index.html harita bloğunu yenile (daha zarif tasarım)

Kullanım:
  py harita_v2.py --dry-run
  py harita_v2.py --no-git
  py harita_v2.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

LAT = "41.0615227"
LON = "28.9003676"

KOK = Path(__file__).resolve().parent
INDEX = KOK / "templates" / "index.html"
SEC = KOK / "security_headers.py"
YED_DIR = KOK / "backups"
MARKER = "cpk-map-embed"

COMMIT_MSG = """fix(harita): CSP frame-src + daha zarif harita tasarımı

- security_headers.py: CSP'ye frame-src openstreetmap.org eklendi
- index.html: harita bloğu yenilendi (daha büyük, minimal overlay)
- Overlay artık sağ altta, sadece ikon (mobilde sade)
- Otomatik yama: harita_v2.py"""


# ============================================================
# YENİ HARİTA BLOK
# ============================================================
HARITA_BLOK = f'''
      <a class="cpk-map" id="{MARKER}"
         href="https://www.google.com/maps/search/?api=1&query={LAT},{LON}"
         target="_blank" rel="noopener"
         aria-label="Konumu haritalar uygulamasında aç">
        <iframe
          class="cpk-map-frame"
          src="https://www.openstreetmap.org/export/embed.html?bbox=28.8988676%2C41.0600227%2C28.9018676%2C41.0630227&amp;layer=mapnik&amp;marker={LAT}%2C{LON}"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          title="C-Peak English konumu">
        </iframe>
        <span class="cpk-map-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none"
               stroke="currentColor" stroke-width="2.2" stroke-linecap="round"
               stroke-linejoin="round">
            <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
        </span>
      </a>
<style id="{MARKER}-style">
.cpk-map {{
  display: block;
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  max-height: 420px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.10);
  background: #1a1a1d;
  text-decoration: none;
  color: inherit;
  margin-top: 18px;
  transition: border-color .2s ease, transform .2s ease;
  -webkit-tap-highlight-color: transparent;
}}
.cpk-map:hover, .cpk-map:focus-visible {{
  border-color: rgba(180,83,9,.55);
  transform: translateY(-2px);
  outline: none;
}}
.cpk-map-frame {{
  width: 100%; height: 100%; border: 0; display: block;
  /* Koyu tema — haritayı hafifçe karart */
  filter: brightness(.88) contrast(1.05) saturate(.9);
  pointer-events: none;
}}
/* Sağ altta küçük, zarif "haritada aç" rozeti */
.cpk-map-badge {{
  position: absolute;
  right: 12px; bottom: 12px;
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px;
  border-radius: 50%;
  background: rgba(0,0,0,.78);
  -webkit-backdrop-filter: blur(12px) saturate(160%);
  backdrop-filter: blur(12px) saturate(160%);
  border: 1px solid rgba(255,255,255,.20);
  color: #f59e0b;
  box-shadow: 0 6px 18px rgba(0,0,0,.35);
  transition: background .18s ease, border-color .18s ease, transform .18s ease;
}}
.cpk-map:hover .cpk-map-badge,
.cpk-map:focus-visible .cpk-map-badge {{
  background: rgba(180,83,9,.9);
  border-color: rgba(180,83,9,1);
  color: #fff;
  transform: scale(1.05);
}}
@media (max-width: 640px) {{
  .cpk-map {{ aspect-ratio: 5 / 4; border-radius: 14px; }}
  .cpk-map-badge {{ width: 32px; height: 32px; right: 10px; bottom: 10px; }}
}}
</style>
'''


# ============================================================
# 1) HTML — haritayı yenile
# ============================================================
def harita_yenile(html: str):
    """Eski harita bloğunu sil, yenisini aynı yere ekle."""
    if MARKER not in html:
        return html, False, "harita bloğu yok"

    # Eski bloğu sil
    sil = re.compile(
        r'<a class="cpk-map" id="' + re.escape(MARKER) + r'".*?'
        r'<style id="' + re.escape(MARKER) + r'-style">.*?</style>',
        re.DOTALL,
    )
    m_sil = sil.search(html)
    if not m_sil:
        return html, False, "mevcut blok bulunamadı"
    html = html[:m_sil.start()] + html[m_sil.end():]

    # Doğru yere ekle: <p>...Bosna Sokak...</p> sonrası
    ekle = re.compile(
        r'<p>[^<]*Bosna\s+Sokak[^<]*(?:<[^>]+>[^<]*)*?</p>',
        re.DOTALL,
    )
    m = ekle.search(html)
    if not m:
        return html, False, "doğru ekleme noktası yok"
    yeni = html[:m.end()] + HARITA_BLOK + html[m.end():]
    return yeni, True, "harita yenilendi"


# ============================================================
# 2) CSP — frame-src ekle
# ============================================================
CSP_FRAME_LINE = (
    '                "frame-src \'self\' '
    'https://www.openstreetmap.org https://www.google.com",\n'
)


def csp_guncelle(ic: str):
    if "openstreetmap.org" in ic:
        return ic, False, "CSP'de OSM zaten var"

    # "frame-ancestors" satırından önce ekle
    pat = re.compile(r'(\s*)"frame-ancestors\s+\'self\'\s*",?', re.MULTILINE)
    m = pat.search(ic)
    if m:
        yeni = ic[:m.start()] + "\n" + CSP_FRAME_LINE.rstrip("\n") + ic[m.start():]
        return yeni, True, "frame-src eklendi (frame-ancestors'tan önce)"

    # frame-ancestors yoksa — "object-src" öncesine ekle
    pat2 = re.compile(r'(\s*)"object-src\s', re.MULTILINE)
    m2 = pat2.search(ic)
    if m2:
        yeni = ic[:m2.start()] + "\n" + CSP_FRAME_LINE.rstrip("\n") + ic[m2.start():]
        return yeni, True, "frame-src eklendi (object-src'tan önce)"

    return ic, False, "CSP bulunamadı — elle eklenecek"


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

    if not INDEX.exists():
        print(f"[HATA] {INDEX} bulunamadı."); sys.exit(1)

    degis = []

    # 1) HTML
    html = INDEX.read_text(encoding="utf-8")
    print(f"[OK] index.html okundu ({len(html)} karakter)")
    yeni_html, html_degisti, html_mesaj = harita_yenile(html)
    print(f"[{'✓' if html_degisti else '·'}] HTML: {html_mesaj}")
    if html_degisti:
        degis.append((INDEX, yeni_html))

    # 2) CSP
    if SEC.exists():
        sec = SEC.read_text(encoding="utf-8")
        yeni_sec, csp_degisti, csp_mesaj = csp_guncelle(sec)
        print(f"[{'✓' if csp_degisti else '·'}] CSP: {csp_mesaj}")
        if csp_degisti:
            degis.append((SEC, yeni_sec))
    else:
        print(f"[UYARI] {SEC} yok — CSP güncellenemedi")

    if not degis:
        print("\n[ATLA] Değişiklik yok."); return

    if args.dry_run:
        print(f"\n[DRY-RUN] {len(degis)} dosya değişecek:")
        for y, _ in degis:
            print(f"  ~ {y.relative_to(KOK)}")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for yol, icerik in degis:
        yed = YED_DIR / f"{yol.name}.{stamp}.bak"
        shutil.copy2(yol, yed)
        print(f"[YEDEK] backups/{yed.name}")
        yol.write_text(icerik, encoding="utf-8")
        print(f"[OK] {yol.relative_to(KOK)} güncellendi")

    yollar = [y for y, _ in degis]
    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(*yollar)

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Ana sayfa → İletişim → harita YÜKLENMİŞ olmalı (gri kutu değil)")
    print("  3) Sağ altta küçük pin rozeti — tıklanabilir")
    print("  4) Tıkla → Google Maps açılır")
    print("  5) Masaüstünde de aynı görünüm")


if __name__ == "__main__":
    main()