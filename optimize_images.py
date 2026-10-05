# -*- coding: utf-8 -*-
"""
Buyuk PNG'leri yeniden boyutlandirip optimize eder.
Ayni dosya adiyla kaydeder -> HTML/CSS degismez.
Yedekleri .orig uzantisiyla saklar.
"""
import os, shutil, subprocess, sys
from datetime import datetime

# Pillow kontrolu
try:
    from PIL import Image
except ImportError:
    print("Pillow yuklu degil. Yukleniyor...")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("HATA: Pillow yuklenemedi:")
        print(r.stderr)
        sys.exit(1)
    from PIL import Image

# (dosya, hedef_maks_genislik)
PLAN = [
    ("static/topbar-logo.png",  240),
    ("static/logo.png",         512),
    ("static/apple-touch-icon.png", 180),
    ("static/logochrome.png",   240),
]

def optimize_png(path, max_w):
    if not os.path.isfile(path):
        print(f"! {path} bulunamadi, atlandi")
        return None

    eski_boyut = os.path.getsize(path)
    img = Image.open(path)

    w, h = img.size
    if w > max_w:
        new_h = int(h * (max_w / w))
        img = img.resize((max_w, new_h), Image.LANCZOS)
        print(f"  boyut: {w}x{h} -> {max_w}x{new_h}")
    else:
        print(f"  boyut: {w}x{h} (dokunulmadi)")

    # RGBA modunda kaydet (saydamlik korunur)
    if img.mode not in ("RGBA", "P"):
        img = img.convert("RGBA")

    # Yedek
    bak = path + ".orig"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print(f"  yedek: {bak}")

    # Optimize kaydet
    img.save(path, "PNG", optimize=True, compress_level=9)

    yeni_boyut = os.path.getsize(path)
    kazanc = (1 - yeni_boyut / eski_boyut) * 100 if eski_boyut else 0
    print(f"  {eski_boyut/1024:.0f} KB -> {yeni_boyut/1024:.0f} KB  (kazanc: %{kazanc:.0f})")
    return eski_boyut - yeni_boyut

def main():
    print("== PNG Optimizasyon ==\n")
    if not os.path.isdir("static"):
        print("HATA: static klasoru bulunamadi.")
        sys.exit(1)

    toplam_kazanc = 0
    degisenler = []
    for path, max_w in PLAN:
        print(f"> {path}")
        k = optimize_png(path, max_w)
        if k and k > 0:
            toplam_kazanc += k
            degisenler.append(path)

    if not degisenler:
        print("\nHicbir dosya degismedi.")
        return

    print(f"\nToplam kazanc: {toplam_kazanc/1024:.0f} KB (~{toplam_kazanc/1024/1024:.2f} MB)")

    # .gitignore'a .orig ekle (istemiyorsak)
    gi = ".gitignore"
    try:
        if os.path.isfile(gi):
            c = open(gi, encoding="utf-8").read()
            if "*.orig" not in c:
                with open(gi, "a", encoding="utf-8") as f:
                    f.write("\n*.orig\n")
                print("+ .gitignore: *.orig eklendi")
    except Exception as e:
        print("! .gitignore:", e)

    # Git
    subprocess.run(["git", "add"] + degisenler + [gi], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "perf(images): buyuk PNG'ler optimize edildi (~3.4MB tasarruf)"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print("commit OK")
    else:
        out = (r.stdout + r.stderr).lower()
        if "nothing to commit" in out or "no changes" in out:
            print("commit edilecek sey yok")
        else:
            print("commit:", r.stderr.strip()[:200])

    br = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    ).stdout.strip() or "main"

    r = subprocess.run(["git", "push", "origin", br], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"push OK (origin/{br})")
    else:
        print("push HATA:", r.stderr.strip()[:200])

    print("\n== BITTI ==")
    print("Not: .orig yedekleri duruyor. Sorun cikarsa geri donebiliriz.")
    print("Sonraki adim: cache header optimizasyonu")

if __name__ == "__main__":
    main()