# -*- coding: utf-8 -*-
"""
login.html: Ana Sayfa butonu mobilde sol uste, ml11-back (Geri) ile alt alta.
- Form kapali: Ana Sayfa top:12px
- Form aktif: Geri top:12px, Ana Sayfa top:~62px (Geri'nin altinda)
"""
import os, shutil, subprocess, sys
from datetime import datetime

ESKI_BLOK = '''@media (max-width: 768px) {
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

YENI_BLOK = '''@media (max-width: 768px) {
  /* Mobilde sol ustte kal, ama ml11-back ile alt alta */
  .cpk-back-home {
    top: max(12px, env(safe-area-inset-top));
    left: max(12px, env(safe-area-inset-left));
    right: auto;
    padding: 8px 13px;
    font-size: .78rem;
    gap: 6px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, .22);
  }
  .cpk-back-home svg {
    width: 14px;
    height: 14px;
  }

  /* Form aktifken ml11-back de sol uste gelir.
     Ana Sayfa butonunu onun hemen altina indir. */
  body.login-page.ml11-form-active .cpk-back-home {
    top: calc(max(12px, env(safe-area-inset-top)) + 48px);
  }
}'''

def main():
    path = "templates/login.html"
    if not os.path.isfile(path):
        print("HATA: templates/login.html bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()

    if "top: calc(max(12px, env(safe-area-inset-top)) + 48px);" in c:
        print("= login.html: zaten duzeltilmis, atlandi.")
        return

    if ESKI_BLOK not in c:
        print("! Beklenen CSS blogu bulunamadi, manuel kontrol gerek.")
        # Yedek eski versiyonlari da dene
        alternatifler = [
            # Onceki sag taraf versiyonu
            ('''  .cpk-back-home {
    top: max(12px, env(safe-area-inset-top));
    left: auto;
    right: max(12px, env(safe-area-inset-right));''',
             '''  .cpk-back-home {
    top: max(12px, env(safe-area-inset-top));
    left: max(12px, env(safe-area-inset-left));
    right: auto;'''),
        ]
        bulundu = False
        for eski, yeni in alternatifler:
            if eski in c:
                c = c.replace(eski, yeni)
                print("  Alternatif pattern ile duzeltildi.")
                bulundu = True
                break
        if not bulundu:
            print("HATA: hicbir pattern bulunamadi.")
            sys.exit(1)

        # ml11-form-active kuralini da ekle
        if "ml11-form-active .cpk-back-home" not in c:
            # @media blogunun sonuna ekle
            marker = "  .cpk-back-home svg {\n    width: 14px;\n    height: 14px;\n  }"
            if marker in c:
                c = c.replace(marker, marker + '''

  body.login-page.ml11-form-active .cpk-back-home {
    top: calc(max(12px, env(safe-area-inset-top)) + 48px);
  }''', 1)
                print("  + ml11-form-active kurali eklendi")
    else:
        c = c.replace(ESKI_BLOK, YENI_BLOK)
        print("+ mobil CSS blogu guncellendi (sol ust, alt alta)")

    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c)
    print("+ login.html guncellendi")

    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix(login): ana sayfa butonu mobilde sola alindi, ml11-back ile alt alta"],
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
    print("Deploy sonrasi mobilde test:")
    print("  Form kapali -> Sol ustte 'Ana Sayfa'")
    print("  Form aktif  -> Sol ustte 'Geri', hemen altinda 'Ana Sayfa'")
    print("  Dark mode toggle ile cakisma yok")

if __name__ == "__main__":
    main()