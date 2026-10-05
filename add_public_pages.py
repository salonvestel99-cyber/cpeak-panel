# -*- coding: utf-8 -*-
"""
C-Peak English — Public sayfalar (hakkimizda, kurslar, iletisim)
- 3 yeni template olusturur
- Flask route'lari ekler
- Sitemap'i gunceller
- Ana sayfa menusunu gercek linklere cevirir
- Yedek alir, git commit + push
"""
import os, re, shutil, subprocess, sys
from datetime import datetime

# ============ ORTAK HEADER / FOOTER (index.html ile ayni) ============
NAV = '''<header class="cpk-header">
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
</header>'''

FOOTER = '''<footer class="cpk-footer">
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
</footer>'''

# ============ HAKKIMIZDA ============
HAKKIMIZDA_HTML = '''{% extends "base.html" %}

{% block title %}Hakkımızda — C-Peak English | İstanbul İngilizce Kursu{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block head %}
<meta name="description" content="C-Peak English hakkında: İstanbul Yıldırım'da küçük sınıflar, deneyimli öğretmenler ve dijital takip sistemiyle İngilizce eğitimi veren modern bir eğitim merkezi.">
<link rel="canonical" href="https://www.cpeakenglish.com/hakkimizda">
<meta property="og:type" content="website">
<meta property="og:title" content="Hakkımızda — C-Peak English">
<meta property="og:description" content="İstanbul Yıldırım'da küçük sınıflar ve modern yöntemlerle İngilizce eğitimi.">
<meta property="og:url" content="https://www.cpeakenglish.com/hakkimizda">
<meta property="og:image" content="https://www.cpeakenglish.com/static/logochrome.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Hakkımızda — C-Peak English">
<meta name="twitter:description" content="İstanbul Yıldırım'da küçük sınıflar ve modern yöntemlerle İngilizce eğitimi.">
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=20261003c">
{% endblock %}

{% block body %}
''' + NAV + '''

<main class="cpk-main">

  <section class="cpk-page-hero">
    <div class="container">
      <span class="cpk-eyebrow">Hakkımızda</span>
      <h1 class="cpk-h1">İngilizceyi <em>zirveye taşıyan</em> bir yaklaşım</h1>
      <p class="cpk-lead">
        C-Peak English, İngilizce öğrenmeyi kolaylaştıran ve takip edilebilir kılan modern bir
        eğitim merkezidir. Öğrenci, veli ve öğretmen üçgeninde şeffaf bir iletişim kurarak her
        öğrencinin potansiyelini en üst seviyeye çıkarmayı hedefliyoruz.
      </p>
    </div>
  </section>

  <section class="cpk-section">
    <div class="container cpk-prose">
      <h2>Hikayemiz</h2>
      <p>
        C-Peak English, İstanbul Yıldırım'da İngilizce eğitimine yeni bir soluk getirmek amacıyla
        kuruldu. Klasik dershane yaklaşımının aksine, küçük sınıflarda birebir ilgiye odaklanıyor;
        her öğrencimizin seviyesine ve hedefine uygun programlar hazırlıyoruz.
      </p>
      <p>
        Amacımız sadece sınavlara hazırlamak değil; öğrencilerimizin İngilizceyi günlük hayatta
        güvenle kullanabilen, düşünen ve üreten bireyler olmalarını sağlamak. Bu yüzden derslerimizi
        konuşma odaklı, interaktif ve güncel materyallerle destekliyoruz.
      </p>

      <h2>Misyonumuz</h2>
      <p>
        Her yaştan ve seviyeden öğrenciye nitelikli İngilizce eğitimini erişilebilir kılmak; veli
        ve öğretmenlerin öğrenci gelişimini şeffaf bir şekilde takip edebildiği bir sistem sunmak.
      </p>

      <h2>Vizyonumuz</h2>
      <p>
        Bölgenin en güvenilir ve tercih edilen İngilizce eğitim merkezi olmak; mezunlarımızın
        İngilizceyi hayatlarının her alanında özgüvenle kullanmalarını sağlamak.
      </p>

      <h2>Değerlerimiz</h2>
      <ul class="cpk-values">
        <li><strong>Kalite:</strong> Her dersimiz deneyimli ve sertifikalı öğretmenler tarafından hazırlanır.</li>
        <li><strong>Şeffaflık:</strong> Veli ve öğrencilerimiz gelişimi online panelden takip edebilir.</li>
        <li><strong>Süreklilik:</strong> Öğrencilerimizin motivasyonunu canlı tutar, hedeflerine ulaşana kadar yanlarında oluruz.</li>
        <li><strong>İnsan Odaklılık:</strong> Her öğrenci farklıdır. Programlarımızı kişiye özel şekillendiririz.</li>
      </ul>

      <h2>Neden C-Peak English?</h2>
      <p>
        Küçük sınıflarımız sayesinde her öğrenciye yeterli zaman ayırıyor, dijital panelimizle
        velilerin çocuklarının gelişimini anlık takip etmesini sağlıyoruz. Ders programı, ödevler,
        bildirimler — hepsi tek bir panelde. Bu şeffaflık öğrenci ve veli arasında güveni
        güçlendiriyor.
      </p>

      <div class="cpk-inline-cta">
        <a href="/kurslar" class="btn-primary btn-copper">Kurslarımızı İnceleyin</a>
        <a href="/iletisim" class="btn-ghost">Bize Ulaşın</a>
      </div>
    </div>
  </section>

</main>

''' + FOOTER + '''
{% endblock %}
'''

# ============ KURSLAR ============
KURSLAR_HTML = '''{% extends "base.html" %}

{% block title %}Kurslar — C-Peak English | İngilizce Eğitim Programları{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block head %}
<meta name="description" content="C-Peak English kursları: Genel İngilizce, YDS / YDT / TOEFL / IELTS sınav hazırlık, konuşma kulübü. Küçük sınıflar ve kişiye özel programlarla İstanbul Yıldırım'da.">
<link rel="canonical" href="https://www.cpeakenglish.com/kurslar">
<meta property="og:type" content="website">
<meta property="og:title" content="Kurslar — C-Peak English">
<meta property="og:description" content="Genel İngilizce, sınav hazırlık ve konuşma kulübü programları.">
<meta property="og:url" content="https://www.cpeakenglish.com/kurslar">
<meta property="og:image" content="https://www.cpeakenglish.com/static/logochrome.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Kurslar — C-Peak English">
<meta name="twitter:description" content="Genel İngilizce, sınav hazırlık ve konuşma kulübü programları.">
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=20261003c">
{% endblock %}

{% block body %}
''' + NAV + '''

<main class="cpk-main">

  <section class="cpk-page-hero">
    <div class="container">
      <span class="cpk-eyebrow">Kurslarımız</span>
      <h1 class="cpk-h1">Her seviyeye ve <em>hedefe</em> uygun programlar</h1>
      <p class="cpk-lead">
        İngilizce öğrenme yolculuğunuzda nerede olursanız olun, size uygun bir kursumuz var.
        Programlarımız öğrencilerimizin seviyesine ve hedeflerine göre kişiselleştirilir.
      </p>
    </div>
  </section>

  <section class="cpk-section">
    <div class="container">
      <div class="cpk-course-list">

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">A</div>
            <h2>Genel İngilizce</h2>
          </div>
          <p class="cpk-course-desc">
            Temel seviyeden ileri seviyeye (A1–C2) kadar konuşma, dinleme, okuma ve yazma
            becerilerinin dengeli gelişimini hedefleyen programımız.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Seviyeler:</strong> A1, A2, B1, B2, C1, C2</li>
            <li><strong>Süre:</strong> Seviye başına 12 hafta</li>
            <li><strong>Ders saati:</strong> Haftada 4 saat, küçük gruplar</li>
            <li><strong>Materyal:</strong> Cambridge & Oxford kaynakları</li>
          </ul>
        </article>

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">B</div>
            <h2>Sınav Hazırlık</h2>
          </div>
          <p class="cpk-course-desc">
            YDS, YDT, TOEFL ve IELTS gibi ulusal ve uluslararası sınavlara yönelik yoğun ve
            stratejik hazırlık programı.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Sınavlar:</strong> YDS, YDT, TOEFL, IELTS</li>
            <li><strong>Yaklaşım:</strong> Deneme ağırlıklı + strateji dersleri</li>
            <li><strong>Materyal:</strong> Güncel sınav formatına uygun kaynaklar</li>
            <li><strong>Değerlendirme:</strong> Haftalık denemeler ve birebir geri bildirim</li>
          </ul>
        </article>

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">C</div>
            <h2>Konuşma Kulübü</h2>
          </div>
          <p class="cpk-course-desc">
            İngilizceyi akıcı ve özgüvenli konuşabilmek için gerçek hayat senaryolarıyla pratik
            yapılan interaktif kulüp programı.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Odak:</strong> Günlük konuşma ve telaffuz</li>
            <li><strong>Format:</strong> Küçük gruplar, aktif katılım</li>
            <li><strong>Konular:</strong> Günlük yaşam, iş, seyahat, kültür</li>
            <li><strong>Kazanım:</strong> Akıcılık ve doğal ifade becerisi</li>
          </ul>
        </article>

        <article class="cpk-course">
          <div class="cpk-course-head">
            <div class="cpk-card-icon">D</div>
            <h2>Online Takip Paneli</h2>
          </div>
          <p class="cpk-course-desc">
            Tüm kurslarımıza dahil olan dijital takip sistemi ile öğrenci, veli ve öğretmen aynı
            platformda buluşur.
          </p>
          <ul class="cpk-course-meta">
            <li><strong>Ders programı:</strong> Anlık güncel</li>
            <li><strong>Ödevler:</strong> Öğretmen tarafından atanır, dijital takip edilir</li>
            <li><strong>Bildirimler:</strong> Önemli duyurular otomatik iletilir</li>
            <li><strong>Veli erişimi:</strong> Gelişim şeffaf şekilde takip edilir</li>
          </ul>
        </article>

      </div>
    </div>
  </section>

  <section class="cpk-section cpk-section-alt">
    <div class="container cpk-section-inner">
      <span class="cpk-eyebrow">Kayıt &amp; Bilgi</span>
      <h2 class="cpk-h2">Hangi kurs size uygun, birlikte <em>belirleyelim</em></h2>
      <p class="cpk-lead">
        Seviye tespit sınavımızla başlayalım, hedeflerinizi konuşalım ve size en uygun programı
        birlikte planlayalım. Kayıt ve ücret bilgisi için bize ulaşın.
      </p>
      <div class="cpk-inline-cta">
        <a href="/iletisim" class="btn-primary btn-copper">Bize Ulaşın</a>
        <a href="tel:+905421808402" class="btn-ghost">0542 180 84 02</a>
      </div>
    </div>
  </section>

</main>

''' + FOOTER + '''
{% endblock %}
'''

# ============ ILETISIM ============
ILETISIM_HTML = '''{% extends "base.html" %}

{% block title %}İletişim — C-Peak English | İstanbul İngilizce Kursu{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block head %}
<meta name="description" content="C-Peak English iletişim bilgileri: Yıldırım Mahallesi, Bosna Sokak No: 29/A, İstanbul. Telefon 0542 180 84 02. E-posta cpeakenglish@gmail.com.">
<link rel="canonical" href="https://www.cpeakenglish.com/iletisim">
<meta property="og:type" content="website">
<meta property="og:title" content="İletişim — C-Peak English">
<meta property="og:description" content="İstanbul Yıldırım'da İngilizce kursu. Adres, telefon ve sosyal medya bilgileri.">
<meta property="og:url" content="https://www.cpeakenglish.com/iletisim">
<meta property="og:image" content="https://www.cpeakenglish.com/static/logochrome.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="İletişim — C-Peak English">
<meta name="twitter:description" content="İstanbul Yıldırım'da İngilizce kursu. Adres, telefon ve sosyal medya bilgileri.">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "C-Peak English",
  "url": "https://www.cpeakenglish.com",
  "logo": "https://www.cpeakenglish.com/static/logochrome.png",
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

<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=20261003c">
{% endblock %}

{% block body %}
''' + NAV + '''

<main class="cpk-main">

  <section class="cpk-page-hero">
    <div class="container">
      <span class="cpk-eyebrow">İletişim</span>
      <h1 class="cpk-h1">Bize <em>ulaşın</em></h1>
      <p class="cpk-lead">
        Sorularınız, kayıt ve seviye tespit sınavı için bize telefon, e-posta veya sosyal medya
        üzerinden ulaşabilirsiniz. En kısa sürede size dönüş yapıyoruz.
      </p>
    </div>
  </section>

  <section class="cpk-section">
    <div class="container">
      <div class="cpk-contact-grid">

        <div class="cpk-contact-block">
          <h3>Adres</h3>
          <p>
            Yıldırım Mahallesi<br>
            Bosna Sokak No: 29/A<br>
            İstanbul
          </p>
        </div>

        <div class="cpk-contact-block">
          <h3>Telefon</h3>
          <p>
            <a href="tel:+905421808402">0542 180 84 02</a>
          </p>
        </div>

        <div class="cpk-contact-block">
          <h3>E-posta</h3>
          <p>
            <a href="mailto:cpeakenglish@gmail.com">cpeakenglish@gmail.com</a>
          </p>
        </div>

        <div class="cpk-contact-block">
          <h3>Sosyal Medya</h3>
          <p>
            <a href="https://www.instagram.com/c_peak_english" target="_blank" rel="noopener">Instagram</a><br>
            <a href="https://www.youtube.com/@c-peak-english" target="_blank" rel="noopener">YouTube</a>
          </p>
        </div>

      </div>

      <div class="cpk-map-wrap">
        <iframe
          src="https://www.google.com/maps?q=Y%C4%B1ld%C4%B1r%C4%B1m+Mahallesi+Bosna+Sokak+No:29%2FA+%C4%B0stanbul&output=embed"
          width="100%" height="380" style="border:0;border-radius:14px;"
          allowfullscreen="" loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          title="C-Peak English Konum"></iframe>
      </div>

      <div class="cpk-inline-cta" style="margin-top:40px;">
        <a href="/kurslar" class="btn-primary btn-copper">Kurslarımızı İnceleyin</a>
        <a href="/hakkimizda" class="btn-ghost">Hakkımızda</a>
      </div>
    </div>
  </section>

</main>

''' + FOOTER + '''
{% endblock %}
'''

# ============ EK CSS ============
EK_CSS = '''

/* =========================================================
   ALT SAYFALAR (hakkimizda, kurslar, iletisim)
   ========================================================= */

.cpk-page-hero {
  padding: 70px 0 50px;
  text-align: center;
  background:
    radial-gradient(circle at 50% 0%, rgba(180,83,9,.10), transparent 60%),
    var(--bg);
}
html[data-theme="dark"] .cpk-page-hero,
html.dark .cpk-page-hero {
  background:
    radial-gradient(circle at 50% 0%, rgba(180,83,9,.16), transparent 60%),
    #0f0f10;
}
.cpk-h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 500;
  font-size: clamp(1.8rem, 3.6vw, 2.8rem);
  line-height: 1.15;
  letter-spacing: -.02em;
  margin: 0 0 20px;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-h1,
html.dark .cpk-h1 {
  color: #fafafa;
}
.cpk-h1 em {
  font-style: italic;
  color: var(--copper);
}

.cpk-prose {
  max-width: 760px;
  margin: 0 auto;
  text-align: left;
}
.cpk-prose h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 500;
  font-size: 1.55rem;
  margin: 42px 0 14px;
  letter-spacing: -.015em;
  color: var(--ink);
}
.cpk-prose h2:first-child { margin-top: 0; }
html[data-theme="dark"] .cpk-prose h2,
html.dark .cpk-prose h2 { color: #fafafa; }
.cpk-prose p {
  font-size: 1rem;
  line-height: 1.75;
  color: var(--muted);
  margin: 0 0 16px;
}
html[data-theme="dark"] .cpk-prose p,
html.dark .cpk-prose p { color: var(--muted-2); }

.cpk-values {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.cpk-values li {
  padding-left: 22px;
  position: relative;
  font-size: .98rem;
  line-height: 1.7;
  color: var(--muted);
}
html[data-theme="dark"] .cpk-values li,
html.dark .cpk-values li { color: var(--muted-2); }
.cpk-values li::before {
  content: "★";
  position: absolute;
  left: 0;
  color: var(--copper);
  font-size: .9rem;
}
.cpk-values strong { color: var(--ink); }
html[data-theme="dark"] .cpk-values strong,
html.dark .cpk-values strong { color: #fafafa; }

.cpk-inline-cta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 36px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}
html[data-theme="dark"] .cpk-inline-cta,
html.dark .cpk-inline-cta { border-top-color: rgba(255,255,255,.08); }
.cpk-inline-cta .btn-primary,
.cpk-inline-cta .btn-ghost {
  width: auto !important;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  padding: 11px 22px;
  font-size: .92rem;
}

/* ============= KURSLAR ============= */
.cpk-course-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 820px;
  margin: 0 auto;
}
.cpk-course {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 30px 28px;
  transition: box-shadow .18s, border-color .18s;
}
html[data-theme="dark"] .cpk-course,
html.dark .cpk-course {
  background: #1c1c1f;
  border-color: rgba(255,255,255,.08);
}
.cpk-course:hover {
  border-color: var(--copper);
  box-shadow: 0 14px 32px rgba(180,83,9,.08);
}
.cpk-course-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}
.cpk-course-head h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 600;
  font-size: 1.35rem;
  margin: 0;
  letter-spacing: -.01em;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-course-head h2,
html.dark .cpk-course-head h2 { color: #fafafa; }
.cpk-course-desc {
  font-size: .98rem;
  line-height: 1.7;
  color: var(--muted);
  margin: 0 0 18px;
}
html[data-theme="dark"] .cpk-course-desc,
html.dark .cpk-course-desc { color: var(--muted-2); }
.cpk-course-meta {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px 22px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}
html[data-theme="dark"] .cpk-course-meta,
html.dark .cpk-course-meta { border-top-color: rgba(255,255,255,.08); }
.cpk-course-meta li {
  font-size: .88rem;
  line-height: 1.55;
  color: var(--muted);
}
html[data-theme="dark"] .cpk-course-meta li,
html.dark .cpk-course-meta li { color: var(--muted-2); }
.cpk-course-meta strong {
  color: var(--ink);
  font-weight: 600;
  margin-right: 4px;
}
html[data-theme="dark"] .cpk-course-meta strong,
html.dark .cpk-course-meta strong { color: #e4e4e7; }

/* ============= ILETISIM ============= */
.cpk-contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 26px;
  max-width: 960px;
  margin: 0 auto 42px;
}
.cpk-contact-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 26px 22px;
}
html[data-theme="dark"] .cpk-contact-block,
html.dark .cpk-contact-block {
  background: #1c1c1f;
  border-color: rgba(255,255,255,.08);
}
.cpk-contact-block h3 {
  font-family: 'Inter', sans-serif;
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--copper);
  margin: 0 0 12px;
}
.cpk-contact-block p {
  margin: 0;
  font-size: .98rem;
  line-height: 1.65;
  color: var(--ink);
}
html[data-theme="dark"] .cpk-contact-block p,
html.dark .cpk-contact-block p { color: #e4e4e7; }
.cpk-contact-block a {
  color: inherit;
  text-decoration: none;
  border-bottom: 1px solid var(--border);
  transition: color .15s, border-color .15s;
}
html[data-theme="dark"] .cpk-contact-block a,
html.dark .cpk-contact-block a { border-bottom-color: rgba(255,255,255,.15); }
.cpk-contact-block a:hover {
  color: var(--copper);
  border-bottom-color: var(--copper);
}
.cpk-map-wrap {
  max-width: 960px;
  margin: 0 auto;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--border);
}
html[data-theme="dark"] .cpk-map-wrap,
html.dark .cpk-map-wrap { border-color: rgba(255,255,255,.08); }

@media (max-width: 768px) {
  .cpk-page-hero { padding: 50px 0 30px; }
  .cpk-prose h2 { font-size: 1.3rem; margin-top: 32px; }
  .cpk-course { padding: 22px 20px; }
  .cpk-course-head h2 { font-size: 1.15rem; }
  .cpk-inline-cta {
    flex-direction: column;
    align-items: stretch;
  }
  .cpk-inline-cta .btn-primary,
  .cpk-inline-cta .btn-ghost {
    width: 100% !important;
    justify-content: center;
  }
}
'''

# ============ ROUTE KODLARI ============
ROUTES_CODE = '''

# ============================================
# SEO: Public sayfalar (add_public_pages.py)
# ============================================
@app.route('/hakkimizda')
def hakkimizda():
    return render_template('hakkimizda.html')


@app.route('/kurslar')
def kurslar():
    return render_template('kurslar.html')


@app.route('/iletisim')
def iletisim():
    return render_template('iletisim.html')
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
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)
    print(f"+ {path} yazildi")
    return True

def git(cmd, check=False):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return r.returncode == 0, (r.stdout or "").strip(), (r.stderr or "").strip()
    except FileNotFoundError:
        return False, "", "git yok"
    except subprocess.CalledProcessError as e:
        return False, (e.stdout or "").strip(), (e.stderr or "").strip()

def app_py_guncelle():
    """app.py'ye route'lari ekler + sitemap'i gunceller."""
    path = "app.py"
    c = open(path, encoding="utf-8").read()
    orig = c
    degisti = False

    # 1) Route'lari ekle
    if '@app.route(\'/hakkimizda\')' not in c:
        yedek(path)
        # sitemap_xml fonksiyonundan hemen sonra ekle
        marker = "    return Response(xml, mimetype='application/xml')"
        idx = c.find(marker)
        if idx == -1:
            # yedek olarak dosyanin sonuna ekle
            c = c.rstrip() + "\n" + ROUTES_CODE + "\n"
        else:
            ins = idx + len(marker)
            c = c[:ins] + ROUTES_CODE + c[ins:]
        print("+ app.py: 3 yeni route eklendi")
        degisti = True

    # 2) Sitemap pages listesini guncelle
    yeni_pages = (
        '    pages = [\n'
        '        "https://www.cpeakenglish.com/",\n'
        '        "https://www.cpeakenglish.com/hakkimizda",\n'
        '        "https://www.cpeakenglish.com/kurslar",\n'
        '        "https://www.cpeakenglish.com/iletisim",\n'
        '        "https://www.cpeakenglish.com/kvkk",\n'
        '    ]'
    )
    pattern = re.compile(r'def sitemap_xml\(\):.*?pages\s*=\s*\[.*?\]', re.DOTALL)
    m = pattern.search(c)
    if m:
        yeni = re.sub(r'(def sitemap_xml\(\):.*?pages\s*=\s*\[).*?(\])',
                      lambda mm: yeni_pages, c, count=1, flags=re.DOTALL)
        if yeni != c:
            c = yeni
            print("+ app.py: sitemap pages listesi guncellendi (5 sayfa)")
            degisti = True
    else:
        print("! app.py: sitemap_xml fonksiyonu bulunamadi")

    if degisti and c != orig:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(c)
    return degisti

def index_html_nav_guncelle():
    """index.html menusundeki #hakkimizda, #kurslar, #iletisim linklerini gercek URL'lere cevirir."""
    path = "templates/index.html"
    if not os.path.isfile(path):
        return False
    c = open(path, encoding="utf-8").read()
    orig = c

    # Menüdeki anchor linkler
    c = c.replace('<a href="#hakkimizda">Hakkımızda</a>', '<a href="/hakkimizda">Hakkımızda</a>')
    c = c.replace('<a href="#kurslar">Kurslar</a>', '<a href="/kurslar">Kurslar</a>')
    c = c.replace('<a href="#iletisim">İletişim</a>', '<a href="/iletisim">İletişim</a>')

    # Bölüm sonlarındaki CTA'lar
    c = c.replace('<a href="#kurslar" class="btn-primary btn-copper cpk-btn-lg">Kursları Keşfet</a>',
                  '<a href="/kurslar" class="btn-primary btn-copper cpk-btn-lg">Kursları Keşfet</a>')
    c = c.replace('<a href="#iletisim" class="btn-ghost cpk-btn-lg cpk-btn-ghost-light">Bize Ulaş</a>',
                  '<a href="/iletisim" class="btn-ghost cpk-btn-lg cpk-btn-ghost-light">Bize Ulaş</a>')

    if c != orig:
        yedek(path)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(c)
        print("+ index.html: menu ve CTA linkleri gercek sayfalara cevrildi")
        return True
    print("= index.html: link guncellemesi gerekmiyor")
    return False

def css_ekle():
    path = "static/index.css"
    if not os.path.isfile(path):
        return False
    c = open(path, encoding="utf-8").read()
    if "ALT SAYFALAR (hakkimizda, kurslar, iletisim)" in c:
        print("= index.css: alt sayfa stilleri zaten var")
        return False
    yedek(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c.rstrip() + "\n" + EK_CSS)
    print("+ index.css: alt sayfa stilleri eklendi")
    return True

def main():
    print("== C-Peak English: Public Sayfalar ==\n")

    if not os.path.isfile("app.py"):
        print("HATA: app.py bulunamadi.")
        sys.exit(1)

    degisiklikler = []
    if yaz("templates/hakkimizda.html", HAKKIMIZDA_HTML): degisiklikler.append("templates/hakkimizda.html")
    if yaz("templates/kurslar.html", KURSLAR_HTML): degisiklikler.append("templates/kurslar.html")
    if yaz("templates/iletisim.html", ILETISIM_HTML): degisiklikler.append("templates/iletisim.html")
    if css_ekle(): degisiklikler.append("static/index.css")
    if index_html_nav_guncelle(): degisiklikler.append("templates/index.html")
    if app_py_guncelle(): degisiklikler.append("app.py")

    if not degisiklikler:
        print("\nHicbir degisiklik yok.")
        return

    print("\n-- git islemleri --")
    git(["git", "add"] + degisiklikler)
    ok, out, err = git(["git", "commit", "-m",
        "feat(seo): hakkimizda, kurslar, iletisim sayfalari + sitemap guncellendi"])
    if ok:
        print("commit OK")
    else:
        if "nothing to commit" in (out + err).lower():
            print("commit edilecek sey yok")
        else:
            print(f"commit HATA: {err}")

    ok, br, _ = git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    br = br or "main"
    ok, _, err = git(["git", "push", "origin", br])
    print(f"push: {'OK (origin/' + br + ')' if ok else 'HATA: ' + err}")

    print("\n== BITTI ==")
    print("Render deploy sonrasi test et:")
    print("  https://www.cpeakenglish.com/hakkimizda")
    print("  https://www.cpeakenglish.com/kurslar")
    print("  https://www.cpeakenglish.com/iletisim")
    print("  https://www.cpeakenglish.com/sitemap.xml  (5 sayfa olmali)")

if __name__ == "__main__":
    main()