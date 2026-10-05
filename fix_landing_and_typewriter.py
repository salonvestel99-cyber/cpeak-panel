# -*- coding: utf-8 -*-
"""
1) Herkese acik sayfalar icin hafif base_seo.html olusturur
   (panel CSS'leri yuklenmez -> mobil duzelir)
2) index.html, hakkimizda.html, kurslar.html, iletisim.html bunu kullanir
3) Typewriter'i external JS'e tasir (CSP/timing sorunu cozulur)
Yedek + commit + push.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

# ============ base_seo.html ============
BASE_SEO = '''<!DOCTYPE html>
<html lang="tr">
<head>
<script>
(function () {
  try {
    var t = localStorage.getItem("cpeak_theme");
    if (!t && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      t = "dark";
    }
    if (t) {
      document.documentElement.setAttribute("data-theme", t);
      document.documentElement.classList.toggle("dark", t === "dark");
    }
  } catch (e) {}
})();
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=5.0">
<title>{% block title %}C-Peak English | İstanbul İngilizce Kursu{% endblock %}</title>
<meta name="description" content="{% block description %}C-Peak English, İstanbul Yıldırım'da küçük sınıflar ve modern yöntemlerle İngilizce eğitimi.{% endblock %}">
<meta name="robots" content="{% block robots %}index, follow{% endblock %}">
<link rel="canonical" href="{% block canonical %}https://www.cpeakenglish.com/{% endblock %}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="C-Peak English">
<meta property="og:title" content="{% block og_title %}C-Peak English | İstanbul İngilizce Kursu{% endblock %}">
<meta property="og:description" content="{% block og_description %}İstanbul Yıldırım'da İngilizce eğitim merkezi.{% endblock %}">
<meta property="og:url" content="{% block og_url %}https://www.cpeakenglish.com/{% endblock %}">
<meta property="og:image" content="{% block og_image %}https://www.cpeakenglish.com/static/logochrome.png{% endblock %}">
<meta property="og:locale" content="tr_TR">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block tw_title %}C-Peak English{% endblock %}">
<meta name="twitter:description" content="{% block tw_description %}İstanbul Yıldırım'da İngilizce eğitim merkezi.{% endblock %}">
<meta name="twitter:image" content="{% block tw_image %}https://www.cpeakenglish.com/static/logochrome.png{% endblock %}">

<link rel="icon" type="image/png" sizes="64x64" href="{{ url_for('static', filename='logochrome.png') }}">
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
<link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='apple-touch-icon.png') }}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Sadece gerekli CSS'ler (panel CSS'leri YOK) -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}?v=20260928_062847">
<link rel="stylesheet" href="{{ url_for('static', filename='hero.css') }}?v=20260928_062847">
<link rel="stylesheet" href="{{ url_for('static', filename='theme.css') }}?v=20260928_062847">
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=20261003d">

{% block head %}{% endblock %}
</head>
<body class="cpk-page {% block body_class %}{% endblock %}">
{% block body %}{% endblock %}
{% block scripts %}{% endblock %}
</body>
</html>
'''

# ============ hero_typewriter.js ============
TYPEWRITER_JS = '''/* C-Peak . Hero Typewriter V1
   Inline script calismazsa devreye girer (CSP/timing fallback).
   Idempotent: ayni h1'e iki kere yazmaz.
*/
(function () {
  "use strict";
  if (window.__cpkTypewriterV1) return;
  window.__cpkTypewriterV1 = true;

  function start() {
    var h1 = document.querySelector(".hero-typewriter");
    if (!h1) return false;
    var hedef = h1.getAttribute("data-metin");
    if (!hedef) return false;

    var span = h1.querySelector(".tw-text");
    if (!span) {
      span = document.createElement("span");
      span.className = "tw-text";
      h1.insertBefore(span, h1.firstChild);
    }

    /* Inline zaten yazmaya basladiysa dokunma */
    if (span.textContent && span.textContent.length > 1) return true;

    span.textContent = "";
    var i = 0;
    var HIZ = 45;

    function step() {
      if (i < hedef.length) {
        span.textContent = hedef.substring(0, i + 1);
        i++;
        setTimeout(step, HIZ);
      }
    }
    step();
    return true;
  }

  /* DOM hazir olunca calistir */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  /* Emniyet: inline script gec calisirsa 800ms sonra tekrar dene */
  setTimeout(start, 800);
})();
'''

# ============ Mobil landing fix ============
MOBILE_CSS = '''

/* =========================================================
   MOBILE LANDING FIX (base.html'deki panel CSS'lerini notrler)
   ========================================================= */
@media (max-width: 768px) {
  /* Panel CSS'lerin landing page'e sizmasini engelle */
  body.cpk-page {
    overflow-x: hidden !important;
  }
  body.cpk-page .cpk-header-inner {
    padding: 12px 16px !important;
  }
  body.cpk-page .cpk-nav {
    gap: 12px !important;
  }
  body.cpk-page .cpk-nav a:not(.cpk-nav-cta) {
    display: none !important;
  }
  body.cpk-page .cpk-nav-cta {
    padding: 8px 14px !important;
    font-size: .82rem !important;
    width: auto !important;
    white-space: nowrap;
  }
  body.cpk-page .topbar-brand-title {
    font-size: 1rem !important;
  }
  body.cpk-page .topbar-brand-sub {
    font-size: .58rem !important;
  }
  body.cpk-page .topbar-brand-mark img {
    height: 32px !important;
  }

  body.cpk-page .cpk-hero {
    padding: 44px 16px 56px !important;
  }
  body.cpk-page .cpk-hero .hero-brand {
    flex-direction: column !important;
    gap: 10px !important;
    margin-bottom: 22px !important;
  }
  body.cpk-page .cpk-hero .hero-brand-mark img {
    height: clamp(60px, 16vw, 78px) !important;
  }
  body.cpk-page .cpk-hero .hero-brand-title {
    font-size: clamp(1.4rem, 6.5vw, 1.9rem) !important;
  }
  body.cpk-page .cpk-hero-title {
    font-size: clamp(1.55rem, 7.5vw, 2.1rem) !important;
    line-height: 1.15 !important;
  }
  body.cpk-page .cpk-hero-lead {
    font-size: .94rem !important;
    padding: 0 4px;
  }
  body.cpk-page .cpk-hero-list {
    align-items: flex-start !important;
    padding-left: 4px;
    font-size: .9rem;
  }
  body.cpk-page .cpk-hero-cta {
    flex-direction: column !important;
    gap: 10px !important;
    align-items: stretch !important;
    padding: 0 4px;
  }
  body.cpk-page .cpk-hero-cta .cpk-btn-lg {
    width: 100% !important;
    justify-content: center !important;
    text-align: center;
  }
  body.cpk-page .cpk-hero-stats {
    flex-wrap: wrap !important;
    gap: 18px 22px !important;
    padding-top: 22px !important;
    margin-top: 30px !important;
  }
  body.cpk-page .cpk-hero-stats .hero-stat {
    min-width: 90px;
  }
  body.cpk-page .cpk-hero-stats .hero-stat strong {
    font-size: 1.35rem !important;
  }
  body.cpk-page .cpk-hero-stats .hero-stat span {
    font-size: .76rem !important;
  }

  body.cpk-page .cpk-section {
    padding: 52px 0 !important;
  }
  body.cpk-page .container {
    padding-left: 16px !important;
    padding-right: 16px !important;
  }
  body.cpk-page .cpk-h2 {
    font-size: clamp(1.35rem, 5.5vw, 1.75rem) !important;
  }
  body.cpk-page .cpk-grid {
    grid-template-columns: 1fr !important;
    gap: 14px !important;
  }
  body.cpk-page .cpk-features {
    grid-template-columns: 1fr !important;
    gap: 24px !important;
  }
  body.cpk-page .cpk-contact {
    grid-template-columns: 1fr !important;
    gap: 20px !important;
  }
  body.cpk-page .cpk-footer-inner {
    flex-direction: column !important;
    text-align: center !important;
    gap: 12px !important;
    padding: 22px 16px !important;
  }
  body.cpk-page .cpk-footer-links {
    flex-wrap: wrap !important;
    justify-content: center !important;
    gap: 14px !important;
  }

  /* Alt sayfalar (hakkimizda, kurslar, iletisim) */
  body.cpk-page .cpk-page-hero {
    padding: 42px 0 26px !important;
  }
  body.cpk-page .cpk-h1 {
    font-size: clamp(1.4rem, 6.5vw, 1.9rem) !important;
  }
  body.cpk-page .cpk-prose h2 {
    font-size: 1.2rem !important;
    margin-top: 30px !important;
  }
  body.cpk-page .cpk-course {
    padding: 20px 18px !important;
  }
  body.cpk-page .cpk-course-meta {
    grid-template-columns: 1fr !important;
  }
  body.cpk-page .cpk-contact-grid {
    grid-template-columns: 1fr !important;
    gap: 16px !important;
  }
  body.cpk-page .cpk-inline-cta {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  body.cpk-page .cpk-inline-cta .btn-primary,
  body.cpk-page .cpk-inline-cta .btn-ghost {
    width: 100% !important;
    justify-content: center !important;
    text-align: center;
  }
}
'''

def yedek(path):
    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print(f"  yedek: {bak}")

def yaz(path, icerik):
    if os.path.exists(path):
        mevcut = open(path, encoding="utf-8").read()
        if mevcut.strip() == icerik.strip():
            print(f"= {path} (zaten ayni)")
            return False
        yedek(path)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)
    print(f"+ {path} yazildi")
    return True

def extend_degistir(path):
    """{% extends "base.html" %} -> {% extends "base_seo.html" %}"""
    if not os.path.isfile(path):
        return False
    c = open(path, encoding="utf-8").read()
    if '{% extends "base_seo.html" %}' in c:
        print(f"= {path}: zaten base_seo kullaniyor")
        return False
    if '{% extends "base.html" %}' not in c:
        print(f"! {path}: extends bulunamadi")
        return False
    yedek(path)
    c2 = c.replace('{% extends "base.html" %}', '{% extends "base_seo.html" %}', 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print(f"+ {path}: base_seo.html'e gecirildi")
    return True

def login_typewriter_ekle():
    """login.html'e external typewriter JS ekle."""
    path = "templates/login.html"
    c = open(path, encoding="utf-8").read()
    if "hero_typewriter.js" in c:
        print("= login.html: typewriter JS zaten yuklu")
        return False
    if "</body>" not in c:
        print("! login.html: </body> bulunamadi")
        return False
    yedek(path)
    ekle = '<script src="{{ url_for(\'static\', filename=\'hero_typewriter.js\') }}?v=1" defer></script>\n'
    c2 = c.replace("</body>", ekle + "</body>", 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("+ login.html: hero_typewriter.js yuklendi")
    return True

def css_append():
    path = "static/index.css"
    if not os.path.isfile(path):
        return False
    c = open(path, encoding="utf-8").read()
    if "MOBILE LANDING FIX" in c:
        print("= index.css: mobil fix zaten var")
        return False
    yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c.rstrip() + "\n" + MOBILE_CSS)
    print("+ index.css: mobil landing fix eklendi")
    return True

def git(cmd, check=False):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()
    except FileNotFoundError:
        return False, "", "git yok"
    except subprocess.CalledProcessError as e:
        return False, (e.stdout or "").strip(), (e.stderr or "").strip()

def main():
    print("== Landing mobil fix + Typewriter fix ==\n")

    if not os.path.isfile("app.py"):
        print("HATA: app.py bulunamadi.")
        sys.exit(1)

    degisiklikler = []

    if yaz("templates/base_seo.html", BASE_SEO): degisiklikler.append("templates/base_seo.html")
    if yaz("static/hero_typewriter.js", TYPEWRITER_JS): degisiklikler.append("static/hero_typewriter.js")
    if css_append(): degisiklikler.append("static/index.css")

    for p in ["templates/index.html", "templates/hakkimizda.html",
              "templates/kurslar.html", "templates/iletisim.html"]:
        if extend_degistir(p): degisiklikler.append(p)

    if login_typewriter_ekle(): degisiklikler.append("templates/login.html")

    if not degisiklikler:
        print("\nHicbir degisiklik yok.")
        return

    print("\n-- git islemleri --")
    git(["git", "add"] + degisiklikler)
    ok, out, err = git(["git", "commit", "-m",
        "fix(landing): hafif base_seo + mobil fix; fix(login): typewriter external JS"])
    if ok:
        print("commit OK")
    else:
        print(f"commit: {err[:200]}")

    ok, br, _ = git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    br = br or "main"
    ok, _, err = git(["git", "push", "origin", br])
    print(f"push: {'OK (origin/' + br + ')' if ok else 'HATA: ' + err}")

    print("\n== BITTI ==")
    print("Deploy sonrasi test:")
    print("  https://www.cpeakenglish.com/  (mobil ve masaustu)")
    print("  https://www.cpeakenglish.com/hakkimizda")
    print("  https://www.cpeakenglish.com/kurslar")
    print("  https://www.cpeakenglish.com/iletisim")
    print("  https://www.cpeakenglish.com/giris  (typewriter calismali)")

if __name__ == "__main__":
    main()