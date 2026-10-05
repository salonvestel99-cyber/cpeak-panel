# seo_detay.py
import re
from pathlib import Path

print("=" * 70)
print("1) robots.txt route'unun TAM içeriği (app.py)")
print("=" * 70)
app = Path("app.py").read_text(encoding="utf-8")
satirlar = app.split("\n")

# robots route'unu bul
for i, s in enumerate(satirlar):
    if re.search(r"def robots_txt", s):
        bas = max(0, i - 5)
        son = min(len(satirlar), i + 30)
        for j in range(bas, son):
            print(f"{j:5d}| {satirlar[j]}")
        break

print("\n" + "=" * 70)
print("2) sitemap.xml route'unun TAM içeriği (app.py)")
print("=" * 70)
for i, s in enumerate(satirlar):
    if re.search(r"def sitemap_xml", s):
        bas = max(0, i - 5)
        son = min(len(satirlar), i + 60)
        for j in range(bas, son):
            print(f"{j:5d}| {satirlar[j]}")
        break

print("\n" + "=" * 70)
print("3) index.html — JSON-LD blok TAM içerik")
print("=" * 70)
idx = Path("templates/index.html")
if idx.exists():
    ic = idx.read_text(encoding="utf-8", errors="replace")
    m = re.search(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        ic, re.DOTALL | re.IGNORECASE,
    )
    if m:
        print(m.group(1).strip()[:2500])
    else:
        print("Bulunamadı")

print("\n" + "=" * 70)
print("4) Her template'in meta description / title bloğu")
print("=" * 70)
for tpl in sorted(Path("templates").glob("*.html")):
    ic = tpl.read_text(encoding="utf-8", errors="replace")
    # Block tanımları
    desc_m = re.search(
        r'\{%\s*block\s+description\s*%\}(.*?)\{%\s*endblock\s*%\}',
        ic, re.DOTALL,
    )
    title_m = re.search(
        r'\{%\s*block\s+title\s*%\}(.*?)\{%\s*endblock\s*%\}',
        ic, re.DOTALL,
    )
    # Direkt meta description
    meta_m = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"',
        ic, re.IGNORECASE,
    )
    boyut = len(ic)
    parts = [f"{tpl.name:32s} ({boyut:>6} b)"]
    if title_m:
        t = title_m.group(1).strip()[:40]
        parts.append(f"title: {t}")
    if desc_m:
        d = desc_m.group(1).strip()[:40]
        parts.append(f"desc-block: {d}")
    elif meta_m:
        parts.append(f"desc-meta: {meta_m.group(1)[:40]}")
    else:
        parts.append("desc: YOK ⚠")
    print(" | ".join(parts))

print("\n" + "=" * 70)
print("5) base.html — head bölümünde hangi SEO tag'leri var?")
print("=" * 70)
base = Path("templates/base.html").read_text(encoding="utf-8", errors="replace")
# head bölümünü al
head_m = re.search(r"<head>(.*?)</head>", base, re.DOTALL | re.IGNORECASE)
if head_m:
    head = head_m.group(1)
    etiketler = [
        "title", "meta name=\"description\"", "meta charset",
        "og:title", "og:description", "og:image", "og:url", "og:type",
        "twitter:card", "twitter:title", "twitter:description",
        "twitter:image", "canonical", "theme-color",
        "apple-touch-icon", "icon",
    ]
    for et in etiketler:
        sayi = len(re.findall(et, head, re.IGNORECASE))
        durum = "✓" if sayi else "✗"
        print(f"  {durum} {et:35s} ({sayi} adet)")

print("\n" + "=" * 70)
print("6) base_seo.html — ne içeriyor?")
print("=" * 70)
bs = Path("templates/base_seo.html")
if bs.exists():
    ic = bs.read_text(encoding="utf-8", errors="replace")
    print(f"Boyut: {len(ic)} byte")
    print(ic[:2000])