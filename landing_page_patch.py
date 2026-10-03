# -*- coding: utf-8 -*-
"""
C-Peak English — Landing Page Patch
-----------------------------------
1) templates/base_public.html olusturur
2) templates/index.html olusturur
3) static/index.css olusturur
4) app.py'deki "/" route'unu landing page kullanacak sekilde degistirir
5) git add + commit + push
Idempotent, yedek alir.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

# ============================================================
# ICERIKLER
# ============================================================

BASE_PUBLIC = '''<!DOCTYPE html>
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
<title>{% block title %}C-Peak English | Istanbul Ingilizce Kursu{% endblock %}</title>

<meta name="description" content="{% block description %}C-Peak English, Istanbul Yildirim'da ogrenci, veli ve ogretmenlere ozel Ingilizce egitim merkezi. Kucuk siniflar, deneyimli ogretmenler, dijital takip sistemi.{% endblock %}">
<meta name="robots" content="{% block robots %}index, follow{% endblock %}">
<link rel="canonical" href="{% block canonical %}https://www.cpeakenglish.com/{% endblock %}">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="C-Peak English">
<meta property="og:title" content="{% block og_title %}C-Peak English | Istanbul Ingilizce Kursu{% endblock %}">
<meta property="og:description" content="{% block og_description %}Istanbul Yildirim'da ogrenci, veli ve ogretmenlere ozel Ingilizce egitim merkezi.{% endblock %}">
<meta property="og:url" content="{% block og_url %}https://www.cpeakenglish.com/{% endblock %}">
<meta property="og:image" content="{% block og_image %}https://www.cpeakenglish.com/static/logochrome.png{% endblock %}">
<meta property="og:locale" content="tr_TR">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block tw_title %}C-Peak English | Istanbul Ingilizce Kursu{% endblock %}">
<meta name="twitter:description" content="{% block tw_description %}Istanbul Yildirim'da ogrenci, veli ve ogretmenlere ozel Ingilizce egitim merkezi.{% endblock %}">
<meta name="twitter:image" content="{% block tw_image %}https://www.cpeakenglish.com/static/logochrome.png{% endblock %}">

<link rel="icon" type="image/png" sizes="64x64" href="{{ url_for('static', filename='logochrome.png') }}">
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
<link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='apple-touch-icon.png') }}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}?v=20260928_062847">
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=1">

{% block head %}{% endblock %}
</head>
<body class="lp-body {% block body_class %}{% endblock %}">
{% block content %}{% endblock %}
{% block scripts %}{% endblock %}
</body>
</html>
'''

INDEX_HTML = '''{% extends "base_public.html" %}

{% block title %}C-Peak English | Istanbul Ingilizce Kursu{% endblock %}
{% block description %}C-Peak English, Istanbul Yildirim'da kucuk siniflarda deneyimli ogretmenlerle Ingilizce egitimi. Ogrenci, veli ve ogretmen panelleri ile takip edilebilir.{% endblock %}

{% block head %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "C-Peak English",
  "url": "https://www.cpeakenglish.com",
  "logo": "https://www.cpeakenglish.com/static/logochrome.png",
  "description": "Istanbul Yildirim'da ogrenci, veli ve ogretmenlere ozel Ingilizce egitim merkezi.",
  "telephone": "+905421808402",
  "email": "cpeakenglish@gmail.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Yildirim Mahallesi, Bosna Sokak No: 29/A",
    "addressLocality": "Istanbul",
    "addressCountry": "TR"
  },
  "sameAs": [
    "https://www.instagram.com/c_peak_english",
    "https://www.youtube.com/@c-peak-english"
  ]
}
</script>
{% endblock %}

{% block content %}
<header class="lp-header">
  <div class="lp-container lp-header-inner">
    <a href="/" class="lp-logo">
      <img src="{{ url_for('static', filename='logochrome.png') }}" alt="C-Peak English" width="44" height="44">
      <span>C-Peak English</span>
    </a>
    <nav class="lp-nav">
      <a href="#hakkimizda">Hakkimizda</a>
      <a href="#kurslar">Kurslar</a>
      <a href="#iletisim">Iletisim</a>
      <a href="{{ url_for('login') }}" class="lp-btn lp-btn-primary">Giris Yap</a>
    </nav>
  </div>
</header>

<main>
  <section class="lp-hero">
    <div class="lp-container">
      <h1>Ingilizceyi <span class="lp-highlight">Zirveye</span> Tasi</h1>
      <p class="lp-subtitle">
        Istanbul Yildirim'da kucuk siniflar, deneyimli ogretmenler ve dijital takip sistemiyle
        ogrenci, veli ve ogretmen odakli Ingilizce egitimi.
      </p>
      <div class="lp-cta">
        <a href="#kurslar" class="lp-btn lp-btn-primary lp-btn-lg">Kurslari Kesfet</a>
        <a href="#iletisim" class="lp-btn lp-btn-outline lp-btn-lg">Bize Ulas</a>
      </div>
    </div>
  </section>

  <section class="lp-section" id="hakkimizda">
    <div class="lp-container">
      <h2>Hakkimizda</h2>
      <p>
        C-Peak English, Ingilizce ogrenmeyi kolaylastiran ve takip edilebilir kilan modern bir
        egitim merkezidir. Ogrencilerimizin gelisimini velilerle ve ogretmenlerle seffaf bir
        sekilde paylasiyor, her adimda yanlarinda oluyoruz.
      </p>
    </div>
  </section>

  <section class="lp-section lp-section-alt" id="kurslar">
    <div class="lp-container">
      <h2>Kurslarimiz</h2>
      <div class="lp-grid">
        <div class="lp-card">
          <h3>Genel Ingilizce</h3>
          <p>Temel seviyeden ileri seviyeye kadar konusma, dinleme, okuma ve yazma becerileri.</p>
        </div>
        <div class="lp-card">
          <h3>Sinav Hazirlik</h3>
          <p>YDS, YDT, TOEFL, IELTS gibi sinavlara yonelik ozel programlar.</p>
        </div>
        <div class="lp-card">
          <h3>Konusma Kulubu</h3>
          <p>Gercek hayat senaryolari ile pratik yaparak akici konusma becerisi kazanma.</p>
        </div>
        <div class="lp-card">
          <h3>Ogrenci & Veli Paneli</h3>
          <p>Ders programi, odevler, bildirimler ve gelisim takibi tek bir panelde.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="lp-section" id="iletisim">
    <div class="lp-container">
      <h2>Iletisim</h2>
      <div class="lp-contact">
        <div class="lp-contact-item">
          <strong>Adres</strong>
          <p>Yildirim Mahallesi, Bosna Sokak No: 29/A, Istanbul</p>
        </div>
        <div class="lp-contact-item">
          <strong>Telefon</strong>
          <p><a href="tel:+905421808402">0542 180 84 02</a></p>
        </div>
        <div class="lp-contact-item">
          <strong>E-posta</strong>
          <p></p>
        </div>
        <div class="lp-contact-item">
          <strong>Sosyal Medya</strong>
          <p>
            <a href="https://www.instagram.com/c_peak_english" target="_blank" rel="noopener">Instagram</a> &middot;
            <a href="https://www.youtube.com/@c-peak-english" target="_blank" rel="noopener">YouTube</a>
          </p>
        </div>
      </div>
    </div>
  </section>
</main>

<footer class="lp-footer">
  <div class="lp-container">
    <p>&copy; 2026 C-Peak English. Tum haklari saklidir. &middot; <a href="{{ url_for('kvkk') }}">KVKK</a></p>
  </div>
</footer>
{% endblock %}
'''

INDEX_CSS = '''/* C-Peak English - Landing Page */

.lp-body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: #f8fafc;
  color: #1e293b;
  line-height: 1.6;
}

html[data-theme="dark"] .lp-body,
html.dark .lp-body {
  background: #0f172a;
  color: #e2e8f0;
}

.lp-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

.lp-header {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  z-index: 100;
}

html[data-theme="dark"] .lp-header,
html.dark .lp-header {
  background: rgba(15, 23, 42, 0.92);
  border-bottom-color: rgba(255, 255, 255, 0.08);
}

.lp-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 68px;
}

.lp-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Fraunces', serif;
  font-weight: 600;
  font-size: 18px;
  color: inherit;
  text-decoration: none;
}

.lp-nav {
  display: flex;
  align-items: center;
  gap: 24px;
}

.lp-nav a {
  color: inherit;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  opacity: 0.85;
}

.lp-nav a:hover { opacity: 1; }

.lp-btn {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  border: 1px solid transparent;
  transition: all 0.15s ease;
  cursor: pointer;
}

.lp-btn-primary {
  background: #2563eb;
  color: #fff;
}

.lp-btn-primary:hover { background: #1d4ed8; }

.lp-btn-outline {
  background: transparent;
  color: inherit;
  border-color: rgba(0, 0, 0, 0.15);
}

.lp-btn-outline:hover { border-color: rgba(0, 0, 0, 0.35); }

.lp-btn-lg {
  padding: 14px 28px;
  font-size: 16px;
}

.lp-hero {
  padding: 100px 0 80px;
  text-align: center;
}

.lp-hero h1 {
  font-family: 'Fraunces', serif;
  font-size: 56px;
  line-height: 1.1;
  font-weight: 600;
  margin: 0 0 24px;
  letter-spacing: -0.02em;
}

.lp-highlight {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.lp-subtitle {
  font-size: 19px;
  max-width: 640px;
  margin: 0 auto 36px;
  opacity: 0.75;
}

.lp-cta {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

.lp-section {
  padding: 80px 0;
}

.lp-section-alt {
  background: rgba(0, 0, 0, 0.025);
}

html[data-theme="dark"] .lp-section-alt,
html.dark .lp-section-alt {
  background: rgba(255, 255, 255, 0.03);
}

.lp-section h2 {
  font-family: 'Fraunces', serif;
  font-size: 36px;
  font-weight: 600;
  margin: 0 0 24px;
  text-align: center;
}

.lp-section > .lp-container > p {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
  font-size: 17px;
  opacity: 0.8;
}

.lp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.lp-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

html[data-theme="dark"] .lp-card,
html.dark .lp-card {
  background: #1e293b;
  border-color: rgba(255, 255, 255, 0.08);
}

.lp-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
}

.lp-card h3 {
  font-family: 'Fraunces', serif;
  font-size: 19px;
  margin: 0 0 10px;
}

.lp-card p {
  margin: 0;
  font-size: 15px;
  opacity: 0.75;
}

.lp-contact {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-top: 40px;
}

.lp-contact-item strong {
  display: block;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  opacity: 0.6;
  margin-bottom: 6px;
}

.lp-contact-item p {
  margin: 0;
  font-size: 16px;
}

.lp-contact-item a {
  color: inherit;
  text-decoration: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.15);
}

html[data-theme="dark"] .lp-contact-item a,
html.dark .lp-contact-item a {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.lp-footer {
  padding: 40px 0;
  text-align: center;
  font-size: 14px;
  opacity: 0.65;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

html[data-theme="dark"] .lp-footer,
html.dark .lp-footer {
  border-top-color: rgba(255, 255, 255, 0.08);
}

.lp-footer a {
  color: inherit;
}

@media (max-width: 768px) {
  .lp-nav {
    gap: 14px;
  }
  .lp-nav a:not(.lp-btn) {
    display: none;
  }
  .lp-hero {
    padding: 60px 0 50px;
  }
  .lp-hero h1 {
    font-size: 36px;
  }
  .lp-subtitle {
    font-size: 16px;
  }
  .lp-section {
    padding: 56px 0;
  }
  .lp-section h2 {
    font-size: 28px;
  }
  .lp-btn-lg {
    padding: 12px 22px;
    font-size: 15px;
  }
}
'''

# ============================================================
# YARDIMCI
# ============================================================

def yaz(path, icerik, force=False):
    """Dosyayi yazar. Zaten varsa ve force degilse atlar."""
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    if os.path.exists(path) and not force:
        mevcut = open(path, encoding="utf-8").read()
        if mevcut.strip() == icerik.strip():
            print(f"= {path} (zaten ayni, atlandi)")
            return False
        else:
            print(f"! {path} farkli icerikle var, UZERINE YAZILDI")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)
    print(f"+ {path} yazildi")
    return True

def yedek(path):
    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print(f"  yedek: {bak}")

def git(cmd, check=False):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()
    except FileNotFoundError:
        return False, "", "git bulunamadi"
    except subprocess.CalledProcessError as e:
        return False, (e.stdout or "").strip(), (e.stderr or "").strip()

# ============================================================
# ANA AKIS
# ============================================================

def main():
    print("== C-Peak English Landing Page Patch ==\n")

    # Proje kokunde miyiz?
    if not os.path.isfile("app.py"):
        print("HATA: app.py bulunamadi. Betigi cpeak klasorunde calistirin.")
        sys.exit(1)

    degisiklikler = []

    # 1) templates/base_public.html
    if yaz("templates/base_public.html", BASE_PUBLIC):
        degisiklikler.append("templates/base_public.html")

    # 2) templates/index.html
    if yaz("templates/index.html", INDEX_HTML):
        degisiklikler.append("templates/index.html")

    # 3) static/index.css
    if yaz("static/index.css", INDEX_CSS):
        degisiklikler.append("static/index.css")

    # 4) app.py - "/" route guncelle
    print()
    yedek("app.py")
    c = open("app.py", encoding="utf-8").read()
    orig = c

    eski_pattern = re.compile(
        r'@app\.route\("/"\)\s*\ndef index\(\):\s*\n\s*return redirect\(url_for\("dashboard"\) if "user_id" in session else url_for\("login"\)\)',
        re.MULTILINE
    )
    yeni = (
        '@app.route("/")\n'
        'def index():\n'
        '    if "user_id" in session:\n'
        '        return redirect(url_for("dashboard"))\n'
        '    return render_template("index.html")'
    )

    if eski_pattern.search(c):
        c = eski_pattern.sub(yeni, c, count=1)
        print("+ app.py: / route guncellendi (landing page aktif)")
        degisiklikler.append("app.py")
    elif 'return render_template("index.html")' in c:
        print("= app.py: / route zaten guncel, atlandi")
    else:
        print("! app.py: beklenen / route bulunamadi. Manuel kontrol gerek.")
        print("  Beklenen:")
        print('    @app.route("/")')
        print('    def index():')
        print('        return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))')

    # render_template import kontrol
    if "render_template" not in c.split("\n\n")[0] and "from flask import" in c:
        m = re.search(r"^from flask import (.+)$", c, re.MULTILINE)
        if m and "render_template" not in m.group(1):
            eski_import = m.group(0)
            yeni_import = eski_import.rstrip() + ", render_template"
            c = c.replace(eski_import, yeni_import, 1)
            print("+ app.py: render_template import eklendi")

    if c != orig:
        open("app.py", "w", encoding="utf-8", newline="\n").write(c)

    if not degisiklikler:
        print("\nHicbir degisiklik yok. Push yapilmadi.")
        return

    # 5) git add + commit + push
    print("\n-- git islemleri --")
    dosyalar = [d for d in degisiklikler if os.path.exists(d)]
    ok, _, err = git(["git", "add"] + dosyalar)
    if not ok:
        print(f"git add HATA: {err}")

    ok, out, err = git(["git", "commit", "-m",
                        "feat: SEO icin herkese acik landing page eklendi"])
    if ok:
        print("commit OK")
    else:
        if "nothing to commit" in (out + err).lower():
            print("commit edilecek sey yok")
        else:
            print(f"commit HATA: {err}")

    # Branch
    ok, br, _ = git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    br = br or "main"

    ok, out, err = git(["git", "push", "origin", br])
    if ok:
        print(f"push OK (origin/{br})")
    else:
        print(f"push HATA: {err}")
        print(f"Manuel: git push origin {br}")

    print("\n== BITTI ==")
    print("Sonraki adim: Render'da deploy bitince test et:")
    print("  https://www.cpeakenglish.com/")
    print("  https://www.cpeakenglish.com/giris")

if __name__ == "__main__":
    main()