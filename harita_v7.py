#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_v7.py — Adres tekrarını kaldır + OSM dark filter

1) Harita kart başlığındaki "KONUM + adres" kaldırıldı
   → Sadece harita + üstünde "Yol Tarifi" butonu
2) CartoDB → OpenStreetMap + CSS dark filter
   → API key gerekmez, filigran yok
3) Tune CSS basitleştirildi

Kullanım:
  py harita_v7.py --dry-run
  py harita_v7.py --no-git
  py harita_v7.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
INDEX = KOK / "templates" / "index.html"
YED_DIR = KOK / "backups"
MARKER = "cpk-map-v7"

COMMIT_MSG = """fix(harita): adres tekrarı kaldırıldı + OSM dark filter

- Harita kartındaki "KONUM + adres" başlığı kaldırıldı (tekrar vardı)
- Yol Tarifi butonu harita üstüne overlay olarak taşındı
- CartoDB → OpenStreetMap + CSS invert filter
  (API key gerekmez, filigran yok, sonsuza kadar ücretsiz)
- Tune CSS sadeleştirildi
- Otomatik yama: harita_v7.py"""


def html_yenile(html: str):
    """Eski harita bloğunu tamamen yenile."""

    # Tüm eski harita bloklarını temizle: embed + tune + style'lar
    sil_patternler = [
        # Harita section'ı (wrap)
        r'<section class="cpk-map-wrap" id="cpk-map-embed">.*?</section>',
        # Eski OSM iframe (a.cpk-map)
        r'<a class="cpk-map" id="cpk-map-embed".*?</a>',
        # Init JS
        r'<script id="cpk-map-init-js">.*?</script>',
        # Stil blokları
        r'<style id="cpk-map-embed-style">.*?</style>',
        r'<style id="cpk-map-tune-v2">.*?</style>',
    ]
    onceki = html
    for pat in sil_patternler:
        html = re.sub(pat, "", html, flags=re.DOTALL)

    if html == onceki:
        print("[BİLGİ] Eski blok bulunamadı — devam ediliyor")

    # Yeni bloğu ekle (Bosna Sokak paragrafından sonra)
    ekle = re.compile(
        r'<p>[^<]*Bosna\s+Sokak[^<]*(?:<[^>]+>[^<]*)*?</p>',
        re.DOTALL,
    )
    m = ekle.search(html)
    if not m:
        return html, False, "ekleme noktası bulunamadı"

    yeni = html[:m.end()] + YENI_BLOK + html[m.end():]
    return yeni, True, "harita v7 eklendi"


YENI_BLOK = '''
<div class="cpk-map-card" id="cpk-map-embed">
  <div id="cpk-map-canvas" class="cpk-map-canvas"
       data-lat="41.0615227" data-lon="28.9003676"
       role="region" aria-label="C-Peak English konumu"></div>
  <a class="cpk-map-cta"
     href="https://www.google.com/maps/dir/?api=1&destination=41.0615227,28.9003676"
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

<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin="">
<script defer
        src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
<script id="cpk-map-init-js">
(function () {
  "use strict";
  if (window.__cpkMapV7) return;
  window.__cpkMapV7 = true;

  var LOG = function () {
    try {
      var a = [].slice.call(arguments);
      a.unshift("%c[CPK-Map]", "color:#f59e0b;font-weight:bold");
      console.log.apply(console, a);
    } catch (e) {}
  };

  var deneme = 0;
  function leafletBekle() {
    if (window.L) { setTimeout(kur, 40); return; }
    if (++deneme > 40) { LOG("Leaflet yüklenmedi"); return; }
    setTimeout(leafletBekle, 100);
  }

  function kur() {
    var el = document.getElementById("cpk-map-canvas");
    if (!el) { LOG("#cpk-map-canvas yok"); return; }

    var lat = parseFloat(el.dataset.lat);
    var lon = parseFloat(el.dataset.lon);

    var map = L.map(el, {
      center: [lat, lon],
      zoom: 17,
      minZoom: 13,
      maxZoom: 19,
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true
    });

    /* OSM standard tile — dark filter CSS'te */
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      subdomains: "abc",
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'
    }).addTo(map);

    var pin = L.divIcon({
      className: "cpk-map-pin",
      html: '<span class="cpk-map-pin-pulse"></span>' +
            '<span class="cpk-map-pin-dot"></span>',
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });
    L.marker([lat, lon], { icon: pin }).addTo(map);

    if (map.zoomControl) map.zoomControl.setPosition("bottomright");

    setTimeout(function () { map.invalidateSize(); }, 120);

    window.__cpkMap = map;
    LOG("Hazır ✓ (OSM dark filter)");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", leafletBekle);
  } else {
    leafletBekle();
  }
})();
</script>

<style id="cpk-map-v7-style">
/* ---- Harita kart ---- */
.cpk-map-card {
  position: relative;
  margin-top: 22px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.09);
  box-shadow:
    0 24px 60px -24px rgba(0,0,0,.7),
    0 4px 16px rgba(0,0,0,.25);
  background: #0f0f12;
}

.cpk-map-canvas {
  width: 100%;
  aspect-ratio: 16 / 10;
  min-height: 300px;
  background: #0f0f12;
}

.cpk-map-canvas .leaflet-container {
  background: #0f0f12 !important;
  font-family: 'Inter', system-ui, sans-serif !important;
}

/* --- Dark filter: OSM tile'larını ters çevirip koyu göster --- */
.cpk-map-canvas .leaflet-tile-pane {
  filter: invert(1) hue-rotate(180deg) brightness(.85) contrast(1.08) saturate(.75);
}

/* --- Zoom kontrolleri (sağ altta, 44px, dark glass) --- */
.cpk-map-canvas .leaflet-control-zoom {
  border: 0 !important;
  box-shadow: 0 10px 28px -6px rgba(0,0,0,.6) !important;
  margin: 14px !important;
}
.cpk-map-canvas .leaflet-control-zoom a {
  width: 44px !important;
  height: 44px !important;
  line-height: 42px !important;
  background: rgba(20,20,24,.92) !important;
  color: #f59e0b !important;
  border: 1px solid rgba(255,255,255,.16) !important;
  -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
  backdrop-filter: blur(14px) saturate(160%) !important;
  font-size: 24px !important;
  font-weight: 500 !important;
  transition: background .15s ease, color .15s ease, transform .12s ease;
}
.cpk-map-canvas .leaflet-control-zoom a:first-child {
  border-radius: 12px 12px 0 0 !important;
}
.cpk-map-canvas .leaflet-control-zoom a:last-child {
  border-radius: 0 0 12px 12px !important;
  border-top: 0 !important;
}
.cpk-map-canvas .leaflet-control-zoom a:hover,
.cpk-map-canvas .leaflet-control-zoom a:focus {
  background: rgba(180,83,9,.95) !important;
  color: #fff !important;
}
.cpk-map-canvas .leaflet-control-zoom a:active { transform: scale(.94); }

/* --- Attribution --- */
.cpk-map-canvas .leaflet-control-attribution {
  background: rgba(0,0,0,.7) !important;
  color: rgba(255,255,255,.5) !important;
  font-size: 10px !important;
  padding: 3px 8px !important;
  border: 0 !important;
  border-radius: 8px 0 0 0 !important;
}
.cpk-map-canvas .leaflet-control-attribution a {
  color: rgba(245,158,11,.85) !important;
}

/* --- Pin --- */
.cpk-map-pin { position: relative; }
.cpk-map-pin-dot {
  position: absolute; left: 50%; top: 50%;
  width: 22px; height: 22px;
  transform: translate(-50%,-50%);
  background: #f59e0b;
  border: 3px solid #18181b;
  border-radius: 50%;
  box-shadow:
    0 0 0 3px rgba(245,158,11,.4),
    0 6px 20px rgba(0,0,0,.6);
  z-index: 2;
}
.cpk-map-pin-pulse {
  position: absolute; left: 50%; top: 50%;
  width: 56px; height: 56px;
  transform: translate(-50%,-50%);
  background: rgba(245,158,11,.32);
  border-radius: 50%;
  animation: cpk-pin-pulse 2s ease-out infinite;
  z-index: 1;
  pointer-events: none;
}
@keyframes cpk-pin-pulse {
  0%   { transform: translate(-50%,-50%) scale(.35); opacity: .9; }
  70%  { transform: translate(-50%,-50%) scale(1.3); opacity: 0; }
  100% { transform: translate(-50%,-50%) scale(1.3); opacity: 0; }
}

/* --- Yol Tarifi butonu — haritanın üstünde, sol altta --- */
.cpk-map-cta {
  position: absolute;
  left: 16px;
  bottom: 16px;
  z-index: 500;
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
  color: #18181b;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .84rem; font-weight: 700;
  letter-spacing: .01em;
  text-decoration: none;
  box-shadow:
    0 10px 26px -8px rgba(245,158,11,.7),
    0 3px 8px rgba(0,0,0,.35);
  transition: transform .15s ease, box-shadow .15s ease;
  -webkit-tap-highlight-color: transparent;
}
.cpk-map-cta:hover, .cpk-map-cta:focus-visible {
  transform: translateY(-2px);
  box-shadow:
    0 14px 32px -8px rgba(245,158,11,.85),
    0 4px 10px rgba(0,0,0,.4);
  outline: none;
}
.cpk-map-cta:active { transform: translateY(0); }
.cpk-map-cta svg { stroke: currentColor; flex-shrink: 0; }

@media (max-width: 640px) {
  .cpk-map-card { border-radius: 16px; margin-top: 18px; }
  .cpk-map-canvas {
    aspect-ratio: 4 / 3;
    min-height: 280px;
  }
  .cpk-map-canvas .leaflet-control-zoom a {
    width: 40px !important;
    height: 40px !important;
    line-height: 38px !important;
    font-size: 22px !important;
  }
  .cpk-map-cta {
    left: 12px; bottom: 12px;
    padding: 10px 15px;
    font-size: .8rem;
    gap: 6px;
  }
  .cpk-map-cta svg { width: 13px; height: 13px; }
}
</style>
'''


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

    yeni, degisti, mesaj = html_yenile(html)
    print(f"[{'✓' if degisti else '·'}] {mesaj}")

    if not degisti:
        return

    print(f"[BİLGİ] Karakter: {len(html)} → {len(yeni)} "
          f"({len(yeni)-len(html):+d})")

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı.")
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
    print("  2) Ana sayfa → İletişim:")
    print("     • Haritada filigran YOK")
    print("     • Koyu, temiz görünüm")
    print("     • Sol altta 'Yol Tarifi' butonu")
    print("     • Adres TEKRARI YOK (sadece solda 'ADRES' kolonu var)")
    print("     • Zoom +/- sağ altta, 44px büyük")
    print("     • Pin pulse animasyonu")


if __name__ == "__main__":
    main()