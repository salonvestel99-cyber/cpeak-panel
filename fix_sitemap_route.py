# -*- coding: utf-8 -*-
"""
app.py'deki bozuk sitemap_xml fonksiyonunu duzeltir.
Syntax kontrolu yapar, hata varsa geri alir.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

def main():
    path = "app.py"
    if not os.path.isfile(path):
        print("HATA: app.py bulunamadi.")
        sys.exit(1)

    c = open(path, encoding="utf-8").read()

    # 1) Bozuk sitemap bolumunu bul
    m_sitemap = re.search(r"@app\.route\(['\"]/sitemap\.xml['\"]\)", c)
    if not m_sitemap:
        print("HATA: @app.route('/sitemap.xml') bulunamadi.")
        sys.exit(1)

    start = m_sitemap.start()

    # 2) Sonraki @app.route'a kadar olan bolumu degistir
    m_next = re.search(r"@app\.route\(", c[start + 10:])
    if m_next:
        end = start + 10 + m_next.start()
    else:
        end = len(c)

    # 3) Dogru sitemap fonksiyonu
    correct = (
        "@app.route('/sitemap.xml')\n"
        "def sitemap_xml():\n"
        "    pages = [\n"
        '        "https://www.cpeakenglish.com/",\n'
        '        "https://www.cpeakenglish.com/hakkimizda",\n'
        '        "https://www.cpeakenglish.com/kurslar",\n'
        '        "https://www.cpeakenglish.com/iletisim",\n'
        '        "https://www.cpeakenglish.com/kvkk",\n'
        "    ]\n"
        "    today = datetime.now().date().isoformat()\n"
        "    xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\\n'\n"
        "    xml += '<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\\n'\n"
        "    for p in pages:\n"
        "        xml += f'  <url><loc>{p}</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>\\n'\n"
        "    xml += '</urlset>'\n"
        "    return Response(xml, mimetype='application/xml')\n"
        "\n\n"
    )

    c2 = c[:start] + correct + c[end:]

    # 4) Eksik route kontrolu (hakkimizda, kurslar, iletisim)
    eksik = []
    for route, func, tpl in [
        ("/hakkimizda", "hakkimizda", "hakkimizda.html"),
        ("/kurslar",    "kurslar",    "kurslar.html"),
        ("/iletisim",   "iletisim",   "iletisim.html"),
    ]:
        if f"@app.route('{route}')" not in c2 and f'@app.route("{route}")' not in c2:
            ekle = (
                f"\n@app.route('{route}')\n"
                f"def {func}():\n"
                f"    return render_template('{tpl}')\n"
            )
            c2 = c2.rstrip() + "\n" + ekle
            eksik.append(route)

    if eksik:
        print("+ eklenen route'lar:", ", ".join(eksik))

    # 5) Yedek al ve yaz
    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("yazildi:", path)

    # 6) Syntax kontrolu
    try:
        compile(c2, path, "exec")
        print("SYNTAX OK")
    except SyntaxError as e:
        print("HALA SYNTAX HATASI:", e)
        print("Geri yukleniyor:", bak)
        shutil.copy2(bak, path)
        sys.exit(1)

    # 7) Commit + push
    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix: sitemap route syntax hatasi duzeltildi"],
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
    print("Render'da yeni deploy baslar. 'Live' olunca test et:")
    print("  https://www.cpeakenglish.com/sitemap.xml")
    print("  https://www.cpeakenglish.com/hakkimizda")
    print("  https://www.cpeakenglish.com/kurslar")
    print("  https://www.cpeakenglish.com/iletisim")

if __name__ == "__main__":
    main()