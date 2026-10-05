# -*- coding: utf-8 -*-
"""
1) Ana sayfa hero stats'i 4 kartla degistirir
2) Kurslar sayfasini gercek duruma uygun icerikle yeniden yazar
Yedek + commit + push.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

# ============ YENI HERO STATS ============
YENI_STATS = '''<div class="hero-stats cpk-hero-stats">
        <div class="hero-stat">
          <strong>150+</strong>
          <span>Mutlu Öğrenci</span>
        </div>
        <div class="hero-stat">
          <strong>4</strong>
          <span>Temel Beceri</span>
        </div>
        <div class="hero-stat">
          <strong>Konuşma</strong>
          <span>Odaklı Eğitim</span>
        </div>
        <div class="hero-stat">
          <strong>A1–C1</strong>
          <span>CEFR Uyumlu</span>
        </div>
      </div>'''

# ============ YENI KURSLAR SAYFASI ============
KURSLAR_HTML = '''{% extends "base_seo.html" %}

{% block title %}Kurslar — C-Peak English | İlkokul & Ortaokul İngilizce{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block description %}C-Peak English, ilkokul ve ortaokul öğrencilerine konuşma odaklı İngilizce eğitimi sunar. Küçük sınıflar, A1–C1 CEFR uyumlu program, öğrenci–veli–öğretmen dijital takip paneli.{% endblock %}
{% block canonical %}https://www.cpeakenglish.com/kurslar{% endblock %}
{% block og_title %}Kurslar — C-Peak English{% endblock %}
{% block og_description %}İlkokul ve ortaokul öğrencilerine konuşma odaklı, CEFR uyumlu İngilizce eğitimi.{% endblock %}
{% block og_url %}https://www.cpeakenglish.com/kurslar{% endblock %}
{% block tw_title %}Kurslar — C-Peak English{% endblock %}
{% block tw_description %}İlkokul ve ortaokul öğrencilerine konuşma odaklı İngilizce eğitimi.{% endblock %}

{% block head %}
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=20261003e">
{% endblock %}

{% block body %}

<header class="cpk-header">
  <div class="cpk-header-inner">
    <a href="/" class="topbar-brand">
      <span class="topbar-brand-mark">
        <img src="{{ url_for('static', filename='logochrome.png') }}" alt="C · Peak English">
      </span>
      <span class="topbar-brand-text">
        <span class="topbar-brand-title">C · Peak</span>
        <span class="topbar-brand-sep"></span>
        <span class="topbar-brand-sub" lang="en">ENGLISH</span>
      </span>
    </a>
    <nav class="cpk-nav">
      <a href="/hakkimizda">Hakkımızda</a>
      <a href="/kurslar">Kurslar</a>
      <a href="/iletisim">İletişim</a>
      <a href="{{ url_for('login') }}" class="btn-primary cpk-nav-cta">Giriş Yap</a>
    </nav>
  </div>
</header>

<main class="cpk-main">

  <section class="cpk-page-hero">
    <div class="container">
      <span class="cpk-eyebrow">Programlarımız</span>
      <h1 class="cpk-h1">İlkokul ve ortaokul için <em>konuşma odaklı</em> İngilizce</h1>
      <p class="cpk-lead">
        C-Peak English, ilkokul ve ortaokul öğrencilerine yönelik A1–C1 CEFR uyumlu,
        küçük sınıflarda birebir ilgiyle yürütülen konuşma odaklı bir program sunar.
        Dört temel beceriyi (dinleme, konuşma, okuma, yazma) dengeli şekilde geliştiriyoruz.
      </p>
    </div>
  </section>

  <section class="cpk-section">
    <div class="container">
      <div class="cpk-course-list">

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">İ</div>
            <h2>İlkokul İngilizce (1–4. Sınıf)</h2>
          </div>
          <p class="cpk-course-desc">
            Oyunlar, şarkılar, hikâyeler ve interaktif aktivitelerle İngilizceyi sevdirerek
            öğretiyoruz. Bu yaş grubunda önceliğimiz doğru telaffuz, temel kelime hazinesi
            ve İngilizceyi kullanma özgüveni kazandırmaktır.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Yaş grubu:</strong> 6–10 yaş</li>
            <li><strong>Seviye:</strong> A1 – A2</li>
            <li><strong>Yaklaşım:</strong> Oyun temelli öğrenme</li>
            <li><strong>Odak:</strong> Dinleme, konuşma, kelime</li>
          </ul>
        </article>

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">O</div>
            <h2>Ortaokul İngilizce (5–8. Sınıf)</h2>
          </div>
          <p class="cpk-course-desc">
            MEB müfredatıyla uyumlu, okul başarısını destekleyen ve LGS'ye hazırlayan program.
            Dil bilgisi, okuma-anlama ve yazma becerilerinin yanı sıra konuşma pratiğine
            ağırlık veriyoruz.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Yaş grubu:</strong> 10–14 yaş</li>
            <li><strong>Seviye:</strong> A2 – B2</li>
            <li><strong>Yaklaşım:</strong> MEB müfredatı + LGS hazırlık</li>
            <li><strong>Odak:</strong> Gramer, okuma, yazma, konuşma</li>
          </ul>
        </article>

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">K</div>
            <h2>Konuşma Odaklı Eğitim</h2>
          </div>
          <p class="cpk-course-desc">
            Dört temel beceriyi (dinleme, konuşma, okuma, yazma) dengeli geliştirirken, en çok
            konuşma pratiğine ağırlık veriyoruz. Öğrencilerimiz gerçek hayat senaryoları ile
            İngilizceyi aktif olarak kullanır.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Odak:</strong> Konuşma ve telaffuz</li>
            <li><strong>Format:</strong> Küçük gruplar, aktif katılım</li>
            <li><strong>Kazanım:</strong> Akıcılık ve özgüven</li>
            <li><strong>Uyum:</strong> CEFR A1 – C1</li>
          </ul>
        </article>

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">P</div>
            <h2>Online Takip Paneli</h2>
          </div>
          <p class="cpk-course-desc">
            Tüm programlarımıza dahil olan dijital takip sistemi ile öğrenci, veli ve öğretmen
            aynı platformda buluşur. Böylece gelişim şeffaf şekilde takip edilir ve iletişim
            güçlenir.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Ders programı:</strong> Anlık güncel</li>
            <li><strong>Ödevler:</strong> Dijital atanır ve takip edilir</li>
            <li><strong>Bildirimler:</strong> Otomatik iletilir</li>
            <li><strong>Veli erişimi:</strong> Gelişim şeffaf görülür</li>
          </ul>
        </article>

      </div>
    </div>
  </section>

  <section class="cpk-section cpk-section-alt">
    <div class="container cpk-section-inner">
      <span class="cpk-eyebrow">Kayıt &amp; Bilgi</span>
      <h2 class="cpk-h2">Çocuğunuz için en uygun programı <em>birlikte</em> belirleyelim</h2>
      <p class="cpk-lead">
        Seviye tespit görüşmesiyle başlayalım, çocuğunuzun seviyesini ve hedefini birlikte
        değerlendirelim. Kayıt ve ücret bilgisi için bize ulaşın.
      </p>
      <div class="cpk-inline-cta">
        <a href="/iletisim" class="btn-primary btn-copper">Bize Ulaşın</a>
        <a href="tel:+905421808402" class="btn-ghost">0542 180 84 02</a>
      </div>
    </div>
  </section>

</main>

<footer class="cpk-footer">
  <div class="container cpk-footer-inner">
    <span>© 2026 C-Peak English. Tüm hakları saklıdır.</span>
    <span class="cpk-footer-links">
      <a href="/hakkimizda">Hakkımızda</a>
      <a href="/kurslar">Kurslar</a>
      <a href="/iletisim">İletişim</a>
      <a href="/kvkk">KVKK</a>
      <a href="{{ url_for('login') }}">Giriş Yap</a>
    </span>
  </div>
</footer>

{% endblock %}
'''

# ============ YENI STATS ICIN EK CSS (4 kart + uzun kelimeler) ============
STATS_CSS = '''

/* =========================================================
   4'LU HERO STATS + Konuşma / A1-C1 gibi metin degerleri
   ========================================================= */
.cpk-hero-stats {
  display: flex !important;
  flex-wrap: wrap !important;
  justify-content: center !important;
  gap: 24px 40px !important;
  max-width: 780px !important;
}
.cpk-hero-stats .hero-stat {
  align-items: center !important;
  text-align: center !important;
  min-width: 100px;
}
.cpk-hero-stats .hero-stat strong {
  font-size: 1.55rem !important;
  line-height: 1.1 !important;
}
/* Metinsel degerler (Konuşma, A1–C1) icin hafif kucultme */
.cpk-hero-stats .hero-stat strong:not([data-num]) {
  font-size: 1.35rem !important;
}

@media (max-width: 768px) {
  .cpk-hero-stats {
    gap: 18px 24px !important;
    padding-top: 22px !important;
    margin-top: 26px !important;
  }
  .cpk-hero-stats .hero-stat {
    min-width: 80px;
    flex: 0 0 auto;
  }
  .cpk-hero-stats .hero-stat strong {
    font-size: 1.25rem !important;
  }
  .cpk-hero-stats .hero-stat strong:not([data-num]) {
    font-size: 1.05rem !important;
  }
  .cpk-hero-stats .hero-stat span {
    font-size: .72rem !important;
  }
}
'''

def yedek(path):
    bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, bak)
    print(f"  yedek: {bak}")

def index_stats_guncelle():
    """index.html hero-stats bloğunu 4'lu versiyonla degistirir."""
    path = "templates/index.html"
    if not os.path.isfile(path):
        print("! index.html bulunamadi")
        return False

    c = open(path, encoding="utf-8").read()
    if "<strong>150+</strong>" in c and "Konuşma" in c and "CEFR Uyumlu" in c:
        print("= index.html: yeni stats zaten var")
        return False

    # Eski hero-stats bloğunu bul ve değiştir
    pattern = re.compile(
        r'<div class="hero-stats cpk-hero-stats">.*?</div>\s*</div>\s*</div>',
        re.DOTALL
    )
    m = pattern.search(c)
    if not m:
        print("! index.html: hero-stats bulunamadi")
        return False

    # Kapanis etiketlerini koru (son iki </div>)
    son_kapanis = "</div>\n    </div>"
    yeni_blok = YENI_STATS + "\n    </div>"
    c2 = c[:m.start()] + yeni_blok + c[m.end():]

    yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c2)
    print("+ index.html: hero stats 4 kartla guncellendi")
    return True

def kurslar_guncelle():
    """kurslar.html'i tamamen yeniden yazar."""
    path = "templates/kurslar.html"
    if os.path.isfile(path):
        mevcut = open(path, encoding="utf-8").read()
        if "İlkokul İngilizce (1–4. Sınıf)" in mevcut:
            print("= kurslar.html: yeni icerik zaten var")
            return False
        yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(KURSLAR_HTML)
    print("+ kurslar.html: ilkokul/ortaokul icerigi ile yeniden yazildi")
    return True

def stats_css_ekle():
    path = "static/index.css"
    if not os.path.isfile(path):
        return False
    c = open(path, encoding="utf-8").read()
    if "4'LU HERO STATS" in c:
        print("= index.css: stats css zaten var")
        return False
    yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c.rstrip() + "\n" + STATS_CSS)
    print("+ static/index.css: 4'lu stats stili eklendi")
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
    print("== Icerik Guncelleme: stats + kurslar ==\n")
    if not os.path.isfile("app.py"):
        print("HATA: app.py bulunamadi.")
        sys.exit(1)

    degisiklikler = []
    if index_stats_guncelle(): degisiklikler.append("templates/index.html")
    if kurslar_guncelle():     degisiklikler.append("templates/kurslar.html")
    if stats_css_ekle():       degisiklikler.append("static/index.css")

    if not degisiklikler:
        print("\nHicbir degisiklik yok.")
        return

    print("\n-- git islemleri --")
    git(["git", "add"] + degisiklikler)
    ok, out, err = git(["git", "commit", "-m",
        "content: hero stats 4 kart, kurslar ilkokul/ortaokul odakli yeniden yazildi"])
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
    print("  https://www.cpeakenglish.com/         (4 stats: 150+ / 4 / Konuşma / A1-C1)")
    print("  https://www.cpeakenglish.com/kurslar  (ilkokul + ortaokul + konuşma + panel)")

if __name__ == "__main__":
    main()