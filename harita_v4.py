#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_v4.py — Leaflet + CartoDB dark tile, premium harita

1) index.html: OSM iframe → Leaflet + dark tile (etkileşimli)
2) security_headers.py + security.py: style-src'ye cdn.jsdelivr.net ekle

Kullanım:
  py harita_v4.py --dry-run
  py harita_v4.py --no-git
  py harita_v4.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

LAT = "41.0615227"
LON = "28.9003676"
ADRES_L1 = "Yıldırım Mahallesi, Bosna Sokak No: 29/A"
ADRES_L2 = "Bayrampaşa / İstanbul"

KOK = Path(__file__).resolve().parent
INDEX = KOK / "templates" / "index.html"
SEC = KOK / "security_headers.py"
SEC2 = KOK / "security.py"
YED_DIR = KOK / "backups"
MARKER = "cpk-map-embed"
MARKER_JS = "cpk-map-init-js"

COMMIT_MSG = """feat(harita): Leaflet + dark tile premium harita

- OSM iframe yerine Leaflet + CartoDB Dark Matter tile
- Kart başlığı: KONUM eyebrow, adres, "Yol Tarifi" butonu
- Custom pin: pulse animation, amber/copper tema
- Zoom kontrolleri sağ altta, dark glass görünüm
- Pan/zoom etkileşimli (pointer-events auto)
- CSP: style-src'ye cdn.jsdelivr.net eklendi
- Otomatik yama: harita_v4.py"""


YENI_HTML = f'''
<section class="cpk-map-wrap" id="{MARKER}">
  <div class="cpk-map-head">
    <div class="cpk-map-info">
      <span class="cpk-map-eyebrow">KONUM</span>
      <p class="cpk-map-addr">
        {ADRES_L1}<br>
        {ADRES_L2}
      </p>
    </div>
    <a class="cpk-map-cta"
       href="https://www.google.com/maps/dir/?api=1&destination={LAT},{LON}"
       target="_blank" rel="noopener"
       aria-label="Yol tarifi al">
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none"
           stroke="currentColor" stroke-width="2.2" stroke-linecap="round"
           stroke-linejoin="round" aria-hidden="true">
        <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"></path>
        <circle cx="12" cy="10" r="3"></circle>
      </svg>
      <span>Yol Tarifi</span>
    </a>
  </div>
  <div id="cpk-map-canvas" class="cpk-map-canvas"
       data-lat="{LAT}" data-lon="{LON}"
       role="region" aria-label="C-Peak English konumu"></div>
</section>

<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin="">
<script defer
        src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
<script id="{MARKER_JS}">
(function () {{
  "use strict";
  if (window.__cpkMapInit) return;
  window.__cpkMapInit = true;

  function init() {{
    var el = document.getElementById("cpk-map-canvas");
    if (!el || !window.L) return;
    var lat = parseFloat(el.dataset.lat) || {LAT};
    var lon = parseFloat(el.dataset.lon) || {LON};

    var map = L.map(el, {{
      center: [lat, lon],
      zoom: 17,
      minZoom: 12,
      maxZoom: 19,
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true,
      tap: true
    }});

    L.tileLayer(
      "https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png",
      {{
        maxZoom: 19,
        subdomains: "abcd",
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> ' +
          '&copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>'
      }}
    ).addTo(map);

    var pin = L.divIcon({{
      className: "cpk-map-pin",
      html: '<span class="cpk-map-pin-pulse"></span>' +
            '<span class="cpk-map-pin-dot"></span>',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    }});
    L.marker([lat, lon], {{ icon: pin }}).addTo(map);

    if (map.zoomControl) map.zoomControl.setPosition("bottomright");
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", function () {{
      setTimeout(init, 80);
    }});
  }} else {{
    setTimeout(init, 80);
  }}
}})();
</script>
<style id="{MARKER}-style">
.cpk-map-wrap {{
  margin-top: 22px;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255,255,255,.035), rgba(255,255,255,.012));
  border: 1px solid rgba(255,255,255,.09);
  box-shadow:
    0 24px 60px -24px rgba(0,0,0,.7),
    0 4px 16px rgba(0,0,0,.25);
}}
.cpk-map-head {{
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; flex-wrap: wrap;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255,255,255,.06);
  background: rgba(0,0,0,.18);
}}
.cpk-map-info {{ min-width: 0; }}
.cpk-map-eyebrow {{
  display: inline-block;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .66rem; font-weight: 700;
  letter-spacing: .2em;
  color: #f59e0b;
  margin-bottom: 5px;
}}
.cpk-map-addr {{
  margin: 0;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .88rem; line-height: 1.45;
  color: rgba(255,255,255,.78);
}}
.cpk-map-cta {{
  display: inline-flex; align-items: center; gap: 7px;
  padding: 9px 15px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
  color: #18181b;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .8rem; font-weight: 700;
  letter-spacing: .01em;
  text-decoration: none;
  white-space: nowrap;
  box-shadow:
    0 8px 22px -8px rgba(245,158,11,.6),
    0 2px 6px rgba(0,0,0,.3);
  transition: transform .15s ease, box-shadow .15s ease;
  -webkit-tap-highlight-color: transparent;
}}
.cpk-map-cta:hover, .cpk-map-cta:focus-visible {{
  transform: translateY(-1px);
  box-shadow:
    0 12px 28px -8px rgba(245,158,11,.75),
    0 3px 8px rgba(0,0,0,.35);
  outline: none;
}}
.cpk-map-cta:active {{ transform: translateY(0); }}
.cpk-map-cta svg {{ stroke: currentColor; }}

.cpk-map-canvas {{
  width: 100%;
  aspect-ratio: 16 / 10;
  background: #0f0f12;
  position: relative;
  z-index: 0;
}}
.cpk-map-canvas .leaflet-container {{
  background: #0f0f12 !important;
  font-family: 'Inter', system-ui, sans-serif !important;
}}
.cpk-map-canvas .leaflet-control-zoom {{
  border: 0 !important;
  box-shadow: 0 8px 24px -6px rgba(0,0,0,.55) !important;
  margin: 12px !important;
}}
.cpk-map-canvas .leaflet-control-zoom a {{
  width: 36px !important; height: 36px !important;
  line-height: 34px !important;
  background: rgba(20,20,24,.94) !important;
  color: #f59e0b !important;
  border: 1px solid rgba(255,255,255,.16) !important;
  -webkit-backdrop-filter: blur(12px) saturate(160%) !important;
  backdrop-filter: blur(12px) saturate(160%) !important;
  font-size: 20px !important;
  font-weight: 600 !important;
  transition: background .15s ease, color .15s ease, transform .12s ease;
}}
.cpk-map-canvas .leaflet-control-zoom a:first-child {{
  border-radius: 10px 10px 0 0 !important;
}}
.cpk-map-canvas .leaflet-control-zoom a:last-child {{
  border-radius: 0 0 10px 10px !important;
  border-top: 0 !important;
}}
.cpk-map-canvas .leaflet-control-zoom a:hover,
.cpk-map-canvas .leaflet-control-zoom a:focus {{
  background: rgba(180,83,9,.95) !important;
  color: #fff !important;
}}
.cpk-map-canvas .leaflet-control-zoom a:active {{
  transform: scale(.95);
}}
.cpk-map-canvas .leaflet-control-attribution {{
  background: rgba(0,0,0,.7) !important;
  color: rgba(255,255,255,.55) !important;
  font-size: 10px !important;
  padding: 3px 8px !important;
  border-radius: 8px 0 0 0 !important;
  border: 0 !important;
}}
.cpk-map-canvas .leaflet-control-attribution a {{
  color: rgba(245,158,11,.85) !important;
}}

.cpk-map-pin {{ position: relative; }}
.cpk-map-pin-dot {{
  position: absolute; left: 50%; top: 50%;
  width: 16px; height: 16px;
  transform: translate(-50%,-50%);
  background: #f59e0b;
  border: 2.5px solid #18181b;
  border-radius: 50%;
  box-shadow:
    0 0 0 2px rgba(245,158,11,.35),
    0 4px 14px rgba(0,0,0,.55);
  z-index: 2;
}}
.cpk-map-pin-pulse {{
  position: absolute; left: 50%; top: 50%;
  width: 40px; height: 40px;
  transform: translate(-50%,-50%);
  background: rgba(245,158,11,.32);
  border-radius: 50%;
  animation: cpk-pin-pulse 1.9s ease-out infinite;
  z-index: 1;
  pointer-events: none;
}}
@keyframes cpk-pin-pulse {{
  0%   {{ transform: translate(-50%,-50%) scale(.35); opacity: .9; }}
  70%  {{ transform: translate(-50%,-50%) scale(1.35); opacity: 0; }}
  100% {{ transform: translate(-50%,-50%) scale(1.35); opacity: 0; }}
}}

@media (max-width: 640px) {{
  .cpk-map-wrap {{ border-radius: 16px; margin-top: 18px; }}
  .cpk-map-head {{ padding: 14px 16px; gap: 12px; }}
  .cpk-map-addr {{ font-size: .84rem; }}
  .cpk-map-cta {{ padding: 8px 13px; font-size: .76rem; gap: 6px; }}
  .cpk-map-cta svg {{ width: 13px; height: 13px; }}
  .cpk-map-canvas {{ aspect-ratio: 5 / 4; }}
}}
</style>
'''


def csp_style_ekle(ic: str):
    """(yeni, degisti, mesaj)"""
    # security_headers.py — liste halinde string'ler
    pat1 = re.compile(
        r'("style-src \'self\' \'unsafe-inline\' https://fonts\.googleapis\.com)(")',
    )
    m = pat1.search(ic)
    if m:
        if "cdn.jsdelivr.net" in m.group(1):
            return ic, False, "style-src'de jsdelivr zaten var"
        yeni = ic[:m.end(1)] + " https://cdn.jsdelivr.net" + ic[m.end(1):]
        return yeni, True, "style-src'ye jsdelivr eklendi"

    # Talisman — "style-src": "..."
    pat2 = re.compile(r'("style-src"\s*:\s*")([^"]*)(")')
    m2 = pat2.search(ic)
    if m2:
        if "cdn.jsdelivr.net" in m2.group(2):
            return ic, False, "Talisman style-src'de zaten var"
        yeni_deger = m2.group(2).rstrip() + " https://cdn.jsdelivr.net"
        yeni = ic[:m2.start()] + m2.group(1) + yeni_deger + m2.group(3) + ic[m2.end():]
        return yeni, True, "Talisman style-src'ye eklendi"

    # Talisman — "style-src": [...]
    pat3 = re.compile(r'("style-src"\s*:\s*\[)(.*?)(\])', re.DOTALL)
    m3 = pat3.search(ic)
    if m3:
        if "cdn.jsdelivr.net" in m3.group(2):
            return ic, False, "Talisman style-src (liste) zaten var"
        icerik = m3.group(2).rstrip()
        if not icerik.endswith(","):
            icerik += ","
        icerik += ' "https://cdn.jsdelivr.net"'
        yeni = ic[:m3.start()] + m3.group(1) + icerik + m3.group(3) + ic[m3.end():]
        return yeni, True, "Talisman style-src (liste) eklendi"

    return ic, False, "style-src bulunamadı"


def html_yenile(html: str):
    if MARKER_JS in html and "leaflet" in html.lower():
        return html, False, "Leaflet zaten kurulu"

    # Eski blok varsa sil
    sil = re.compile(
        r'<a class="cpk-map" id="' + re.escape(MARKER) + r'".*?'
        r'<style id="' + re.escape(MARKER) + r'-style">.*?</style>',
        re.DOTALL,
    )
    m_sil = sil.search(html)
    if m_sil:
        html = html[:m_sil.start()] + html[m_sil.end():]
        print("[BİLGİ] Eski OSM bloğu silindi")

    # Bosna Sokak paragrafından sonra yeni HTML
    ekle = re.compile(
        r'<p>[^<]*Bosna\s+Sokak[^<]*(?:<[^>]+>[^<]*)*?</p>',
        re.DOTALL,
    )
    m = ekle.search(html)
    if not m:
        return html, False, "ekleme noktası bulunamadı"
    yeni = html[:m.end()] + YENI_HTML + html[m.end():]
    return yeni, True, "Leaflet haritası eklendi"


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

    degis = []

    html = INDEX.read_text(encoding="utf-8")
    yeni_html, h_degisti, h_mesaj = html_yenile(html)
    print(f"[{'✓' if h_degisti else '·'}] HTML: {h_mesaj}")
    if h_degisti:
        degis.append((INDEX, yeni_html))

    if SEC.exists():
        sec = SEC.read_text(encoding="utf-8")
        yeni_sec, s_degisti, s_mesaj = csp_style_ekle(sec)
        print(f"[{'✓' if s_degisti else '·'}] security_headers.py: {s_mesaj}")
        if s_degisti:
            degis.append((SEC, yeni_sec))

    if SEC2.exists():
        sec2 = SEC2.read_text(encoding="utf-8")
        yeni_sec2, s2_degisti, s2_mesaj = csp_style_ekle(sec2)
        print(f"[{'✓' if s2_degisti else '·'}] security.py: {s2_mesaj}")
        if s2_degisti:
            degis.append((SEC2, yeni_sec2))

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
    print("  2) Ana sayfa → İletişim → harita:")
    print("     • Dark zemin, premium görünüm")
    print("     • Pin pulse animasyonu")
    print("     • Sağ altta +/- kontrolleri ÇALIŞIR")
    print("     • Sürükle → pan")
    print("     • 'Yol Tarifi' → Google Maps Directions")
    print("  3) Masaüstünde de aynı")


if __name__ == "__main__":
    main()