#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blog_v2.py — Blog tasarımını premium/editorial görünüme geçirir.
              CTA'yı kaldırır. Tarihi TR formatına çevirir.

Değişir:
  - cpk_blog.py         → date_tr alanı eklendi (5 Ekim 2026)
  - templates/blog.html → editorial liste (numaralı, ince çizgiler)
  - templates/blog_yazi.html → dergi okuma deneyimi
  - content/blog/*.md   → CTA kısmı silinir

Kullanım:
  py blog_v2.py --dry-run
  py blog_v2.py --no-git
  py blog_v2.py
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
CONTENT = KOK / "content" / "blog"
TMPL = KOK / "templates"
YED_DIR = KOK / "backups"
BLOG_MODUL = KOK / "cpk_blog.py"

COMMIT_MSG = """ui(blog): editorial/premium tasarım + CTA temizliği

- cpk_blog.py: date_tr alanı (5 Ekim 2026 formatı)
- templates/blog.html: dergi içindekiler tarzı liste
  • Numaralı satırlar, ince çizgiler, hover'da kayan ok
  • Grid yerine editorial düzen
- templates/blog_yazi.html: okuma deneyimi
  • Drop-cap ilk harf, geniş satır aralığı, ortada dar kolon
  • Yazı sonunda paylaşım, CTA yok
- content/blog/*.md: "Ücretsiz deneme dersi" CTA'sı silindi
- Otomatik yama: blog_v2.py"""


# ============================================================
# 1) cpk_blog.py — Türkçe tarih formatı
# ============================================================
BLOG_PY = '''# -*- coding: utf-8 -*-
"""
cpk_blog.py — Markdown blog yükleyici.
"""
import re
from pathlib import Path

try:
    import markdown as _md
    _MD_VAR = True
except ImportError:
    _MD_VAR = False

BLOG_DIR = Path(__file__).resolve().parent / "content" / "blog"

_AYLAR = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def _slugla(metin):
    esleme = str.maketrans({
        "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i", "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
    })
    s = metin.translate(esleme).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _frontmatter(metin):
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


def _tarih_tr(iso):
    """2026-10-05 -> 5 Ekim 2026"""
    try:
        y, m, d = iso.split("-")
        return f"{int(d)} {_AYLAR[int(m)]} {y}"
    except Exception:
        return iso


def _render_md(metin):
    if not _MD_VAR:
        parcalar = [p.strip() for p in metin.split("\\n\\n") if p.strip()]
        return "\\n".join(f"<p>{p}</p>" for p in parcalar)
    return _md.markdown(
        metin,
        extensions=["extra", "smarty", "sane_lists"],
    )


def _yazi_yukle(path):
    ic = path.read_text(encoding="utf-8")
    meta, body = _frontmatter(ic)
    slug = meta.get("slug") or _slugla(meta.get("title") or path.stem)
    tarih_iso = meta.get("date", "")
    return {
        "slug": slug,
        "title": meta.get("title") or path.stem,
        "description": meta.get("description", ""),
        "date": tarih_iso,
        "date_tr": _tarih_tr(tarih_iso),
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
# 2) templates/blog.html — editorial liste
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
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=blogv2">
<style>
/* ============================================================
   C-Peak · Blog — Editorial
   ============================================================ */
.cpk-blog-hero {
  padding: 80px 0 44px;
  text-align: left;
}
.cpk-blog-hero .container { max-width: 900px; }
.cpk-blog-eyebrow {
  display: inline-block;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .32em;
  text-transform: uppercase;
  color: #f59e0b;
  margin-bottom: 18px;
}
.cpk-blog-h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(2rem, 6vw, 3.4rem);
  font-weight: 500;
  line-height: 1.1;
  letter-spacing: -0.024em;
  color: #fff;
  margin: 0 0 22px;
  max-width: 760px;
}
.cpk-blog-h1 em {
  font-style: italic;
  font-weight: 400;
  color: rgba(255,255,255,.72);
}
.cpk-blog-intro {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 1.02rem;
  line-height: 1.68;
  color: rgba(255,255,255,.6);
  max-width: 620px;
  margin: 0;
}

/* --- İçindekiler listesi --- */
.cpk-blog-list {
  padding: 20px 0 100px;
}
.cpk-blog-list .container { max-width: 900px; }

.cpk-post-row {
  display: grid;
  grid-template-columns: 56px 1fr 40px;
  gap: 20px;
  align-items: center;
  padding: 34px 4px;
  border-top: 1px solid rgba(255,255,255,.08);
  text-decoration: none;
  color: inherit;
  transition: padding .25s ease;
  -webkit-tap-highlight-color: transparent;
}
.cpk-post-row:last-child {
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.cpk-post-row:hover,
.cpk-post-row:focus-visible {
  padding-left: 12px;
  padding-right: 0;
  outline: none;
}
.cpk-post-num {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.08rem;
  font-weight: 400;
  font-style: italic;
  color: rgba(255,255,255,.32);
  align-self: start;
  padding-top: 4px;
  transition: color .2s ease;
}
.cpk-post-row:hover .cpk-post-num,
.cpk-post-row:focus-visible .cpk-post-num {
  color: #f59e0b;
}
.cpk-post-body { min-width: 0; }
.cpk-post-date {
  display: block;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: rgba(255,255,255,.45);
  margin-bottom: 8px;
}
.cpk-post-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.4rem, 3.6vw, 1.85rem);
  font-weight: 500;
  line-height: 1.22;
  letter-spacing: -0.018em;
  color: #fff;
  margin: 0 0 10px;
  transition: color .2s ease;
}
.cpk-post-row:hover .cpk-post-title,
.cpk-post-row:focus-visible .cpk-post-title {
  color: #f59e0b;
}
.cpk-post-desc {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .94rem;
  line-height: 1.6;
  color: rgba(255,255,255,.55);
  margin: 0;
  max-width: 620px;
}
.cpk-post-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.14);
  color: rgba(255,255,255,.55);
  align-self: center;
  transition: all .22s ease;
  flex-shrink: 0;
}
.cpk-post-arrow svg {
  width: 14px;
  height: 14px;
  transition: transform .22s ease;
}
.cpk-post-row:hover .cpk-post-arrow,
.cpk-post-row:focus-visible .cpk-post-arrow {
  background: #f59e0b;
  border-color: #f59e0b;
  color: #18181b;
}
.cpk-post-row:hover .cpk-post-arrow svg,
.cpk-post-row:focus-visible .cpk-post-arrow svg {
  transform: translateX(2px);
}

.cpk-blog-empty {
  padding: 80px 0;
  text-align: center;
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 1.15rem;
  color: rgba(255,255,255,.4);
}

@media (max-width: 640px) {
  .cpk-blog-hero { padding: 48px 0 32px; }
  .cpk-post-row {
    grid-template-columns: 40px 1fr;
    gap: 14px;
    padding: 26px 0;
  }
  .cpk-post-arrow { display: none; }
  .cpk-post-title { font-size: 1.28rem; }
  .cpk-post-desc { font-size: .88rem; }
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
  <section class="cpk-blog-hero">
    <div class="container">
      <span class="cpk-blog-eyebrow">Blog</span>
      <h1 class="cpk-blog-h1">
        İngilizce öğrenmeye dair <em>notlar, rehberler ve denemeler.</em>
      </h1>
      <p class="cpk-blog-intro">
        Sınav hazırlığı, konuşma pratiği, çocuklara İngilizce ve daha fazlası.
        Bayrampaşa ve İstanbul'da İngilizce eğitimi üzerine pratik yazılar.
      </p>
    </div>
  </section>

  <section class="cpk-blog-list">
    <div class="container">
      {% if yazilar %}
        {% for y in yazilar %}
        <a href="/blog/{{ y.slug }}" class="cpk-post-row">
          <span class="cpk-post-num">{{ "%02d"|format(loop.index) }}</span>
          <div class="cpk-post-body">
            <span class="cpk-post-date">{{ y.date_tr }}</span>
            <h2 class="cpk-post-title">{{ y.title }}</h2>
            {% if y.description %}
            <p class="cpk-post-desc">{{ y.description }}</p>
            {% endif %}
          </div>
          <span class="cpk-post-arrow" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </span>
        </a>
        {% endfor %}
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
# 3) templates/blog_yazi.html — dergi okuma
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
<link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}?v=blogv2">
<style>
/* ============================================================
   C-Peak · Blog Yazısı — Okuma Deneyimi
   ============================================================ */
.cpk-post-wrap {
  max-width: 720px;
  margin: 0 auto;
  padding: 72px 24px 100px;
}
.cpk-post-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .82rem;
  font-weight: 600;
  letter-spacing: .04em;
  color: rgba(255,255,255,.5);
  text-decoration: none;
  margin-bottom: 36px;
  transition: color .18s ease;
}
.cpk-post-back:hover { color: #f59e0b; }
.cpk-post-back svg { width: 12px; height: 12px; }

.cpk-post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: .74rem;
  font-weight: 600;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: rgba(255,255,255,.42);
  margin-bottom: 20px;
}
.cpk-post-meta .dot {
  width: 3px; height: 3px;
  border-radius: 50%;
  background: rgba(255,255,255,.3);
}

.cpk-post-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.9rem, 5.2vw, 2.9rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.022em;
  color: #fff;
  margin: 0 0 22px;
}

.cpk-post-lead {
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: clamp(1.06rem, 2.4vw, 1.22rem);
  line-height: 1.55;
  color: rgba(255,255,255,.68);
  margin: 0 0 44px;
  padding-bottom: 44px;
  border-bottom: 1px solid rgba(255,255,255,.08);
}

/* --- İçerik --- */
.cpk-post-body {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 1.08rem;
  line-height: 1.78;
  color: rgba(255,255,255,.82);
  letter-spacing: -0.003em;
}
.cpk-post-body > p:first-of-type::first-letter {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 4.2em;
  font-weight: 500;
  line-height: .88;
  float: left;
  padding: .08em .12em 0 0;
  color: #f59e0b;
}
.cpk-post-body h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.34rem, 3.4vw, 1.62rem);
  font-weight: 500;
  line-height: 1.28;
  letter-spacing: -0.014em;
  color: #fff;
  margin: 54px 0 16px;
}
.cpk-post-body h3 {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 1.08rem;
  font-weight: 700;
  letter-spacing: -0.004em;
  color: #fff;
  margin: 34px 0 12px;
}
.cpk-post-body p { margin: 0 0 22px; }
.cpk-post-body a {
  color: #f59e0b;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 4px;
  transition: color .15s ease;
}
.cpk-post-body a:hover { color: #fff; }
.cpk-post-body ul, .cpk-post-body ol {
  margin: 0 0 24px;
  padding-left: 22px;
}
.cpk-post-body li { margin-bottom: 10px; padding-left: 4px; }
.cpk-post-body strong { color: #fff; font-weight: 700; }
.cpk-post-body em { font-style: italic; color: rgba(255,255,255,.9); }
.cpk-post-body blockquote {
  margin: 30px 0;
  padding: 4px 0 4px 24px;
  border-left: 2px solid #f59e0b;
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 1.14rem;
  line-height: 1.55;
  color: rgba(255,255,255,.75);
}
.cpk-post-body hr {
  border: 0;
  border-top: 1px solid rgba(255,255,255,.09);
  margin: 48px auto;
  width: 40px;
}
.cpk-post-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .9em;
  background: rgba(255,255,255,.06);
  padding: 2px 6px;
  border-radius: 5px;
  color: #f59e0b;
}

/* --- Yazı sonu --- */
.cpk-post-foot {
  margin-top: 72px;
  padding-top: 40px;
  border-top: 1px solid rgba(255,255,255,.08);
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  text-align: center;
}
.cpk-post-foot-tag {
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 1.04rem;
  color: rgba(255,255,255,.5);
}
.cpk-post-foot-share {
  display: flex;
  gap: 10px;
  align-items: center;
}
.cpk-post-foot-share a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px; height: 38px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.14);
  color: rgba(255,255,255,.7);
  text-decoration: none;
  transition: all .18s ease;
}
.cpk-post-foot-share a:hover {
  background: #f59e0b;
  border-color: #f59e0b;
  color: #18181b;
  transform: translateY(-2px);
}
.cpk-post-foot-share svg { width: 15px; height: 15px; }

@media (max-width: 640px) {
  .cpk-post-wrap { padding: 44px 20px 72px; }
  .cpk-post-body > p:first-of-type::first-letter {
    font-size: 3.4em;
    padding: .1em .1em 0 0;
  }
  .cpk-post-body h2 { margin-top: 40px; }
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
  <article class="cpk-post-wrap">
    <a href="/blog" class="cpk-post-back">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
      Tüm yazılar
    </a>

    <div class="cpk-post-meta">
      <span>{{ yazi.date_tr }}</span>
      <span class="dot"></span>
      <span>{{ yazi.author }}</span>
    </div>

    <h1 class="cpk-post-title">{{ yazi.title }}</h1>

    {% if yazi.description %}
    <p class="cpk-post-lead">{{ yazi.description }}</p>
    {% endif %}

    <div class="cpk-post-body">
      {{ yazi.html | safe }}
    </div>

    <div class="cpk-post-foot">
      <span class="cpk-post-foot-tag">— C-Peak English</span>
      <div class="cpk-post-foot-share">
        <a href="https://www.instagram.com/c_peak_english" target="_blank"
           rel="noopener" aria-label="Instagram">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="5"></rect>
            <circle cx="12" cy="12" r="4"></circle>
            <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"></circle>
          </svg>
        </a>
        <a href="https://www.youtube.com/@c-peak-english" target="_blank"
           rel="noopener" aria-label="YouTube">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 8.5a3 3 0 0 0-2.1-2.1C18 6 12 6 12 6s-6 0-7.9.4A3 3 0 0 0 2 8.5 31 31 0 0 0 2 12a31 31 0 0 0 .1 3.5 3 3 0 0 0 2.1 2.1C6 18 12 18 12 18s6 0 7.9-.4a3 3 0 0 0 2.1-2.1A31 31 0 0 0 22 12a31 31 0 0 0-.1-3.5z"></path>
            <polygon points="10 9 16 12 10 15 10 9" fill="currentColor" stroke="none"></polygon>
          </svg>
        </a>
      </div>
    </div>
  </article>
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
# 4) Yazılardan CTA'yı temizle
# ============================================================
def cta_temizle(metin):
    """
    Şu blokları sil:
      ---
      **Ücretsiz deneme dersi için:** ...
      **Web:** ...
      **Instagram:** ...
    """
    # Önce ortadaki CTA + hr bloğunu ara
    patterns = [
        # "---" + CTA bloğu
        re.compile(
            r"\n---\s*\n+\s*\*\*Ücretsiz deneme dersi için:\*\*.*?"
            r"(?=\Z|\n##)",
            re.DOTALL,
        ),
        # Sadece CTA (hr olmadan)
        re.compile(
            r"\n\s*\*\*Ücretsiz deneme dersi için:\*\*.*?(?=\Z|\n##)",
            re.DOTALL,
        ),
        # "**Web:**" satırından itibaren
        re.compile(
            r"\n\s*\*\*Web:\*\*.*?(?=\Z|\n##)",
            re.DOTALL,
        ),
    ]
    yeni = metin
    for pat in patterns:
        yeni2 = pat.sub("\n", yeni)
        if yeni2 != yeni:
            yeni = yeni2
            break
    # Sondaki fazla boşlukları temizle
    yeni = re.sub(r"\n{3,}", "\n\n", yeni).rstrip() + "\n"
    return yeni


def icerik_duzelt(metin):
    if "Ücretsiz deneme dersi" not in metin:
        return metin, False, "CTA yok"
    yeni = cta_temizle(metin)
    if yeni == metin:
        return metin, False, "CTA temizlenemedi (regex eşleşmedi)"
    return yeni, True, "CTA kaldırıldı"


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


def git_commit_push():
    print("\n[GIT] Başlatılıyor...")
    kok = git_kok_bul(KOK)
    if kok is None:
        print("[GIT] .git yok — atlandı."); return False
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

    degis = []

    # 1) cpk_blog.py
    if BLOG_MODUL.exists():
        eski = BLOG_MODUL.read_text(encoding="utf-8")
        if "date_tr" not in eski:
            degis.append((BLOG_MODUL, BLOG_PY, "cpk_blog.py: date_tr eklendi"))
        else:
            print("[·] cpk_blog.py: date_tr zaten var")

    # 2) blog.html
    hedef = TMPL / "blog.html"
    if hedef.exists():
        eski = hedef.read_text(encoding="utf-8")
        if "blogv2" not in eski:
            degis.append((hedef, TMPL_LISTE_HTML, "blog.html: editorial tasarım"))
        else:
            print("[·] blog.html: v2 zaten kurulu")

    # 3) blog_yazi.html
    hedef2 = TMPL / "blog_yazi.html"
    if hedef2.exists():
        eski = hedef2.read_text(encoding="utf-8")
        if "blogv2" not in eski:
            degis.append((hedef2, TMPL_YAZI_HTML, "blog_yazi.html: dergi deneyimi"))
        else:
            print("[·] blog_yazi.html: v2 zaten kurulu")

    # 4) Markdown yazılardan CTA'yı temizle
    cta_sayisi = 0
    if CONTENT.exists():
        for md in sorted(CONTENT.glob("*.md")):
            eski = md.read_text(encoding="utf-8")
            yeni, d, m = icerik_duzelt(eski)
            if d:
                degis.append((md, yeni, f"{md.name}: CTA kaldırıldı"))
                cta_sayisi += 1
            else:
                print(f"[·] {md.name}: {m}")

    print("=" * 60)
    print("  BLOG v2 — EDITORIAL TASARIM + CTA TEMİZLİĞİ")
    print("=" * 60)

    if not degis:
        print("\n[ATLA] Değişiklik yok.")
        return

    print(f"\nYapılacaklar ({len(degis)}):")
    for y, _, m in degis:
        print(f"  ~ {y.relative_to(KOK)}  ({m})")

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for yol, icerik, mesaj in degis:
        yed = YED_DIR / f"{yol.name}.{stamp}.bak"
        shutil.copy2(yol, yed)
        yol.write_text(icerik, encoding="utf-8")
        print(f"[OK] {yol.relative_to(KOK)}  ({mesaj})")

    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push()

    print("\nTest:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) /blog → numaralı editorial liste")
    print("  3) Bir yazıya tıkla → drop-cap, geniş satır aralığı")
    print("  4) Yazı sonunda CTA YOK, sadece paylaşım ikonları")
    print("  5) Tarih '5 Ekim 2026' formatında")


if __name__ == "__main__":
    main()