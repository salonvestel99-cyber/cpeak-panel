# -*- coding: utf-8 -*-
"""
Mobil landing header duzeltmesi:
- Hero icindeki marka blogunu mobilde gizler (header ile ciftlenmesin)
- Header marka yazisini okunabilir hale getirir
- Giris Yap butonunu rahatlatir
"""
import os, shutil, subprocess, sys
from datetime import datetime

CSS_EK = '''

/* =========================================================
   MOBILE HEADER FIX v2 — cift marka, kucuk yazi, sikisan buton
   ========================================================= */
@media (max-width: 768px) {

  /* Header: marka + buton net gorunsun */
  body.cpk-page .cpk-header-inner {
    padding: 10px 14px !important;
    gap: 8px !important;
    height: auto !important;
    min-height: 56px !important;
  }
  body.cpk-page .cpk-header .topbar-brand {
    gap: 8px !important;
    min-width: 0;
    flex: 1 1 auto;
  }
  body.cpk-page .cpk-header .topbar-brand-mark img {
    height: 34px !important;
    width: 34px !important;
    object-fit: contain;
  }
  body.cpk-page .cpk-header .topbar-brand-text {
    min-width: 0;
  }
  body.cpk-page .cpk-header .topbar-brand-title {
    font-size: 1.05rem !important;
    line-height: 1 !important;
    white-space: nowrap;
    letter-spacing: -.01em;
  }
  body.cpk-page .cpk-header .topbar-brand-sep {
    display: none !important;
  }
  body.cpk-page .cpk-header .topbar-brand-sub {
    display: block !important;
    font-size: .55rem !important;
    letter-spacing: .3em !important;
    margin-top: 3px;
    line-height: 1;
  }
  body.cpk-page .cpk-nav {
    gap: 0 !important;
    flex-shrink: 0;
  }
  body.cpk-page .cpk-nav a:not(.cpk-nav-cta) {
    display: none !important;
  }
  body.cpk-page .cpk-nav-cta {
    padding: 9px 16px !important;
    font-size: .82rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    width: auto !important;
    white-space: nowrap;
    line-height: 1 !important;
  }

  /* Hero icindeki cift marka blogunu gizle */
  body.cpk-page .cpk-hero .hero-brand {
    display: none !important;
  }

  /* Hero ust boslugunu azalt (artik brand yok) */
  body.cpk-page .cpk-hero {
    padding: 36px 16px 48px !important;
  }
  body.cpk-page .cpk-hero-title {
    margin-top: 0 !important;
  }
}
'''

def main():
    path = "static/index.css"
    if not os.path.isfile(path):
        print("HATA: static/index.css bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()
    if "MOBILE HEADER FIX v2" in c:
        print("= index.css: v2 fix zaten var, atlandi.")
        return

    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c.rstrip() + "\n" + CSS_EK)
    print("+ static/index.css: mobil header fix eklendi")

    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix(mobile): header marka ciftlenmesi giderildi, buton rahatlatildi"],
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
        print(f"Manuel: git push origin {br}")

    print("\n== BITTI ==")
    print("Render deploy bitince mobile'da test et: https://www.cpeakenglish.com/")

if __name__ == "__main__":
    main()