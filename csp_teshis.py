# csp_teshis.py
import re
from pathlib import Path

print("=" * 70)
print("1) security_headers.py — CSP bloğu")
print("=" * 70)
sec = Path("security_headers.py")
if sec.exists():
    ic = sec.read_text(encoding="utf-8")
    m = re.search(r'Content-Security-Policy.*?\]\)', ic, re.DOTALL)
    if m:
        print(m.group(0)[:2000])
    else:
        print("[!] CSP bulunamadı")
        # frame-src var mı?
        if "frame-src" in ic:
            print("    ama 'frame-src' var")
        else:
            print("    ve 'frame-src' YOK")

print("\n" + "=" * 70)
print("2) security.py — Talisman konfigürasyonu")
print("=" * 70)
sec2 = Path("security.py")
if sec2.exists():
    ic2 = sec2.read_text(encoding="utf-8")
    # Talisman satırları
    for i, s in enumerate(ic2.split("\n")):
        if re.search(r'Talisman|content_security|CSP|force_https|frame',
                     s, re.IGNORECASE):
            print(f"{i:4d}| {s.rstrip()[:150]}")
else:
    print("[!] security.py yok")

print("\n" + "=" * 70)
print("3) app.py — Talisman / CSP referansı")
print("=" * 70)
app = Path("app.py")
if app.exists():
    ic3 = app.read_text(encoding="utf-8")
    for i, s in enumerate(ic3.split("\n")):
        if re.search(r'Talisman|content_security|after_request|CSP',
                     s, re.IGNORECASE):
            print(f"{i:4d}| {s.rstrip()[:150]}")

print("\n" + "=" * 70)
print("4) index.html — iframe bloğu")
print("=" * 70)
idx = Path("templates/index.html")
if idx.exists():
    ic4 = idx.read_text(encoding="utf-8")
    m = re.search(r'<a class="cpk-map".*?</a>', ic4, re.DOTALL)
    if m:
        print(m.group(0)[:800])
    # Kaç tane cpk-map var?
    print(f"\ncpk-map sayısı: {ic4.count('class=\"cpk-map\"')}")
    print(f"cpk-map-embed marker: {ic4.count('cpk-map-embed')}")
else:
    print("[!] index.html yok")

print("\n" + "=" * 70)
print("5) requirements.txt — Talisman var mı?")
print("=" * 70)
req = Path("requirements.txt")
if req.exists():
    ic5 = req.read_text(encoding="utf-8")
    for s in ic5.split("\n"):
        if "talisman" in s.lower() or "flask" in s.lower():
            print(s.strip())