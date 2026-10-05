# seo_teshis.py
import re
from pathlib import Path

print("=" * 70)
print("1) robots.txt — kök dizin")
print("=" * 70)
robots = Path("robots.txt")
if robots.exists():
    ic = robots.read_text(encoding="utf-8", errors="replace")
    print(f"✓ Var ({len(ic)} byte)")
    print("-" * 60)
    print(ic)
    print("-" * 60)
else:
    print("✗ Kök dizinde robots.txt yok")
    # static içinde mi?
    for p in Path(".").rglob("robots.txt"):
        print(f"  Bulundu: {p}")

print("\n" + "=" * 70)
print("2) sitemap.xml — kök dizin")
print("=" * 70)
sm = Path("sitemap.xml")
if sm.exists():
    ic = sm.read_text(encoding="utf-8", errors="replace")
    print(f"✓ Var ({len(ic)} byte)")
    # URL sayısı
    sayi = len(re.findall(r"<url>", ic, re.IGNORECASE))
    print(f"  Toplam URL: {sayi}")
    # İlk 2000 karakter
    print("-" * 60)
    print(ic[:2000])
    print("-" * 60 if len(ic) > 2000 else "")
else:
    print("✗ Kök dizinde sitemap.xml yok")
    for p in Path(".").rglob("sitemap.xml"):
        print(f"  Bulundu: {p}")

print("\n" + "=" * 70)
print("3) app.py — robots/sitemap route'ları")
print("=" * 70)
app = Path("app.py").read_text(encoding="utf-8")
for i, s in enumerate(app.split("\n")):
    if re.search(r'robots|sitemap', s, re.IGNORECASE):
        print(f"{i:4d}| {s.strip()[:140]}")

print("\n" + "=" * 70)
print("4) Kanonik URL / domain — hangi domain kullanılıyor?")
print("=" * 70)
for f in ["templates/base.html", "templates/base_seo.html",
          "templates/index.html"]:
    p = Path(f)
    if not p.exists():
        continue
    ic = p.read_text(encoding="utf-8", errors="replace")
    # canonical, og:url, sitemap referansı
    for m in re.finditer(
        r'<(?:link[^>]*rel="canonical"|meta[^>]*property="og:url")[^>]*>',
        ic, re.IGNORECASE
    ):
        print(f"  {f}: {m.group(0)[:160]}")

print("\n" + "=" * 70)
print("5) index.html — schema.org (LocalBusiness?)")
print("=" * 70)
idx = Path("templates/index.html")
if idx.exists():
    ic = idx.read_text(encoding="utf-8", errors="replace")
    # JSON-LD bloklarını bul
    bloklar = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        ic, re.DOTALL | re.IGNORECASE
    )
    print(f"JSON-LD blok sayısı: {len(bloklar)}")
    for i, b in enumerate(bloklar, 1):
        # @type'ları çek
        tipler = re.findall(r'"@type"\s*:\s*"([^"]+)"', b)
        print(f"  #{i}  @type: {', '.join(tipler)}  ({len(b)} byte)")

print("\n" + "=" * 70)
print("6) base.html — meta description / title blokları")
print("=" * 70)
base = Path("templates/base.html")
if base.exists():
    ic = base.read_text(encoding="utf-8", errors="replace")
    for i, s in enumerate(ic.split("\n")):
        if re.search(r'<title>|meta\s+name="description"|'
                     r'og:title|og:description|twitter:',
                     s, re.IGNORECASE):
            print(f"{i:4d}| {s.strip()[:140]}")