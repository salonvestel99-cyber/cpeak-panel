# -*- coding: utf-8 -*-
"""
Giris yapmamis kullanicilarda logout modal gorunmesini engeller.
1) base.html icindeki logoutModal div'ini {% if session.get('user_id') %} ile sarar
2) geri_onay.js basina "logoutModal yoksa cik" guard ekler
Yedek alir, git commit + push yapar.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

def yedek(path):
    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print(f"  yedek: {bak}")
    return bak

def div_blogunu_bul(text, baslangic_idx):
    """baslangic_idx'ten itibaren div blogunu kapanisina kadar bulur."""
    i = baslangic_idx
    derinlik = 0
    # Ilk <div'i bul
    acilis = text.find("<div", i)
    if acilis == -1:
        return -1, -1
    i = acilis
    n = len(text)
    while i < n:
        if text.startswith("<div", i):
            # <div veya <div> veya <div ...>  (self-closing yok varsayimi)
            derinlik += 1
            # bu etiketin sonunu atla
            kapanis = text.find(">", i)
            if kapanis == -1:
                return -1, -1
            i = kapanis + 1
            continue
        if text.startswith("</div>", i):
            derinlik -= 1
            if derinlik == 0:
                return acilis, i + len("</div>")
            i += len("</div>")
            continue
        i += 1
    return -1, -1

def fix_base_html(path):
    c = open(path, encoding="utf-8").read()
    if "{% if session.get('user_id') %}\n<div id=\"logoutModal\"" in c:
        print("= base.html: zaten korumali, atlandi")
        return False
    if '{% if session.get("user_id") %}\n<div id="logoutModal"' in c:
        print("= base.html: zaten korumali, atlandi")
        return False

    marker = '<div id="logoutModal"'
    idx = c.find(marker)
    if idx == -1:
        print("HATA: base.html icinde logoutModal bulunamadi")
        return False

    bas, son = div_blogunu_bul(c, idx)
    if bas == -1:
        print("HATA: logoutModal div blogu kapanisi bulunamadi")
        return False

    blok = c[bas:son]
    yeni_blok = "{% if session.get('user_id') %}\n" + blok + "\n{% endif %}"
    c2 = c[:bas] + yeni_blok + c[son:]

    yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("+ base.html: logoutModal artik sadece giris yapmisken render ediliyor")
    return True

def fix_geri_onay(path):
    c = open(path, encoding="utf-8").read()
    if "// cpk: logged-out guard" in c:
        print("= geri_onay.js: zaten korumali, atlandi")
        return False

    # "use strict"ten sonra guard ekle
    m = re.search(r'("use strict";\s*)', c)
    if not m:
        print("HATA: geri_onay.js icinde 'use strict' bulunamadi")
        return False

    guard = (
        m.group(1)
        + "\n  // cpk: logged-out guard — oturum acmamis kullanicida hic calisma\n"
        + "  if (!document.getElementById('logoutModal')) {\n"
        + "    return;\n"
        + "  }\n"
    )
    c2 = c[:m.start()] + guard + c[m.end():]

    yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("+ geri_onay.js: logoutModal yoksa en basta cikiyor")
    return True

def main():
    print("== Logout modal guard fix ==\n")

    base = "templates/base.html"
    js = "static/geri_onay.js"

    for p in (base, js):
        if not os.path.isfile(p):
            print(f"HATA: {p} bulunamadi")
            sys.exit(1)

    degisti = []
    if fix_base_html(base):
        degisti.append(base)
    if fix_geri_onay(js):
        degisti.append(js)

    if not degisti:
        print("\nHicbir degisiklik yok. Push yapilmadi.")
        return

    print("\n-- git islemleri --")
    subprocess.run(["git", "add"] + degisti, check=False)
    r = subprocess.run(
        ["git", "commit", "-m",
         "fix(auth-ui): logout modal artik sadece giris yapmis kullanicida gorunur"],
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
    print("Render deploy bitince test et:")
    print("  Giris YAPMADAN  https://www.cpeakenglish.com/  -> geri tusuna bas -> modal CIKMAMALI")
    print("  Giris YAPTIKTAN https://www.cpeakenglish.com/panel  -> geri tusuna bas -> modal CIKMALI")

if __name__ == "__main__":
    main()