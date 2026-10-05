# -*- coding: utf-8 -*-
"""
1) app.py basindaki BOM'u temizler
2) Bozuk sitemap_xml fonksiyonunu duzeltir
3) Eksik route'lari (hakkimizda, kurslar, iletisim) ekler
4) Syntax kontrolu yapar, temizse commit + push
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

def main():
    path = "app.py"
    if not os.path.isfile(path):
        print("HATA: app.py bulunamadi.")
        sys.exit(1)

    # 1) Dosyayi BINARY oku ve BOM'u temizle
    with open(path, "rb") as f:
        raw = f.read()

    # UTF-8 BOM: EF BB BF
    if raw.startswith(b"\xef\xbb\xbf"):
        print("BOM bulundu (UTF-8 BOM), temizleniyor...")
        raw = raw[3:]
    # UTF-16 BOM kontrolu (olasi karisiklik)
    elif raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        print("HATA: Dosya UTF-16 ile kaydedilmis. Manuel mudahale gerek.")
        sys.exit(1)

    # UTF-8 olarak decode et
    try:
        c = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print("HATA: Dosya UTF-8 degil:", e)
        sys.exit(1)

    # Diğer gorunmez karakterleri de temizle (satir basi/sonu BOM)
    c = c.replace("\ufeff", "")

    # 2) Bozuk sitemap blogunu bul ve duzelt
    m_sitemap = re.search(r"@app\.route\(['\"]/sitemap\.xml['\"]\)", c)
    if not m_sitemap:
        print("UYARI: @app.route('/sitemap.xml') bulunamadi, atlaniyor.")
    else:
        start = m_sitemap.start()
        m_next = re.search(r"@app\.route\(", c[start + 10:])
        end = start + 10 + m_next.start() if m_next else len(c)

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
        c = c[:start] + correct + c[end:]
        print("+ sitemap_xml duzeltildi")

    # 3) Eksik route'lari ekle
    eksik = []
    for route, func, tpl in [
        ("/hakkimizda", "hakkimizda", "hakkimizda.html"),
        ("/kurslar",    "kurslar",    "kurslar.html"),
        ("/iletisim",   "iletisim",   "iletisim.html"),
    ]:
        if f"@app.route('{route}')" not in c and f'@app.route("{route}")' not in c:
            ekle = (
                f"\n@app.route('{route}')\n"
                f"def {func}():\n"
                f"    return render_template('{tpl}')\n"
            )
            c = c.rstrip() + "\n" + ekle
            eksik.append(route)
    if eksik:
        print("+ eklenen route'lar:", ", ".join(eksik))

    # 4) Syntax kontrolu (BOM'suz haliyle)
    try:
        compile(c, path, "exec")
        print("SYNTAX OK")
    except SyntaxError as e:
        print("SYNTAX HATASI:", e)
        print("Hicbir degisiklik yazilmadi.")
        sys.exit(1)

    # 5) Yedek al, BOM'suz UTF-8 olarak yaz
    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print("yedek:", bak)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c)
    print("yazildi:", path, "(BOM'suz UTF-8)")

    # 6) Git
    subprocess.run(["git", "add", path], check=False)
    r = subprocess.run(
        ["git", "commit", "-m", "fix: app.py BOM temizlendi + sitemap route duzeltildi"],
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
    print("Render deploy bitince test et:")
    print("  https://www.cpeakenglish.com/sitemap.xml")
    print("  https://www.cpeakenglish.com/hakkimizda")
    print("  https://www.cpeakenglish.com/kurslar")
    print("  https://www.cpeakenglish.com/iletisim")

if __name__ == "__main__":
    main()