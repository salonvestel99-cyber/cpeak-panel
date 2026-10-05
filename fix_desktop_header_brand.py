# -*- coding: utf-8 -*-
"""
Desktop landing header marka yazisi duzeltmesi:
topbar-brand ve cocuklarini dogru renk/font ile stiller.
"""
import os, shutil, subprocess, sys
from datetime import datetime

CSS_EK = '''

/* =========================================================
   DESKTOP HEADER BRAND FIX — varsayilan link rengi mor gorunumu
   ========================================================= */

/* Marka linki: renk ve alt cizgi sifirla */
.cpk-header .topbar-brand,
.cpk-header .topbar-brand:link,
.cpk-header .topbar-brand:visited,
.cpk-header .topbar-brand:hover,
.cpk-header .topbar-brand:active {
  color: var(--ink) !important;
  text-decoration: none !important;
  display: flex !important;
  align-items: center;
  gap: 12px;
}

html[data-theme="dark"] .cpk-header .topbar-brand,
html.dark .cpk-header .topbar-brand,
html[data-theme="dark"] .cpk-header .topbar-brand:link,
html.dark .cpk-header .topbar-brand:link,
html[data-theme="dark"] .cpk-header .topbar-brand:visited,
html.dark .cpk-header .topbar-brand:visited,
html[data-theme="dark"] .cpk-header .topbar-brand:hover,
html.dark .cpk-header .topbar-brand:hover {
  color: #fafafa !important;
}

/* Marka metin blogu */
.cpk-header .topbar-brand-text {
  display: flex;
  align-items: baseline;
  gap: 8px;
  line-height: 1;
  text-decoration: none !important;
}

/* Ana baslik: C · Peak */
.cpk-header .topbar-brand-title {
  font-family: 'Fraunces', Georgia, serif !important;
  font-size: 1.15rem !important;
  font-weight: 600 !important;
  letter-spacing: -.02em !important;
  color: inherit !important;
  text-decoration: none !important;
}

/* Ayrac */
.cpk-header .topbar-brand-sep {
  display: inline-block;
  width: 1px;
  height: 14px;
  background: currentColor;
  opacity: .35;
  align-self: center;
}

/* ENGLISH alt basligi */
.cpk-header .topbar-brand-sub {
  font-family: 'Inter', sans-serif !important;
  font-size: .68rem !important;
  font-weight: 700 !important;
  letter-spacing: .28em !important;
  color: var(--copper) !important;
  text-decoration: none !important;
  text-transform: uppercase;
}

/* Logo boyutu */
.cpk-header .topbar-brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.cpk-header .topbar-brand-mark img {
  height: 40px;
  width: auto;
  object-fit: contain;
  display: block;
}

/* Nav linkleri de net gorunsun */
.cpk-header .cpk-nav a,
.cpk-header .cpk-nav a:link,
.cpk-header .cpk-nav a:visited {
  color: var(--ink) !important;
  text-decoration: none !important;
}
html[data-theme="dark"] .cpk-header .cpk-nav a,
html.dark .cpk-header .cpk-nav a,
html[data-theme="dark"] .cpk-header .cpk-nav a:link,
html.dark .cpk-header .cpk-nav a:link,
html[data-theme="dark"] .cpk-header .cpk-nav a:visited,
html.dark .cpk-header .cpk-nav a:visited {
  color: #e4e4e7 !important;
}
.cpk-header .cpk-nav a:hover {
  color: var(--copper) !important;
}
.cpk-header .cpk-nav-cta,
.cpk-header .cpk-nav-cta:link,
.cpk-header .cpk-nav-cta:visited {
  color: #fff !important;
  text-decoration: none !important;
}

/* Mobilde de gecerli */
@media (max-width: 768px) {
  .cpk-header .topbar-brand-title {
    font-size: 1.05rem !important;
  }
  .cpk-header .topbar-brand-sub {
    font-size: .58rem !important;
  }
  .cpk-header .topbar-brand-mark img {
    height: 34px !important;
  }
}
'''

def main():
    path = "static/index.css"
    if not os.path.isfile(path):
        print("HATA: static/index.css bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()
    if "DESKTOP HEADER BRAND FIX" in c:
        print("= index.css: fix zaten var, atlandi.")
        return

    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c.rstrip() + "\n" + CSS_EK)
    print("+ static/index.css: header brand fix eklendi")

    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix(header): desktop landing marka yazisi dogru renk ve font ile"],
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
    print("Render deploy bitince kontrol et: https://www.cpeakenglish.com/")
    print("  - Marka yazisi 'C · Peak' koyu, 'ENGLISH' bakir olmali")
    print("  - Nav linkleri (Hakkimizda / Kurslar / Iletisim) normal renkte olmali")

if __name__ == "__main__":
    main()