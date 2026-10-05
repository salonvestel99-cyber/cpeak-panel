# -*- coding: utf-8 -*-
"""
login.html'e sabit konumlu 'Ana Sayfa' butonu ekler.
Idempotent: varsa atlar. Yedek + commit + push.
"""
import os, shutil, subprocess, sys
from datetime import datetime

CSS = '''
<style>
/* cpk: back-home button on login page */
.cpk-back-home {
  position: fixed;
  top: max(16px, env(safe-area-inset-top));
  left: max(16px, env(safe-area-inset-left));
  z-index: 9999;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 15px;
  border-radius: 999px;
  background: rgba(0, 0, 0, .42);
  -webkit-backdrop-filter: blur(14px) saturate(160%);
  backdrop-filter: blur(14px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, .18);
  color: #fff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: .84rem;
  font-weight: 500;
  letter-spacing: .01em;
  text-decoration: none;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(0, 0, 0, .22);
  transition: background .18s ease, border-color .18s ease, transform .18s ease;
}
.cpk-back-home:hover,
.cpk-back-home:focus-visible {
  background: rgba(180, 83, 9, .55);
  border-color: rgba(180, 83, 9, .85);
  transform: translateY(-1px);
  color: #fff;
  text-decoration: none;
  outline: none;
}
.cpk-back-home:active {
  transform: translateY(0);
}
.cpk-back-home svg {
  width: 15px;
  height: 15px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}

@media (max-width: 768px) {
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
}
</style>
<a href="/" class="cpk-back-home" aria-label="Ana sayfaya dön">
  <svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="15 18 9 12 15 6"></polyline></svg>
  <span>Ana Sayfa</span>
</a>
'''

MARKER = "<!-- cpk:back-home -->"

def main():
    path = "templates/login.html"
    if not os.path.isfile(path):
        print("HATA: templates/login.html bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()

    if "cpk-back-home" in c:
        print("= login.html: ana sayfa butonu zaten var, atlandi.")
        return

    # block body hemen sonrasina ekle
    if "{% block body %}" not in c:
        print("HATA: login.html icinde '{% block body %}' bulunamadi.")
        sys.exit(1)

    eklenecek = "{% block body %}\n" + MARKER + "\n" + CSS
    c2 = c.replace("{% block body %}", eklenecek, 1)

    # Syntax kontrolu (Jinja'nin kendisi degil, sadece dosya saglamligi)
    if "{% block body %}" not in c2:
        print("HATA: blok sonrasi bozuldu, islem iptal.")
        sys.exit(1)

    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("+ login.html: 'Ana Sayfa' butonu eklendi")

    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "feat(login): ana sayfaya don butonu eklendi"],
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
    print("Deploy sonrasi test:")
    print("  https://www.cpeakenglish.com/giris")
    print("  -> Sol ust kosede cam efektli 'Ana Sayfa' butonu gorunmeli")
    print("  -> Tiklayinca '/' sayfasina gitmeli")

if __name__ == "__main__":
    main()