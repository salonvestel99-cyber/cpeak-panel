#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harita_v5.py — Leaflet yüklenme sorununu kökten çöz.

1) security.py: Talisman CSP'yi kapat (content_security_policy=None)
   → tek CSP kalsın, security_headers.py sahibi olsun
2) index.html: init script'i Leaflet'i bekleyen + log basan versiyonla değiştir

Kullanım:
  py harita_v5.py --dry-run
  py harita_v5.py --no-git
  py harita_v5.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

LAT = "41.0615227"
LON = "28.9003676"

KOK = Path(__file__).resolve().parent
INDEX = KOK / "templates" / "index.html"
SEC2 = KOK / "security.py"
YED_DIR = KOK / "backups"
MARKER_JS = "cpk-map-init-js"

COMMIT_MSG = """fix(harita): Leaflet yüklemesi — Talisman CSP kapatıldı

- security.py: Talisman content_security_policy=None
  (tek CSP kalsın, security_headers.py sahibi)
- index.html: Leaflet'i bekleyen + log basan yeni init script
- Konsol [CPK-Map] logları ile teşhis kolay
- Otomatik yama: harita_v5.py"""


YENI_JS = '''<script id="cpk-map-init-js">
(function () {
  "use strict";
  if (window.__cpkMapInitV5) return;
  window.__cpkMapInitV5 = true;

  var LOG = function () {
    try {
      var a = [].slice.call(arguments);
      a.unshift("%c[CPK-Map]", "color:#f59e0b;font-weight:bold");
      console.log.apply(console, a);
    } catch (e) {}
  };
  LOG("init script yüklendi");

  var deneme = 0;
  var MAX = 40; // 4 sn

  function leafletBekle() {
    if (window.L) {
      LOG("Leaflet hazır");
      setTimeout(haritaKur, 50);
      return;
    }
    deneme++;
    if (deneme >= MAX) {
      LOG("HATA: Leaflet 4sn içinde yüklenmedi (CDN veya CSP engeli)");
      return;
    }
    if (deneme % 10 === 0) LOG("Leaflet bekleniyor... (" + deneme + ")");
    setTimeout(leafletBekle, 100);
  }

  function haritaKur() {
    try {
      var el = document.getElementById("cpk-map-canvas");
      if (!el) { LOG("HATA: #cpk-map-canvas yok"); return; }
      var lat = parseFloat(el.dataset.lat) || 41.0615227;
      var lon = parseFloat(el.dataset.lon) || 28.9003676;
      LOG("Konum:", lat, lon);

      var w = el.offsetWidth, h = el.offsetHeight;
      LOG("Container boyut:", w + "x" + h);
      if (w === 0 || h === 0) {
        LOG("Container boyutu sıfır → 200ms sonra tekrar");
        setTimeout(haritaKur, 200);
        return;
      }

      var map = L.map(el, {
        center: [lat, lon],
        zoom: 17,
        minZoom: 12,
        maxZoom: 19,
        scrollWheelZoom: false,
        zoomControl: true,
        attributionControl: true
      });
      LOG("Map oluşturuldu");

      var tile = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          maxZoom: 19,
          subdomains: "abcd",
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OSM</a> ' +
            '&copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>'
        }
      );
      tile.on("tileerror", function (e) {
        LOG("tile error:", e.tile && e.tile.src);
      });
      tile.addTo(map);
      LOG("Tile layer eklendi");

      var pin = L.divIcon({
        className: "cpk-map-pin",
        html: '<span class="cpk-map-pin-pulse"></span>' +
              '<span class="cpk-map-pin-dot"></span>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });
      L.marker([lat, lon], { icon: pin }).addTo(map);
      LOG("Pin eklendi");

      if (map.zoomControl) map.zoomControl.setPosition("bottomright");

      setTimeout(function () {
        map.invalidateSize();
        LOG("invalidateSize çağrıldı");
      }, 150);

      window.__cpkMap = map;
      LOG("Hazır ✓");
    } catch (err) {
      LOG("HATA:", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", leafletBekle);
  } else {
    leafletBekle();
  }
})();
</script>'''


# ------------------------------------------------------------
# 1) security.py — Talisman CSP kapat
# ------------------------------------------------------------
def talisman_csp_kapat(ic: str):
    if 'content_security_policy=None' in ic:
        return ic, False, "zaten None"
    yeni = ic.replace(
        "content_security_policy=csp",
        "content_security_policy=None  # CSP security_headers.py'de",
        1,
    )
    if yeni == ic:
        return ic, False, "content_security_policy=csp bulunamadı"
    return yeni, True, "Talisman CSP kapatıldı (tek CSP kaldı)"


# ------------------------------------------------------------
# 2) index.html — init script'i değiştir
# ------------------------------------------------------------
def js_degistir(html: str):
    if "leafletBekle" in html:
        return html, False, "yeni JS zaten var"

    # Eski script bloğunu bul
    pat = re.compile(
        r'<script id="' + re.escape(MARKER_JS) + r'">.*?</script>',
        re.DOTALL,
    )
    m = pat.search(html)
    if not m:
        return html, False, "eski init script bulunamadı"

    yeni = html[:m.start()] + YENI_JS + html[m.end():]
    return yeni, True, "init script yenilendi"


# ------------------------------------------------------------
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

    if INDEX.exists():
        html = INDEX.read_text(encoding="utf-8")
        yeni, d, m = js_degistir(html)
        print(f"[{'✓' if d else '·'}] index.html: {m}")
        if d:
            degis.append((INDEX, yeni))

    if SEC2.exists():
        sec2 = SEC2.read_text(encoding="utf-8")
        yeni2, d2, m2 = talisman_csp_kapat(sec2)
        print(f"[{'✓' if d2 else '·'}] security.py: {m2}")
        if d2:
            degis.append((SEC2, yeni2))

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
    print("  2) Telefonda ana sayfa → İletişim")
    print("  3) Chrome DevTools (USB ile) → Console → [CPK-Map] loglarına bak")
    print("     • 'Leaflet hazır' görünüyorsa → JS tarafı OK")
    print("     • 'tile error: ...' görünüyorsa → tile URL sorunu")
    print("     • 'Container boyutu: 0x0' → CSS sorunu")
    print("  4) Hâlâ siyahsa → konsol çıktısını gönder")


if __name__ == "__main__":
    main()