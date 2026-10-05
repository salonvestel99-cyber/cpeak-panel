import re, shutil
from datetime import datetime

f = "app.py"
c = open(f, encoding="utf-8").read()
orig = c

# Yedek
bak = f + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(f, bak)
print(f"Yedek: {bak}")

# pages = [ ... ] blogunu bul
pattern = r'(def sitemap_xml\(\):.*?pages\s*=\s*\[)(.*?)(\])'
match = re.search(pattern, c, re.DOTALL)

if not match:
    print("HATA: sitemap_xml fonksiyonu bulunamadi")
    raise SystemExit(1)

yeni_pages = '\n        "https://www.cpeakenglish.com/kvkk",\n    '
c = c[:match.start(2)] + yeni_pages + c[match.end(2):]

if c != orig:
    open(f, "w", encoding="utf-8").write(c)
    print("Sitemap guncellendi: sadece /kvkk kaldi")
else:
    print("Degisiklik yok")
    raise SystemExit(0)