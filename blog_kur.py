#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blog_kur.py — Markdown tabanlı blog altyapısını kurar.

Oluşturur:
  - content/blog/  (yazı klasörü)
  - cpk_blog.py    (markdown yükleyici)
  - templates/blog.html       (liste sayfası)
  - templates/blog_yazi.html  (tek yazı)

Günceller:
  - app.py           → /blog ve /blog/<slug> route'ları + sitemap
  - base_seo.html    → nav menüye Blog linki (JS injector)
  - requirements.txt → Markdown kütüphanesi

Örnek yazı ekler:
  - content/blog/bayrampasa-ingilizce-kursu-nasil-secilir.md

Kullanım:
  py blog_kur.py --dry-run
  py blog_kur.py --no-git
  py blog_kur.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
CONTENT = KOK / "content" / "blog"
YED_DIR = KOK / "backups"

APP = KOK / "app.py"
BASE_SEO = KOK / "templates" / "base_seo.html"
REQ = KOK / "requirements.txt"
BLOG_MODUL = KOK / "cpk_blog.py"
TMPL_LISTE = KOK / "templates" / "blog.html"
TMPL_YAZI = KOK / "templates" / "blog_yazi.html"

MARKER = "CPK_BLOG"

COMMIT_MSG = """feat(blog): markdown tabanlı blog altyapısı

- cpk_blog.py: markdown yükleyici + frontmatter parser
- templates/blog.html + blog_yazi.html
- app.py: /blog ve /blog/<slug> route'ları
- app.py: sitemap.xml artık blog yazılarını da içeriyor
- base_seo.html: nav menüye Blog linki
- requirements.txt: Markdown>=3.5.0
- content/blog/: örnek yazı
- Otomatik yama: blog_kur.py [CPK_BLOG]"""


# ============================================================
# 1) cpk_blog.py
# ============================================================
BLOG_PY = '''# -*- coding: utf-8 -*-
"""
cpk_blog.py — Markdown blog yükleyici.

Kullanım:
    from cpk_blog import tum_yazilar, yazi_bul
    yazilar = tum_yazilar()          # liste
    yazi = yazi_bul("slug")          # tek yazı veya None
"""
import re
from pathlib import Path

try:
    import markdown as _md
    _MD_VAR = True
except ImportError:
    _MD_VAR = False

BLOG_DIR = Path(__file__).resolve().parent / "content" / "blog"


def _slugla(metin):
    """Türkçe karakterleri sadeleştirip URL-slug yapar."""
    esleme = str.maketrans({
        "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
    })
    s = metin.translate(esleme).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _frontmatter(metin):
    """---\\n...\\n---\\n gövde"""
    m = re.match(r"^---\\s*\\n(.*?)\\n---\\s*\\n?(.*)$", metin, re.DOTALL)
    if not m:
        return {}, metin
    fm, body = m.group(1), m.group(2)
    meta = {}
    for satir in fm.split("\\n"):
        satir = satir.strip()
        if not satir or ":" not in satir:
            continue
        k, _, v = satir.partition(":")
        v = v.strip().strip('"').strip("'")
        meta[k.strip()] = v
    return meta, body


def _render_md(metin):
    if not _MD_VAR:
        # Fallback: satır satır <p>
        parcalar = [p.strip() for p in metin.split("\\n\\n") if p.strip()]
        return "\\n".join(f"<p>{p}</p>" for p in parcalar)
    return _md.markdown(
        metin,
        extensions=["extra", "smarty", "sane_lists", "toc"],
    )


def _yazi_yukle(path):
    ic = path.read_text(encoding="utf-8")
    meta, body = _frontmatter(ic)
    slug = meta.get("slug") or _slugla(meta.get("title") or path.stem)
    return {
        "slug": slug,
        "title": meta.get("title") or path.stem,
        "description": meta.get("description", ""),
        "date": meta.get("date", ""),
        "keywords": meta.get("keywords", ""),
        "author": meta.get("author", "C-Peak English"),
        "html": _render_md(body),
        "md": body,
        "file": path.name,
    }


def tum_yazilar():
    if not BLOG_DIR.exists():
        return []
    yazilar = []
    for p in BLOG_DIR.glob("*.md"):
        try:
            yazilar.append(_yazi_yukle(p))
        except Exception as e:
            print(f"[cpk_blog] hata okunurken {p.name}: {e}")
    yazilar.sort(key=lambda y: y.get("date", ""), reverse=True)
    return yazilar


def yazi_bul(slug):
    for y in tum_yazilar():
        if y["slug"] == slug:
            return y
    return None
'''


# ============================================================
# 2) templates/blog.html
# ============================================================
TMPL_LISTE_HTML = '''{% extends "base_seo.html" %}

{% block title %}Blog — C-Peak English | İngilizce Öğrenme Rehberi{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block head %}
<meta name="description" content="İngilizce öğrenme, sınav hazırlığı, dil edinimi ve Bayrampaşa'da İngilizce eğitimi üzerine faydalı rehberler.">
<link rel="canonical" href="https://www.cpeakenglish.com/blog">
<meta property="og:type" content="website">
<meta property="og:title" content="Blog — C-Peak English">
<meta property="og:description" content="İngilizce öğrenme üzerine faydalı rehberler.">
<meta property="og:url" content="https://www.cpeakenglish.com/blog">
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=blog">
<style>
.cpk-blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 32px;
}
.cpk-blog-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 26px 24px 22px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.015));
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 14px 40px -20px rgba(0,0,0,.55);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
  text-decoration: none;
  color: inherit;
}
.cpk-blog-card:hover, .cpk-blog-card:focus-visible {
  transform: translateY(-3px);
  border-color: rgba(245,158,11,.45);
  box-shadow: 0 22px 60px -20px rgba(245,158,11,.28);
  outline: none;
}
.cpk-blog-date {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: #f59e0b;
}
.cpk-blog-title {
  margin: 0;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.32rem;
  font-weight: 600;
  line-height: 1.28;
  letter-spacing: -0.012em;
  color: #fff;
}
.cpk-blog-desc {
  margin: 0;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .92rem;
  line-height: 1.55;
  color: rgba(255,255,255,.72);
}
.cpk-blog-more {
  margin-top: auto;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .84rem;
  font-weight: 600;
  color: #f59e0b;
  letter-spacing: .01em;
}
.cpk-blog-empty {
  padding: 60px 20px;
  text-align: center;
  font-family: 'Inter', system-ui, sans-serif;
  color: rgba(255,255,255,.55);
}
</style>
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
      <a href="/blog">Blog</a>
      <a href="/iletisim">İletişim</a>
      <a href="{{ url_for('login') }}" class="btn-primary cpk-nav-cta">Giriş Yap</a>
    </nav>
  </div>
</header>

<main class="cpk-main">
  <section class="cpk-page-hero">
    <div class="container">
      <span class="cpk-eyebrow">Blog</span>
      <h1 class="cpk-h1">İngilizce <em>öğrenme</em> rehberi</h1>
      <p class="cpk-lead">
        Sınav hazırlığı, konuşma pratiği, çocuklara İngilizce ve daha fazlası.
        Bayrampaşa ve İstanbul'da İngilizce eğitimi üzerine pratik yazılar.
      </p>
    </div>
  </section>

  <section class="cpk-section">
    <div class="container">
      {% if yazilar %}
      <div class="cpk-blog-grid">
        {% for y in yazilar %}
        <a href="/blog/{{ y.slug }}" class="cpk-blog-card">
          {% if y.date %}
          <span class="cpk-blog-date">{{ y.date }}</span>
          {% endif %}
          <h2 class="cpk-blog-title">{{ y.title }}</h2>
          {% if y.description %}
          <p class="cpk-blog-desc">{{ y.description }}</p>
          {% endif %}
          <span class="cpk-blog-more">Devamını Oku →</span>
        </a>
        {% endfor %}
      </div>
      {% else %}
      <div class="cpk-blog-empty">Henüz yazı yok.</div>
      {% endif %}
    </div>
  </section>
</main>

<footer class="cpk-footer">
  <div class="container cpk-footer-inner">
    <span>© 2026 C-Peak English. Tüm hakları saklıdır.</span>
    <span class="cpk-footer-links">
      <a href="/hakkimizda">Hakkımızda</a>
      <a href="/kurslar">Kurslar</a>
      <a href="/blog">Blog</a>
      <a href="/iletisim">İletişim</a>
      <a href="/kvkk">KVKK</a>
      <a href="{{ url_for('login') }}">Giriş Yap</a>
    </span>
  </div>
</footer>
{% endblock %}
'''


# ============================================================
# 3) templates/blog_yazi.html
# ============================================================
TMPL_YAZI_HTML = '''{% extends "base_seo.html" %}

{% block title %}{{ yazi.title }} — C-Peak English{% endblock %}
{% block body_class %}cpk-page{% endblock %}

{% block head %}
<meta name="description" content="{{ yazi.description }}">
<link rel="canonical" href="https://www.cpeakenglish.com/blog/{{ yazi.slug }}">
<meta property="og:type" content="article">
<meta property="og:title" content="{{ yazi.title }}">
<meta property="og:description" content="{{ yazi.description }}">
<meta property="og:url" content="https://www.cpeakenglish.com/blog/{{ yazi.slug }}">
<meta property="article:published_time" content="{{ yazi.date }}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ yazi.title }}">
<meta name="twitter:description" content="{{ yazi.description }}">
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=blog">
<style>
.cpk-blog-article {
  max-width: 720px;
  margin: 0 auto;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 1.06rem;
  line-height: 1.72;
  color: rgba(255,255,255,.86);
}
.cpk-blog-article h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.8rem, 4.5vw, 2.6rem);
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.018em;
  color: #fff;
  margin: 0 0 14px;
}
.cpk-blog-article h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.28rem, 3.2vw, 1.55rem);
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.012em;
  color: #fff;
  margin: 40px 0 14px;
}
.cpk-blog-article h3 {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 28px 0 10px;
}
.cpk-blog-article p { margin: 0 0 18px; }
.cpk-blog-article a {
  color: #f59e0b;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.cpk-blog-article ul, .cpk-blog-article ol {
  margin: 0 0 20px;
  padding-left: 24px;
}
.cpk-blog-article li { margin-bottom: 8px; }
.cpk-blog-article strong { color: #fff; font-weight: 700; }
.cpk-blog-article blockquote {
  margin: 22px 0;
  padding: 4px 0 4px 20px;
  border-left: 3px solid #f59e0b;
  font-style: italic;
  color: rgba(255,255,255,.7);
}
.cpk-blog-article hr {
  border: 0;
  border-top: 1px solid rgba(255,255,255,.1);
  margin: 36px 0 22px;
}
.cpk-blog-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: .82rem;
  color: rgba(255,255,255,.5);
  margin-bottom: 28px;
}
.cpk-blog-meta-dot { width: 3px; height: 3px; border-radius: 50%; background: rgba(255,255,255,.3); }
.cpk-blog-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: .86rem;
  font-weight: 600;
  color: #f59e0b;
  text-decoration: none;
  margin-bottom: 20px;
}
.cpk-blog-back:hover { text-decoration: underline; }
</style>
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
      <a href="/blog">Blog</a>
      <a href="/iletisim">İletişim</a>
      <a href="{{ url_for('login') }}" class="btn-primary cpk-nav-cta">Giriş Yap</a>
    </nav>
  </div>
</header>

<main class="cpk-main">
  <section class="cpk-section">
    <div class="container">
      <div class="cpk-blog-article">
        <a href="/blog" class="cpk-blog-back">← Tüm Yazılar</a>
        <div class="cpk-blog-meta">
          {% if yazi.date %}<span>{{ yazi.date }}</span>{% endif %}
          {% if yazi.date %}<span class="cpk-blog-meta-dot"></span>{% endif %}
          <span>{{ yazi.author }}</span>
        </div>
        {{ yazi.html | safe }}
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
      <a href="/blog">Blog</a>
      <a href="/iletisim">İletişim</a>
      <a href="/kvkk">KVKK</a>
      <a href="{{ url_for('login') }}">Giriş Yap</a>
    </span>
  </div>
</footer>
{% endblock %}
'''


# ============================================================
# 4) Örnek yazı
# ============================================================
ORNEK_YAZI = '''---
title: "Bayrampaşa'da İngilizce Kursu Nasıl Seçilir? 7 Kritik Soru"
slug: "bayrampasa-ingilizce-kursu-nasil-secilir"
date: "2026-10-05"
description: "İngilizce kursu seçerken mutlaka sormanız gereken 7 kritik soru. Sınıf mevcudu, öğretmen kalitesi ve şeffaf sözleşme rehberi."
keywords: "bayrampaşa ingilizce kursu, ingilizce kursu seçimi, bayrampaşa dil okulu, istanbul ingilizce kursu"
author: "C-Peak English"
---

# Bayrampaşa'da İngilizce Kursu Nasıl Seçilir? 7 Kritik Soru

Bayrampaşa'da onlarca İngilizce kursu var. Hangisinin sana ya da çocuğuna gerçekten iyi geleceğini anlamak zor. Reklam afişlerinde hepsi "en iyi" görünüyor ama 3 ay sonra "keşke başka bir yere gitseydik" diyen çok veli var.

Bu yazıda, bir kursa kaydolmadan önce mutlaka sorman gereken 7 soruyu paylaşıyorum. Bu soruların cevapları, gerçekten iyi bir kursla sadece iyi pazarlama yapan bir kursu ayırt eder.

## Neden bu sorular önemli?

Çünkü İngilizce öğrenmek zaman ve para işi. Yanlış kursa 6 ay gidip hiçbir şey öğrenmemek, hem moralini bozar hem de çocuğunun İngilizceye olan ilgisini bitirir. Doğru seçim, 1 yılda 2 yıllık yol almanı sağlar.

## 1. Sınıf mevcudu kaç kişi?

Bu, sorulacak **ilk soru**. 20 kişilik sınıfta öğretmen herkesle tek tek ilgilenemez. Özellikle konuşma pratiği için her öğrenciye sıra gelmesi gerekir — 20 kişide bu mümkün değil.

İdeal sınıf mevcudu **8-12 kişi**. 12'nin üstündeyse, öğretmenin kalitesi ne olursa olsun, sıra bekleyerek geçen dersler olur.

## 2. Öğretmenler kim, sertifikaları var mı?

"5 yıllık tecrübeli öğretmen kadromuz" gibi cümleler her yerde var. Sen somut bilgi iste:

- Öğretmenin İngilizce öğretimi sertifikası var mı? (CELTA, TEFL gibi)
- Yurt dışında yaşamış mı?
- Kaç yıllık öğretmenlik tecrübesi var?

Öğretmen sık değişiyorsa, o kursta bir sorun var demektir. Öğretmenle tanışma dersi isteyebilirsin.

## 3. Seviye tespit sınavı yapılıyor mu?

Kursa kaydolmadan önce seviyeni ölçmeleri gerek. "Herkes A1'den başlar" diyen bir kurs, sana değil kendine göre program yapıyor demektir.

Doğru olan: **yazılı + sözlü** seviye tespit sınavı. Sonuç: A1, A2, B1 gibi net bir seviye.

## 4. Haftada kaç saat ders var?

Haftada 2 saat dersle İngilizce öğrenilmez. B2 seviyesine gelmek için ortalama **500-600 saat** ders gerekiyor. Bunu 1 yılda bitirmek istiyorsan haftada 10-12 saat şart.

Kursa sor:

- Haftada kaç gün, kaç saat?
- Telafi dersi var mı?
- Konuşma kulübü var mı?

## 5. Materyaller dahil mi, ücretli mi?

Bazı kurslar kayıt ücretini düşük gösterip kitap, materyal diye ekstra para alıyor. Baştan net öğren:

- Kitap ve dijital materyaller dahil mi?
- Sınav ücretleri ne kadar?
- Toplam maliyet ne kadar?

## 6. Öğrencinin gelişimi nasıl takip ediliyor?

Bu, **veliler için en önemli soru**. Çocuğunuz haftada 2 kere gidip geliyor ama ne öğrendiğini bilmiyorsanız, süreç karanlıkta ilerliyor.

İyi bir kurs şunları sunar:

- Online veli paneli
- Aylık karne veya gelişim raporu
- Öğretmenle doğrudan iletişim

## 7. Sözleşme ve iade koşulları nasıl?

Son ama en önemli soru. Kayıt olmadan önce mutlaka **yazılı sözleşme** isteyin.

- Erken çıkışta iade var mı?
- Öğretmen değişirse ne olur?
- Ders iptal edilirse telafi nasıl yapılır?

"Sözlü anlaşırız" diyen bir kurstan uzak durun.

## C-Peak English bu sorulara nasıl cevap veriyor?

C-Peak English olarak Bayrampaşa'da bu 7 sorunun tamamına net cevap veriyoruz. Sınıflarımız küçük, öğretmenlerimiz sertifikalı ve her öğrencimizin gelişimini online panelden takip ediyoruz.

C-Peak English'te amacımız kalabalık sınıflarda sıra bekleyen öğrenciler değil; seviyesini bilen ve hedefine doğru ilerleyen öğrenciler yetiştirmek. İstanbul'da İngilizce öğrenmek isteyen herkesin şeffaf ve birebir ilgi gören bir kursu hak ettiğine inanıyoruz.

## Sonuç

Bu 7 soruyu bir deftere yaz. Her kursa gittiğinde sor. Cevapları karşılaştır. Sana net, somut, yazılı cevap veren kursu seç.

---

**Ücretsiz deneme dersi için:** 0542 180 84 02  
**Web:** cpeakenglish.com  
**Instagram:** @c_peak_english
'''


# ============================================================
# app.py patch
# ============================================================
BLOG_ROUTES = '''

# === CPK_BLOG ROUTES (blog_kur.py) ===
@app.route("/blog")
def blog_listesi():
    from cpk_blog import tum_yazilar
    yazilar = tum_yazilar()
    return render_template("blog.html", yazilar=yazilar)


@app.route("/blog/<slug>")
def blog_yazi(slug):
    from cpk_blog import yazi_bul
    yazi = yazi_bul(slug)
    if not yazi:
        return "Yazı bulunamadı", 404
    return render_template("blog_yazi.html", yazi=yazi)
# === /CPK_BLOG ROUTES ===

'''


def app_patch(ic: str):
    if "CPK_BLOG ROUTES" in ic:
        return ic, False, "blog route'ları zaten var"

    # Blog route'larını /hakkimizda route'undan önce ekle
    pat = re.compile(
        r'(@app\.route\([\'"]/hakkimizda[\'"]\)\s*\ndef\s+hakkimizda)',
        re.MULTILINE,
    )
    m = pat.search(ic)
    if not m:
        return ic, False, "/hakkimizda route'u bulunamadı"

    yeni = ic[:m.start()] + BLOG_ROUTES.lstrip("\n") + ic[m.start():]

    # Sitemap'e blog yazılarını ekle
    pat2 = re.compile(
        r'(def sitemap_xml\(\):\s*\n)(\s*)(pages\s*=\s*\[)',
        re.MULTILINE,
    )
    m2 = pat2.search(yeni)
    if m2:
        # "pages = [" satırından sonra blog import'unu ekleyelim
        # Ama zaten pages listesi var — sonuna eklemek daha temiz
        pat3 = re.compile(
            r'(def sitemap_xml\(\):.*?pages\s*=\s*\[)(.*?)(\])',
            re.DOTALL,
        )
        m3 = pat3.search(yeni)
        if m3 and "cpk_blog" not in m3.group(0):
            # Blog döngüsünü pages listesi kapanışından sonra ekle
            ekle = (
                "\n    from cpk_blog import tum_yazilar as _blog_yazilar\n"
                "    for _y in _blog_yazilar():\n"
                "        pages.append(f\"https://www.cpeakenglish.com/blog/{_y['slug']}\")\n"
            )
            yeni = yeni[:m3.end(3)] + ekle + yeni[m3.end(3):]

    return yeni, True, "blog route'ları + sitemap güncellendi"


# ============================================================
# base_seo.html patch — nav injector
# ============================================================
NAV_INJECTOR = '''
<script id="cpk-blog-nav-injector">
(function () {
  "use strict";
  function ekle() {
    var nav = document.querySelector(".cpk-nav");
    if (!nav) return;
    if (nav.querySelector('a[href="/blog"]')) return;
    var link = document.createElement("a");
    link.href = "/blog";
    link.textContent = "Blog";
    var iletisim = nav.querySelector('a[href="/iletisim"]');
    if (iletisim) nav.insertBefore(link, iletisim);
    else nav.appendChild(link);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ekle);
  } else {
    ekle();
  }
  setTimeout(ekle, 500);
})();
</script>
'''


def base_seo_patch(ic: str):
    if "cpk-blog-nav-injector" in ic:
        return ic, False, "nav injector zaten var"

    idx = ic.rfind("</body>")
    if idx == -1:
        return ic, False, "</body> bulunamadı"

    yeni = ic[:idx] + NAV_INJECTOR + "\n" + ic[idx:]
    return yeni, True, "nav injector eklendi"


# ============================================================
# requirements.txt patch
# ============================================================
def req_patch(ic: str):
    if "Markdown" in ic or "markdown" in ic.lower():
        return ic, False, "Markdown zaten var"
    yeni = ic.rstrip() + "\nMarkdown>=3.5.0\n"
    return yeni, True, "Markdown kütüphanesi eklendi"


# ============================================================
# GIT
# ============================================================
def git_kok_bul(p):
    p = p.resolve()
    for u in [p] + list(p.parents):
        if (u / ".git").exists(): return u
    return None


def git_calistir(kok, *a, sessiz=False):
    r = subprocess.run(["git"]+list(a), cwd=str(kok), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if not sessiz:
        if r.stdout.strip(): print("    " + r.stdout.strip().replace("\n","\n    "))
        if r.stderr.strip(): print("    " + r.stderr.strip().replace("\n","\n    "))
    return r


def git_commit_push(*yollar):
    print("\n[GIT] Başlatılıyor...")
    kok = None
    for y in yollar:
        kok = git_kok_bul(y)
        if kok: break
    if kok is None: print("[GIT] .git yok — atlandı."); return False
    try: subprocess.run(["git","--version"], capture_output=True, check=True)
    except Exception: print("[GIT] git kurulu değil — atlandı."); return False

    # Tüm dosyaları ekle (yeni klasörler için)
    if git_calistir(kok, "add", "-A").returncode != 0:
        print("[GIT] add başarısız."); return False
    if git_calistir(kok, "diff", "--cached", "--quiet", sessiz=True).returncode == 0:
        print("[GIT] Değişiklik yok."); return False
    if git_calistir(kok, "commit", "-m", COMMIT_MSG).returncode != 0:
        print("[GIT] commit başarısız."); return False
    if git_calistir(kok, "push").returncode != 0:
        print("[GIT] UYARI: push başarısız."); return False
    print("[GIT] ✓ commit + push tamam."); return True


# ============================================================
# ANA
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not APP.exists():
        print(f"[HATA] {APP} bulunamadı."); sys.exit(1)

    plan = []
    icerikler = {}

    # 1) content/blog klasörü
    if not CONTENT.exists():
        plan.append("+ content/blog/")
        icerikler["__mkdir_content"] = True

    # 2) cpk_blog.py
    if not BLOG_MODUL.exists():
        plan.append(f"+ cpk_blog.py")
        icerikler["cpk_blog"] = BLOG_PY

    # 3) templates
    if not TMPL_LISTE.exists():
        plan.append(f"+ templates/blog.html")
        icerikler["blog.html"] = TMPL_LISTE_HTML
    if not TMPL_YAZI.exists():
        plan.append(f"+ templates/blog_yazi.html")
        icerikler["blog_yazi.html"] = TMPL_YAZI_HTML

    # 4) app.py
    app_ic = APP.read_text(encoding="utf-8")
    yeni_app, app_d, app_m = app_patch(app_ic)
    if app_d:
        plan.append(f"~ app.py ({app_m})")
        icerikler["app.py"] = yeni_app

    # 5) base_seo.html
    if BASE_SEO.exists():
        bs_ic = BASE_SEO.read_text(encoding="utf-8")
        yeni_bs, bs_d, bs_m = base_seo_patch(bs_ic)
        if bs_d:
            plan.append(f"~ base_seo.html ({bs_m})")
            icerikler["base_seo.html"] = yeni_bs

    # 6) requirements.txt
    if REQ.exists():
        req_ic = REQ.read_text(encoding="utf-8")
        yeni_req, req_d, req_m = req_patch(req_ic)
        if req_d:
            plan.append(f"~ requirements.txt ({req_m})")
            icerikler["requirements.txt"] = yeni_req

    # 7) Örnek yazı
    ornek = CONTENT / "bayrampasa-ingilizce-kursu-nasil-secilir.md"
    if not ornek.exists():
        plan.append(f"+ content/blog/{ornek.name}")
        icerikler["ornek_yazi"] = ORNEK_YAZI

    print("=" * 60)
    print("  BLOG KURULUMU")
    print("=" * 60)
    print(f"\nYapılacaklar ({len(plan)} işlem):")
    for p in plan:
        print(f"  {p}")

    if not plan:
        print("\n[ATLA] Hepsi zaten kurulu.")
        return

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Yedek + yaz
    # content/blog
    if icerikler.pop("__mkdir_content", None):
        CONTENT.mkdir(parents=True, exist_ok=True)
        print(f"[OK] content/blog/ oluşturuldu")

    if "cpk_blog" in icerikler:
        BLOG_MODUL.write_text(icerikler.pop("cpk_blog"), encoding="utf-8")
        print(f"[OK] cpk_blog.py")

    if "blog.html" in icerikler:
        TMPL_LISTE.write_text(icerikler.pop("blog.html"), encoding="utf-8")
        print(f"[OK] templates/blog.html")

    if "blog_yazi.html" in icerikler:
        TMPL_YAZI.write_text(icerikler.pop("blog_yazi.html"), encoding="utf-8")
        print(f"[OK] templates/blog_yazi.html")

    if "app.py" in icerikler:
        yed = YED_DIR / f"app.py.{stamp}.bak"
        shutil.copy2(APP, yed)
        print(f"[YEDEK] backups/{yed.name}")
        APP.write_text(icerikler.pop("app.py"), encoding="utf-8")
        print(f"[OK] app.py güncellendi")

    if "base_seo.html" in icerikler:
        yed = YED_DIR / f"base_seo.html.{stamp}.bak"
        shutil.copy2(BASE_SEO, yed)
        print(f"[YEDEK] backups/{yed.name}")
        BASE_SEO.write_text(icerikler.pop("base_seo.html"), encoding="utf-8")
        print(f"[OK] base_seo.html güncellendi")

    if "requirements.txt" in icerikler:
        yed = YED_DIR / f"requirements.txt.{stamp}.bak"
        shutil.copy2(REQ, yed)
        REQ.write_text(icerikler.pop("requirements.txt"), encoding="utf-8")
        print(f"[OK] requirements.txt güncellendi")

    if "ornek_yazi" in icerikler:
        CONTENT.mkdir(parents=True, exist_ok=True)
        ornek.write_text(icerikler.pop("ornek_yazi"), encoding="utf-8")
        print(f"[OK] content/blog/{ornek.name}")

    print("\n[!] ÖNEMLİ: markdown kütüphanesi kurulu değilse:")
    print("    py -m pip install Markdown")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(
            APP, BLOG_MODUL, TMPL_LISTE, TMPL_YAZI,
            BASE_SEO, REQ, CONTENT / ".",
        )

    print("\nTest:")
    print("  1) py -m pip install Markdown")
    print("  2) Sunucuyu yeniden başlat")
    print("  3) Tarayıcıda: http://localhost:5000/blog")
    print("  4) Örnek yazı görünmeli → tıkla → açılmalı")
    print("  5) https://www.cpeakenglish.com/blog (deploy sonrası)")


if __name__ == "__main__":
    main()