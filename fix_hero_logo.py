# -*- coding: utf-8 -*-
"""
Hero'daki bulanik/yanlis konumlanmis logolari temizler.
- cpk-hero::before (bulanik arka plan logosu) kaldirilir
- hero-brand-mark::before (glow) notrlenir
- hero-brand-mark img mix-blend-mode normal, net gorunur
"""
import os, shutil, subprocess, sys
from datetime import datetime

CSS_EK = '''

/* =========================================================
   HERO LOGO FIX — bulanik arka plan logosu + kayip logo
   ========================================================= */

/* 1) Hero'nun arka planindaki bulanik dev logo'yu kaldir */
.cpk-hero::before {
  display: none !important;
  content: none !important;
  background: none !important;
}

/* 2) Logonun etrafindaki asiri glow'u notrle */
.cpk-hero .hero-brand-mark::before {
  display: none !important;
  content: none !important;
}

/* 3) Hero'daki logoyu net ve dogru boyutta goster */
.cpk-hero .hero-brand-mark {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cpk-hero .hero-brand-mark img {
  position: relative;
  z-index: 1;
  display: block;
  height: clamp(72px, 8vw, 96px) !important;
  width: auto !important;
  object-fit: contain;
  mix-blend-mode: normal !important;
  filter: drop-shadow(0 4px 16px rgba(180,83,9,.35)) !important;
  opacity: 1 !important;
}

/* 4) Marka blogu (logo + yazi) duzgun hizalansin */
.cpk-hero .hero-brand {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 18px !important;
  margin: 0 auto 34px !important;
  text-align: left;
}

.cpk-hero .hero-brand-text {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  line-height: 1;
}

.cpk-hero .hero-brand-title {
  font-family: 'Fraunces', Georgia, serif !important;
  font-size: clamp(1.8rem, 3.2vw, 2.6rem) !important;
  font-weight: 600 !important;
  letter-spacing: -.02em !important;
  color: #fff !important;
  line-height: 1 !important;
}

.cpk-hero .hero-brand-sub {
  margin-top: 6px;
  font-family: 'Inter', sans-serif !important;
  font-size: .74rem !important;
  font-weight: 700 !important;
  letter-spacing: .38em !important;
  color: var(--copper) !important;
  text-transform: uppercase;
}

/* 5) Mobilde alt alta kalsin ama temiz */
@media (max-width: 768px) {
  .cpk-hero .hero-brand {
    flex-direction: column !important;
    gap: 12px !important;
    text-align: center;
    margin-bottom: 24px !important;
  }
  .cpk-hero .hero-brand-text {
    align-items: center !important;
  }
  .cpk-hero .hero-brand-mark img {
    height: 72px !important;
  }
  .cpk-hero .hero-brand-title {
    font-size: 1.6rem !important;
  }
  .cpk-hero .hero-brand-sub {
    font-size: .6rem !important;
    letter-spacing: .3em !important;
  }
}
'''

def main():
    path = "static/index.css"
    if not os.path.isfile(path):
        print("HATA: static/index.css bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()
    if "HERO LOGO FIX" in c:
        print("= index.css: hero logo fix zaten var, atlandi.")
        return

    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c.rstrip() + "\n" + CSS_EK)
    print("+ static/index.css: hero logo fix eklendi")

    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix(hero): bulanik arka plan logosu kaldirildi, hero logo netlendi"],
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
    print("  - Arka plandaki bulanik dev logo KAYBOLMALI")
    print("  - Hero'da logo + C · Peak / ENGLISH net gorunmeli")
    print("  - Mobilde alt alta, masaustunde yan yana")

if __name__ == "__main__":
    main()