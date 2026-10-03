# -*- coding: utf-8 -*-
"""
C-Peak English — Landing Page v2 (tema uyumlu)
Mevcut kömür+bakır temasını kullanır, base.html'i extend eder.
"""
import os, shutil, subprocess, sys
from datetime import datetime

INDEX_HTML = '''{% extends "base.html" %}

{% block title %}C-Peak English — İstanbul İngilizce Kursu{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block head %}
<meta name="description" content="C-Peak English, İstanbul Yıldırım'da küçük sınıflar, deneyimli öğretmenler ve dijital takip sistemiyle öğrenci, veli ve öğretmen odaklı İngilizce eğitimi sunar.">
<link rel="canonical" href="https://www.cpeakenglish.com/">

<meta property="og:type" content="website">
<meta property="og:site_name" content="C-Peak English">
<meta property="og:title" content="C-Peak English — İstanbul İngilizce Kursu">
<meta property="og:description" content="İstanbul Yıldırım'da öğrenci, veli ve öğretmen odaklı İngilizce eğitim merkezi.">
<meta property="og:url" content="https://www.cpeakenglish.com/">
<meta property="og:image" content="https://www.cpeakenglish.com/static/logochrome.png">
<meta property="og:locale" content="tr_TR">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="C-Peak English — İstanbul İngilizce Kursu">
<meta name="twitter:description" content="İstanbul Yıldırım'da öğrenci, veli ve öğretmen odaklı İngilizce eğitim merkezi.">
<meta name="twitter:image" content="https://www.cpeakenglish.com/static/logochrome.png">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "C-Peak English",
  "url": "https://www.cpeakenglish.com",
  "logo": "https://www.cpeakenglish.com/static/logochrome.png",
  "description": "İstanbul Yıldırım'da öğrenci, veli ve öğretmenlere özel İngilizce eğitim merkezi.",
  "telephone": "+905421808402",
  "email": "cpeakenglish@gmail.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Yıldırım Mahallesi, Bosna Sokak No: 29/A",
    "addressLocality": "İstanbul",
    "addressCountry": "TR"
  },
  "sameAs": [
    "https://www.instagram.com/c_peak_english",
    "https://www.youtube.com/@c-peak-english"
  ]
}
</script>

<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=20261003b">
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
      <a href="#hakkimizda">Hakkımızda</a>
      <a href="#kurslar">Kurslar</a>
      <a href="#neden">Neden Biz</a>
      <a href="#iletisim">İletişim</a>
      <a href="{{ url_for('login') }}" class="btn-primary cpk-nav-cta">Giriş Yap</a>
    </nav>
  </div>
</header>

<main class="cpk-main">

  <!-- ============== HERO ============== -->
  <section class="cpk-hero">
    <div class="cpk-hero-inner">
      <div class="cpk-hero-brand hero-brand">
        <span class="hero-brand-mark">
          <img src="{{ url_for('static', filename='logochrome.png') }}" alt="C · Peak English">
        </span>
        <span class="hero-brand-text">
          <span class="hero-brand-title">C · Peak</span>
          <span class="hero-brand-sub" lang="en">ENGLISH</span>
        </span>
      </div>

      <h1 class="cpk-hero-title">İngilizceyi <span class="cpk-copper">Zirveye</span> Taşı</h1>

      <p class="cpk-hero-lead">
        İstanbul Yıldırım'da küçük sınıflar, deneyimli öğretmenler ve dijital takip sistemiyle
        öğrenci, veli ve öğretmen odaklı İngilizce eğitimi.
      </p>

      <ul class="hero-list cpk-hero-list">
        <li>Küçük sınıflarda birebir ilgi</li>
        <li>Deneyimli ve sertifikalı öğretmenler</li>
        <li>Öğrenci, veli ve öğretmen panelleri ile şeffaf takip</li>
      </ul>

      <div class="cpk-hero-cta">
        <a href="#kurslar" class="btn-primary btn-copper cpk-btn-lg">Kursları Keşfet</a>
        <a href="#iletisim" class="btn-ghost cpk-btn-lg cpk-btn-ghost-light">Bize Ulaş</a>
      </div>

      <div class="hero-stats cpk-hero-stats">
        <div class="hero-stat">
          <strong>500+</strong>
          <span>Mutlu Öğrenci</span>
        </div>
        <div class="hero-stat">
          <strong>10+</strong>
          <span>Yıllık Deneyim</span>
        </div>
        <div class="hero-stat">
          <strong>%98</strong>
          <span>Veli Memnuniyeti</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ============== HAKKIMIZDA ============== -->
  <section class="cpk-section" id="hakkimizda">
    <div class="container cpk-section-inner">
      <span class="cpk-eyebrow">Hakkımızda</span>
      <h2 class="cpk-h2">İngilizce öğrenmeyi <em>kolaylaştırıyoruz</em></h2>
      <p class="cpk-lead">
        C-Peak English, İngilizce öğrenmeyi kolaylaştıran ve takip edilebilir kılan modern bir
        eğitim merkezidir. Öğrencilerimizin gelişimini velilerle ve öğretmenlerle şeffaf bir
        şekilde paylaşıyor, her adımda yanlarında oluyoruz.
      </p>
    </div>
  </section>

  <!-- ============== KURSLAR ============== -->
  <section class="cpk-section cpk-section-alt" id="kurslar">
    <div class="container cpk-section-inner">
      <span class="cpk-eyebrow">Kurslarımız</span>
      <h2 class="cpk-h2">Her seviyeye uygun programlar</h2>

      <div class="cpk-grid">
        <article class="cpk-card">
          <div class="cpk-card-icon">A</div>
          <h3>Genel İngilizce</h3>
          <p>Temel seviyeden ileri seviyeye kadar konuşma, dinleme, okuma ve yazma becerileri.</p>
        </article>

        <article class="cpk-card">
          <div class="cpk-card-icon">B</div>
          <h3>Sınav Hazırlık</h3>
          <p>YDS, YDT, TOEFL ve IELTS gibi sınavlara yönelik özel hazırlık programları.</p>
        </article>

        <article class="cpk-card">
          <div class="cpk-card-icon">C</div>
          <h3>Konuşma Kulübü</h3>
          <p>Gerçek hayat senaryoları ile pratik yaparak akıcı konuşma becerisi kazanın.</p>
        </article>

        <article class="cpk-card">
          <div class="cpk-card-icon">D</div>
          <h3>Online Takip Paneli</h3>
          <p>Ders programı, ödevler, bildirimler ve gelişim takibi tek bir panelde.</p>
        </article>
      </div>
    </div>
  </section>

  <!-- ============== NEDEN BİZ ============== -->
  <section class="cpk-section" id="neden">
    <div class="container cpk-section-inner">
      <span class="cpk-eyebrow">Neden C-Peak?</span>
      <h2 class="cpk-h2">Farkımız <em>insan odaklı</em> yaklaşımımız</h2>

      <div class="cpk-features">
        <div class="cpk-feature">
          <span class="cpk-feature-num">01</span>
          <h4>Küçük Sınıflar</h4>
          <p>Her öğrencimize yeterli zaman ayırabilmek için sınıflarımızı küçük tutuyoruz.</p>
        </div>
        <div class="cpk-feature">
          <span class="cpk-feature-num">02</span>
          <h4>Şeffaf Takip</h4>
          <p>Veli ve öğretmenler öğrenci gelişimini online panelden takip edebilir.</p>
        </div>
        <div class="cpk-feature">
          <span class="cpk-feature-num">03</span>
          <h4>Kişiye Özel Program</h4>
          <p>Her öğrencinin seviyesine ve hedefine göre program hazırlıyoruz.</p>
        </div>
        <div class="cpk-feature">
          <span class="cpk-feature-num">04</span>
          <h4>Modern Materyal</h4>
          <p>Güncel kaynaklar ve interaktif dijital içeriklerle desteklenmiş dersler.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ============== İLETİŞİM ============== -->
  <section class="cpk-section cpk-section-alt" id="iletisim">
    <div class="container cpk-section-inner">
      <span class="cpk-eyebrow">İletişim</span>
      <h2 class="cpk-h2">Bize ulaşın</h2>

      <div class="cpk-contact">
        <div class="cpk-contact-item">
          <span class="cpk-contact-label">Adres</span>
          <p>Yıldırım Mahallesi, Bosna Sokak No: 29/A<br>İstanbul</p>
        </div>
        <div class="cpk-contact-item">
          <span class="cpk-contact-label">Telefon</span>
          <p><a href="tel:+905421808402">0542 180 84 02</a></p>
        </div>
        <div class="cpk-contact-item">
          <span class="cpk-contact-label">E-posta</span>
          <p>
            <a href="mailto:cpeakenglish@gmail.com">cpeakenglish@gmail.com</a>
          </p>
        </div>
        <div class="cpk-contact-item">
          <span class="cpk-contact-label">Sosyal Medya</span>
          <p>
            <a href="https://www.instagram.com/c_peak_english" target="_blank" rel="noopener">Instagram</a><br>
            <a href="https://www.youtube.com/@c-peak-english" target="_blank" rel="noopener">YouTube</a>
          </p>
        </div>
      </div>
    </div>
  </section>

</main>

<footer class="cpk-footer">
  <div class="container cpk-footer-inner">
    <span>© 2026 C-Peak English. Tüm hakları saklıdır.</span>
    <span class="cpk-footer-links">
      <a href="/kvkk">KVKK</a>
      <a href="{{ url_for('login') }}">Giriş Yap</a>
    </span>
  </div>
</footer>

{% endblock %}
'''

INDEX_CSS = '''/* =========================================================
   C-PEAK ENGLISH — Landing Page
   Mevcut kömür + bakır temasıyla uyumlu
   ========================================================= */

.cpk-page {
  background: var(--bg);
  color: var(--ink);
}

/* ---------- HEADER ---------- */
.cpk-header {
  position: sticky;
  top: 0;
  z-index: 90;
  background: rgba(250, 250, 249, .92);
  backdrop-filter: saturate(160%) blur(12px);
  -webkit-backdrop-filter: saturate(160%) blur(12px);
  border-bottom: 1px solid var(--border);
}
html[data-theme="dark"] .cpk-header,
html.dark .cpk-header {
  background: rgba(24, 24, 27, .88);
  border-bottom-color: rgba(255, 255, 255, .08);
}
.cpk-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.cpk-nav {
  display: flex;
  align-items: center;
  gap: 28px;
}
.cpk-nav a {
  color: var(--ink);
  text-decoration: none;
  font-size: .92rem;
  font-weight: 500;
  opacity: .78;
  transition: opacity .15s, color .15s;
}
.cpk-nav a:hover {
  opacity: 1;
  color: var(--copper);
}
.cpk-nav-cta {
  width: auto !important;
  padding: 9px 18px !important;
  font-size: .88rem !important;
  border-radius: 8px !important;
}

/* ---------- HERO ---------- */
.cpk-hero {
  position: relative;
  overflow: hidden;
  padding: 90px 28px 100px;
  background:
    radial-gradient(circle at 20% 25%, rgba(180, 83, 9, .28), transparent 45%),
    radial-gradient(circle at 85% 85%, rgba(180, 83, 9, .18), transparent 50%),
    linear-gradient(140deg, #18181b 0%, #1f1f22 55%, #0f0f10 100%);
  color: #fff;
}
.cpk-hero::before {
  content: "";
  position: absolute;
  right: -12%;
  bottom: -18%;
  width: 70%;
  aspect-ratio: 1 / 1;
  background: url("logochrome.png") center/contain no-repeat;
  opacity: .05;
  filter: blur(2px) saturate(1.3);
  transform: rotate(-9deg);
  pointer-events: none;
}
.cpk-hero-inner {
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}

/* Hero marka bloğu — login ile aynı görünüm */
.cpk-hero .hero-brand {
  margin: 0 auto 40px;
  justify-content: center;
}
.cpk-hero .hero-brand-title {
  color: #fff;
}
.cpk-hero .hero-brand-sub {
  color: var(--copper);
}

.cpk-hero-title {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 500;
  font-size: clamp(2rem, 4.5vw, 3.5rem);
  line-height: 1.1;
  letter-spacing: -.025em;
  margin: 0 0 22px;
  color: #fff;
}
.cpk-copper {
  color: #e4a15d;
}

.cpk-hero-lead {
  font-size: clamp(.98rem, 1.4vw, 1.1rem);
  color: rgba(255,255,255,.78);
  max-width: 620px;
  margin: 0 auto 30px;
  line-height: 1.6;
}

.cpk-hero-list {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  margin: 0 0 36px;
  padding: 0;
  text-align: left;
}

.cpk-hero-cta {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 48px;
}
.cpk-btn-lg {
  width: auto !important;
  padding: 13px 26px !important;
  font-size: .95rem !important;
  border-radius: 10px !important;
}
.cpk-btn-ghost-light {
  background: transparent !important;
  color: #fff !important;
  border-color: rgba(255,255,255,.25) !important;
}
.cpk-btn-ghost-light:hover {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.45) !important;
}

.cpk-hero-stats {
  max-width: 620px;
  margin: 0 auto !important;
  justify-content: center;
  border-top: 1px solid rgba(255,255,255,.10) !important;
  padding-top: 30px !important;
}
.cpk-hero-stats .hero-stat {
  align-items: center;
  text-align: center;
}
.cpk-hero-stats .hero-stat strong {
  color: #e4a15d;
}
.cpk-hero-stats .hero-stat span {
  color: rgba(255,255,255,.65);
  font-size: .84rem;
}

/* ---------- GENEL BÖLÜM ---------- */
.cpk-section {
  padding: 90px 0;
}
.cpk-section-alt {
  background: var(--surface-2);
}
html[data-theme="dark"] .cpk-section-alt,
html.dark .cpk-section-alt {
  background: rgba(255,255,255,.03);
}
.cpk-section-inner {
  max-width: 1100px;
  margin: 0 auto;
  text-align: center;
}
.cpk-eyebrow {
  display: inline-block;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: var(--copper);
  margin-bottom: 16px;
}
.cpk-h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 500;
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  line-height: 1.2;
  letter-spacing: -.02em;
  margin: 0 0 20px;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-h2,
html.dark .cpk-h2 {
  color: #fafafa;
}
.cpk-h2 em {
  font-style: italic;
  color: var(--copper);
}
.cpk-lead {
  max-width: 720px;
  margin: 0 auto;
  font-size: 1.02rem;
  line-height: 1.7;
  color: var(--muted);
}
html[data-theme="dark"] .cpk-lead,
html.dark .cpk-lead {
  color: var(--muted-2);
}

/* ---------- KURS KARTLARI ---------- */
.cpk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 22px;
  margin-top: 48px;
  text-align: left;
}
.cpk-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 28px 24px;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
html[data-theme="dark"] .cpk-card,
html.dark .cpk-card {
  background: #1c1c1f;
  border-color: rgba(255,255,255,.08);
}
.cpk-card:hover {
  transform: translateY(-3px);
  border-color: var(--copper);
  box-shadow: 0 14px 32px rgba(180,83,9,.10);
}
.cpk-card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--copper-bg);
  color: var(--copper-2);
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 600;
  font-size: 1.05rem;
  margin-bottom: 16px;
}
html[data-theme="dark"] .cpk-card-icon,
html.dark .cpk-card-icon {
  background: rgba(180,83,9,.20);
  color: #e4a15d;
}
.cpk-card h3 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: -.01em;
  margin: 0 0 10px;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-card h3,
html.dark .cpk-card h3 {
  color: #fafafa;
}
.cpk-card p {
  margin: 0;
  font-size: .93rem;
  line-height: 1.6;
  color: var(--muted);
}
html[data-theme="dark"] .cpk-card p,
html.dark .cpk-card p {
  color: var(--muted-2);
}

/* ---------- ÖZELLİKLER ---------- */
.cpk-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 32px 40px;
  margin-top: 52px;
  text-align: left;
}
.cpk-feature-num {
  display: inline-block;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.8rem;
  font-weight: 500;
  color: var(--copper);
  line-height: 1;
  margin-bottom: 14px;
}
.cpk-feature h4 {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: -.005em;
  margin: 0 0 8px;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-feature h4,
html.dark .cpk-feature h4 {
  color: #fafafa;
}
.cpk-feature p {
  margin: 0;
  font-size: .9rem;
  line-height: 1.6;
  color: var(--muted);
}
html[data-theme="dark"] .cpk-feature p,
html.dark .cpk-feature p {
  color: var(--muted-2);
}

/* ---------- İLETİŞİM ---------- */
.cpk-contact {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  margin-top: 48px;
  text-align: left;
}
.cpk-contact-label {
  display: block;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--copper);
  margin-bottom: 10px;
}
.cpk-contact-item p {
  margin: 0;
  font-size: .96rem;
  line-height: 1.65;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-contact-item p,
html.dark .cpk-contact-item p {
  color: #e4e4e7;
}
.cpk-contact-item a {
  color: var(--ink);
  text-decoration: none;
  border-bottom: 1px solid var(--border);
  transition: color .15s, border-color .15s;
}
html[data-theme="dark"] .cpk-contact-item a,
html.dark .cpk-contact-item a {
  color: #e4e4e7;
  border-bottom-color: rgba(255,255,255,.15);
}
.cpk-contact-item a:hover {
  color: var(--copper);
  border-bottom-color: var(--copper);
}

/* ---------- FOOTER ---------- */
.cpk-footer {
  border-top: 1px solid var(--border);
  background: var(--surface);
}
html[data-theme="dark"] .cpk-footer,
html.dark .cpk-footer {
  background: #0f0f10;
  border-top-color: rgba(255,255,255,.08);
}
.cpk-footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  font-size: .88rem;
  color: var(--muted);
}
.cpk-footer-links {
  display: flex;
  gap: 22px;
}
.cpk-footer-links a {
  color: var(--muted);
  text-decoration: none;
  transition: color .15s;
}
.cpk-footer-links a:hover {
  color: var(--copper);
}

/* ---------- MOBILE ---------- */
@media (max-width: 768px) {
  .cpk-header-inner {
    padding: 12px 18px;
    gap: 12px;
  }
  .cpk-nav {
    gap: 14px;
  }
  .cpk-nav a:not(.cpk-nav-cta) {
    display: none;
  }
  .cpk-nav-cta {
    padding: 8px 14px !important;
    font-size: .84rem !important;
  }

  .cpk-hero {
    padding: 60px 18px 70px;
  }
  .cpk-hero .hero-brand {
    margin-bottom: 28px;
  }
  .cpk-hero .hero-brand-mark img {
    height: clamp(64px, 18vw, 88px) !important;
  }
  .cpk-hero .hero-brand-title {
    font-size: clamp(1.5rem, 6vw, 2rem) !important;
  }
  .cpk-hero-title {
    font-size: clamp(1.6rem, 8vw, 2.2rem);
  }
  .cpk-hero-lead {
    font-size: .95rem;
  }
  .cpk-hero-cta {
    flex-direction: column;
    align-items: stretch;
  }
  .cpk-hero-cta .cpk-btn-lg {
    width: 100% !important;
    text-align: center;
    justify-content: center;
  }
  .cpk-hero-stats {
    gap: 20px !important;
  }
  .cpk-hero-stats .hero-stat strong {
    font-size: 1.4rem;
  }

  .cpk-section {
    padding: 60px 0;
  }
  .cpk-grid,
  .cpk-features,
  .cpk-contact {
    margin-top: 32px;
    gap: 18px;
  }
  .cpk-contact {
    gap: 24px;
  }
  .cpk-footer-inner {
    flex-direction: column;
    text-align: center;
    padding: 24px 18px;
  }
}
'''

def yaz(path, icerik):
    """Dosyayı UTF-8 olarak yazar. Varsa farklı ise yedek alıp üzerine yazar."""
    if os.path.exists(path):
        mevcut = open(path, encoding="utf-8").read()
        if mevcut.strip() == icerik.strip():
            print(f"= {path} (zaten aynı, atlandı)")
            return False
        bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(path, bak)
        print(f"  yedek: {bak}")
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)
    print(f"+ {path} yazıldı")
    return True

def git(cmd, check=False):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()
    except FileNotFoundError:
        return False, "", "git bulunamadı"
    except subprocess.CalledProcessError as e:
        return False, (e.stdout or "").strip(), (e.stderr or "").strip()

def main():
    print("== C-Peak English Landing v2 (tema uyumlu) ==\n")

    if not os.path.isfile("app.py"):
        print("HATA: app.py bulunamadı. Betiği cpeak klasöründe çalıştırın.")
        sys.exit(1)

    degisiklikler = []

    if yaz("templates/index.html", INDEX_HTML):
        degisiklikler.append("templates/index.html")
    if yaz("static/index.css", INDEX_CSS):
        degisiklikler.append("static/index.css")

    # Eski base_public.html varsa temizle (artık kullanılmıyor)
    eski = "templates/base_public.html"
    if os.path.exists(eski):
        bak = eski + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(eski, bak)
        os.remove(eski)
        print(f"- {eski} kaldırıldı (yedek: {bak})")
        try:
            subprocess.run(["git", "rm", "--cached", eski], capture_output=True)
        except Exception:
            pass
        degisiklikler.append(eski)

    if not degisiklikler:
        print("\nDeğişiklik yok. Push yapılmadı.")
        return

    print("\n-- git işlemleri --")
    dosyalar = [d for d in degisiklikler if os.path.exists(d)]
    git(["git", "add"] + dosyalar)
    if "templates/base_public.html" in degisiklikler and not os.path.exists("templates/base_public.html"):
        git(["git", "add", "-A", "templates/"])

    ok, out, err = git(["git", "commit", "-m",
                        "feat(landing): tema uyumlu ana sayfa — kömür+bakır paleti, doğru Türkçe, mobil uyumlu"])
    if ok:
        print("commit OK")
    else:
        if "nothing to commit" in (out + err).lower():
            print("commit edilecek şey yok")
        else:
            print(f"commit HATA: {err}")

    ok, br, _ = git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    br = br or "main"
    ok, _, err = git(["git", "push", "origin", br])
    print(f"push: {'OK (origin/' + br + ')' if ok else 'HATA: ' + err}")

    print("\n== BİTTİ ==")
    print("Render'da deploy bitince test et:")
    print("  https://www.cpeakenglish.com/")
    print("  https://www.cpeakenglish.com/giris")

if __name__ == "__main__":
    main()