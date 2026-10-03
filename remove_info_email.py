# -*- coding: utf-8 -*-
"""
cpeakenglish@gmail.com adresini projeden kaldirir.
- <a href="mailto:info@...">...</a> ve varsa yanindaki <br>'i siler
- Kalan duz metin referanslarini cpeakenglish@gmail.com ile degistirir
- Yedek alir, git commit + push yapar
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

ESKI = "cpeakenglish@gmail.com"
YENI = "cpeakenglish@gmail.com"

ATLA_KLASOR = {".git", "venv", ".venv", "__pycache__", "node_modules", ".idea", ".vscode"}
UZANTILAR = {".html", ".py", ".css", ".js", ".json", ".md", ".txt", ".xml", ".jinja", ".jinja2"}

# info@... iceren <a> anchor'unu (ve varsa hemen ardindaki <br>'i) sil
ANCHOR_RE = re.compile(
    r'<a\b[^>]*mailto:' + re.escape(ESKI) + r'[^>]*>[^<]*</a>\s*(<br\s*/?>\s*)?',
    re.IGNORECASE
)

def dosyalari_bul(kok="."):
    for dirpath, dirnames, filenames in os.walk(kok):
        dirnames[:] = [d for d in dirnames if d not in ATLA_KLASOR]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in UZANTILAR:
                yield os.path.join(dirpath, fn)

def dosyada_degistir(path):
    try:
        c = open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        return None  # ikili/binary dosya, atla

    if ESKI not in c:
        return None

    orig = c
    anchor_sayisi = len(ANCHOR_RE.findall(c))
    c = ANCHOR_RE.sub("", c)
    kalan_replace = c.count(ESKI)
    if kalan_replace:
        c = c.replace(ESKI, YENI)

    if c == orig:
        return None

    return {
        "yeni_icerik": c,
        "anchor_silindi": anchor_sayisi,
        "metin_degistirildi": kalan_replace,
    }

def main():
    print("== cpeakenglish@gmail.com temizligi ==\n")

    if not os.path.isfile("app.py"):
        print("HATA: app.py bulunamadi. Betigi cpeak klasorunde calistirin.")
        sys.exit(1)

    etkilenen = []
    for path in dosyalari_bul("."):
        sonuc = dosyada_degistir(path)
        if sonuc:
            etkilenen.append((path, sonuc))
            print(f"~ {path}")
            if sonuc["anchor_silindi"]:
                print(f"    - {sonuc['anchor_silindi']} anchor (<a>) silindi")
            if sonuc["metin_degistirildi"]:
                print(f"    - {sonuc['metin_degistirildi']} duz metin -> {YENI}")

    if not etkilenen:
        print("Hicbir dosyada 'cpeakenglish@gmail.com' bulunamadi.")
        return

    print(f"\nToplam {len(etkilenen)} dosya degisecek.")
    onay = input("Devam edilsin mi? (e/H): ").strip().lower()
    if onay not in ("e", "evet", "y", "yes"):
        print("Iptal edildi.")
        return

    print("\n-- yedekler aliniyor ve yaziliyor --")
    for path, sonuc in etkilenen:
        bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(path, bak)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(sonuc["yeni_icerik"])
        print(f"  yazildi: {path}  (yedek: {bak})")

    print("\n-- git islemleri --")
    dosyalar = [p for p, _ in etkilenen]
    subprocess.run(["git", "add"] + dosyalar, check=False)

    r = subprocess.run(
        ["git", "commit", "-m",
         f"chore: {ESKI} adresi kaldirildi, sadece {YENI} kaldi"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print("commit OK")
    else:
        out = (r.stdout + r.stderr).lower()
        if "nothing to commit" in out or "no changes" in out:
            print("commit edilecek sey yok")
        else:
            print(f"commit HATA: {r.stderr.strip()[:300]}")

    br = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        capture_output=True, text=True).stdout.strip() or "main"
    r = subprocess.run(["git", "push", "origin", br], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"push OK (origin/{br})")
    else:
        print(f"push HATA: {r.stderr.strip()[:300]}")
        print(f"Manuel: git push origin {br}")

    print("\n== BITTI ==")
    print("Render deploy bitince kontrol et: https://www.cpeakenglish.com/")

if __name__ == "__main__":
    main()