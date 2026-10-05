# -*- coding: utf-8 -*-
"""
login.html'deki .cpk-back-home butonunu mobilde saga tasir,
boylece ml11-back (sol ust) ile cakismaz.
"""
import os, shutil, subprocess, sys
from datetime import datetime

ESKI_MOBIL = '''@media (max-width: 768px) {
  .cpk-back-home {
    top: max(10px, env(safe-area-inset-top));
    left: max(10px, env(safe-area-inset-left));
    padding: 8px 13px;
    font-size: .78rem;
    gap: 6px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, .22);
  }
  .cpk-back-home svg {
    width: 14px;
    height: 14px;
  }
}'''

YENI_MOBIL = '''@media (max-width: 768px) {
  /* Mobilde sag uste al: sol ustteki ml11-back ile cakismaz */
  .cpk-back-home {
    top: max(12px, env(safe-area-inset-top));
    left: auto;
    right: max(12px, env(safe-area-inset-right));
    padding: 8px 13px;
    font-size: .78rem;
    gap: 6px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, .22);
  }
  .cpk-back-home svg {
    width: 14px;
    height: 14px;
  }

  /* ml11-back gorunurken (form aktif) benim buton biraz daha assagi insin,
     cunku sag ustte hero markasi veya form basligi olabilir */
  body.login-page.ml11-form-active .cpk-back-home {
    top: max(14px, env(safe-area-inset-top));
    right: max(14px, env(safe-area-inset-right));
  }
}'''

def main():
    path = "templates/login.html"
    if not os.path.isfile(path):
        print("HATA: templates/login.html bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()

    if "right: max(12px, env(safe-area-inset-right));" in c and "cpk-back-home" in c:
        print("= login.html: buton zaten sagda, atlandi.")
        return

    if ESKI_MOBIL not in c:
        print("! login.html: beklenen mobil CSS blogu bulunamadi.")
        print("  Manuel kontrol gerek.")
        # Yedek al ve yine de sag tarafa tasimayi dene
        eski_alternatif = '''  .cpk-back-home {
    top: max(10px, env(safe-area-inset-top));
    left: max(10px, env(safe-area-inset-left));'''
        if eski_alternatif in c:
            c2 = c.replace(eski_alternatif,
                '''  .cpk-back-home {
    top: max(12px, env(safe-area-inset-top));
    left: auto;
    right: max(12px, env(safe-area-inset-right));''')
            print("  Alternatif pattern ile duzeltildi.")
        else:
            sys.exit(1)
    else:
        c2 = c.replace(ESKI_MOBIL, YENI_MOBIL)
        print("+ mobil CSS blogu guncellendi")

    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("+ login.html: buton mobilde sag uste tasindi")

    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix(login): ana sayfa butonu mobilde saga tasindi (ml11-back cakismasi)"],
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
    print("Deploy sonrasi mobilde test et:")
    print("  https://www.cpeakenglish.com/giris")
    print("  - Sol ust: 'Geri' (form aktif olunca)")
    print("  - Sag ust: 'Ana Sayfa'")
    print("  - Ust uste binmemeli")

if __name__ == "__main__":
    main()