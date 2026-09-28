# -*- coding: utf-8 -*-
"""Ikinci cikis modalini (ckCikisOverlay) siler; UDMIN cikis linkini premium modal'a baglar."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(KOK, "templates", "base.html")
YEDEK = os.path.join(KOK, "backups")
os.makedirs(YEDEK, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(BASE, os.path.join(YEDEK, f"base.{stamp}.bak"))
print(f"Yedek: backups/base.{stamp}.bak")

with open(BASE, "r", encoding="utf-8") as f:
    c = f.read()

onceki_len = len(c)

# ============================================================
# 1) CKMODAL-INLINE blogunu TAMAMEN sil
#    <!-- CKMODAL-INLINE --> ... <!-- /CKMODAL-INLINE -->
# ============================================================
pat_cm = re.compile(
    r'<!--\s*CKMODAL-INLINE\s*-->.*?<!--\s*/CKMODAL-INLINE\s*-->',
    re.DOTALL
)
c, n = pat_cm.subn('', c)
if n > 0:
    print(f"[OK] CKMODAL-INLINE blogu silindi ({onceki_len - len(c)} byte)")
else:
    print("[--] CKMODAL-INLINE markeri bulunamadi")

# ============================================================
# 2) UDMIN cikis butonuna data-logout attribute ekle
#    <a class="ud-i ud-danger" href="/cikis" id="udCikisBtn" data-cikis-url="/cikis">
#    ->
#    <a class="ud-i ud-danger" href="#" data-logout id="udCikisBtn" class="...">
# ============================================================
pat_btn = re.compile(
    r'<a\s+class="ud-i ud-danger"\s+href="[^"]*"\s+id="udCikisBtn"\s+data-cikis-url="[^"]*"\s*>',
    re.DOTALL
)

YENI_BTN = '<a class="ud-i ud-danger logout-item" href="#" data-logout id="udCikisBtn">'
c, n2 = pat_btn.subn(YENI_BTN, c)
if n2 > 0:
    print(f"[OK] udCikisBtn premium modal'a baglandi")
else:
    # Alternatif pattern
    pat_btn2 = re.compile(
        r'<a[^>]*id="udCikisBtn"[^>]*>',
        re.DOTALL
    )
    c, n2 = pat_btn2.subn(YENI_BTN, c)
    if n2 > 0:
        print(f"[OK] udCikisBtn premium modal'a baglandi (fallback)")
    else:
        print("[--] udCikisBtn bulunamadi")

# ============================================================
# 3) UDMIN JS'inde udCikisBtn'e baglanan eski cikis JS'ini sil
#    (zaten logoutModal data-logout ile tetiklenir)
# ============================================================
# CKMODAL JS'i CKMODAL blogunun icindeydi, o blogu tamamen sildik.

# Ama bazen udCikisBtn icin ayri JS olabilir
# Su pattern'i ara: getElementById("udCikisBtn") + form.submit()
pat_js = re.compile(
    r'\(function\s*\(\s*\)\s*\{[^{}]*getElementById\("udCikisBtn"\)[^{}]*\}\s*\)\s*\(\s*\)\s*;?',
    re.DOTALL
)
c, n3 = pat_js.subn('', c)
if n3 > 0:
    print(f"[OK] Eski cikis JS'i silindi ({n3} adet)")

# ============================================================
# 4) Form'u sil (ckCikisForm)
# ============================================================
pat_form = re.compile(
    r'<form[^>]*id="ckCikisForm"[^>]*>.*?</form>',
    re.DOTALL
)
c, n4 = pat_form.subn('', c)
if n4 > 0:
    print(f"[OK] ckCikisForm silindi")

# ============================================================
# 5) UDMIN menusundeki "Gizlilik & KVKK" linki altina bir ayirici koy? Yok gerek yok.
# ============================================================

# Kalan "ckCikis" referansi kontrolu
if "ckCikisOverlay" in c or "ckCikisForm" in c:
    print("[!!] UYARI: halen ckCikis referansi var!")
    for m in re.finditer(r'ckCikis\w+', c):
        s = max(0, m.start()-40)
        e = min(len(c), m.end()+40)
        print(f"    ...{c[s:e]}...")
else:
    print("[OK] ckCikis referansi kalmadi")

# Bos satir toparla
c = re.sub(r'\n{3,}', '\n\n', c)

with open(BASE, "w", encoding="utf-8") as f:
    f.write(c)

print(f"[OK] Toplam: {onceki_len} -> {len(c)} byte")

# Cache-busting
with open(BASE, "r", encoding="utf-8") as f:
    bc = f.read()
bc = re.sub(r"\?v=[\w_]+", "", bc)
yeni_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bc = re.sub(
    r"(filename='(?:hero|panel|login|theme|style|student|teacher|footer|responsive|whatsapp|admin|legal)\.css'\) \}\})",
    r"\1?v=" + yeni_stamp, bc
)
with open(BASE, "w", encoding="utf-8") as f:
    f.write(bc)
print(f"[OK] base.html ?v={yeni_stamp}")

print()
print("BITTI. Ctrl+C, py app.py, tarayicida Ctrl+Shift+R")
print()
print("Simdi cikis butonuna basinca TEK modal cikacak (premium logoutModal).")