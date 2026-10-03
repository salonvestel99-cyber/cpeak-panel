#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mobil_pro.py — C-Peak mobil deneyim katmanı
  static/mobil_pro.css + static/mobil_pro.js oluşturur
  templates/base.html'e idempotent olarak bağlar
  Git commit + push
Kullanım: py mobil_pro.py [--no-git] [--dry-run]
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
STATIC = KOK / "static"
BASE = KOK / "templates" / "base.html"
YED_DIR = KOK / "backups"

CSS_YOL = STATIC / "mobil_pro.css"
JS_YOL  = STATIC / "mobil_pro.js"

MARKER = "MOBIL_PRO_V1"

COMMIT_MSG = """mobil(feat): pro katman — hamburger, bottom tab, kart tablo, bottom-sheet

- static/mobil_pro.css + mobil_pro.js eklendi
- base.html'e idempotent olarak bağlandı
- Topbar mobil: hamburger + slide-in drawer
- Bottom tab bar (topbar-nav linklerinden otomatik üretilir)
- Tablolar mobilde kart görünümüne dönüşür
- Modallar bottom-sheet davranışına geçer
- Safe-area, dokunma feedback, loading state
- Form row mobilde tek sütun
- iOS klavye scrollIntoView
- Masaüstü etkilenmez: tüm CSS @media (max-width: 900px) içinde
- Otomatik yama: mobil_pro.py [MOBIL_PRO_V1]"""
COMMIT_MSG = COMMIT_MSG  # sabit


# ============================================================
# CSS
# ============================================================
CSS_ICERIK = r'''/* ============================================================
   C-Peak · MOBİL PRO KATMANI v1
   Tüm kurallar @media (max-width: 900px) içinde.
   Masaüstü düzeni HİÇ etkilenmez.
   ============================================================ */

/* ---------- 0) AYARLAR ---------- */
:root {
  --mpro-tab-h: 62px;
  --mpro-topbar-h: 56px;
}

@media (max-width: 900px) {

  /* ---------- 0.1) SAFE-AREA + TEMEL ---------- */
  html {
    -webkit-text-size-adjust: 100%;
  }
  body {
    padding-bottom: env(safe-area-inset-bottom) !important;
    overflow-x: hidden !important;
  }
  /* Topbar ve tab bar hariç tüm main içerik tab bar'ın üstünde kalsın */
  body.mpro-has-tab main,
  body.mpro-has-tab .container,
  body.mpro-has-tab .wrapper {
    padding-bottom: calc(var(--mpro-tab-h) + env(safe-area-inset-bottom) + 16px) !important;
  }

  /* ---------- 0.2) DOKUNMA GERİ BİLDİRİMİ ---------- */
  button, a.btn, a.btn-primary, a.btn-ghost, .btn-primary, .btn-ghost,
  .btn-mini, .qa-btn, .st-quick-card, .tp-quick-card, .admin-tab,
  .odev-card, .card {
    -webkit-tap-highlight-color: transparent;
    transition: transform .12s ease, box-shadow .15s ease,
                background-color .15s ease !important;
  }
  button:active, a.btn:active, .btn-primary:active, .btn-ghost:active,
  .btn-mini:active, .qa-btn:active, .admin-tab:active,
  .st-quick-card:active, .tp-quick-card:active, .odev-card:active {
    transform: scale(.975) !important;
  }

  /* ---------- 0.3) TOPBAR / HAMBURGER ---------- */
  .topbar {
    height: var(--mpro-topbar-h) !important;
    min-height: var(--mpro-topbar-h) !important;
    padding-top: env(safe-area-inset-top) !important;
  }
  .topbar-inner {
    padding: 0 14px !important;
    height: var(--mpro-topbar-h) !important;
    gap: 10px !important;
  }

  /* Hamburger butonu (JS ekler) */
  .mpro-hamburger {
    display: none;
    align-items: center; justify-content: center;
    width: 42px; height: 42px;
    border-radius: 10px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.10);
    color: #fff;
    cursor: pointer;
    flex-shrink: 0;
    padding: 0;
  }
  body.mpro-has-nav .mpro-hamburger { display: inline-flex; }
  .mpro-hamburger:active { transform: scale(.94); background: rgba(255,255,255,.12); }
  .mpro-hamburger svg { width: 20px; height: 20px; }

  /* Masaüstü nav'ı mobilde gizle */
  body.mpro-has-nav .topbar-nav { display: none !important; }
  body.mpro-has-nav .topbar-user-info { display: none !important; }

  /* ---------- 0.4) DRAWER (slide-in) ---------- */
  .mpro-backdrop {
    position: fixed; inset: 0;
    background: rgba(0,0,0,.5);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    opacity: 0;
    pointer-events: none;
    transition: opacity .22s ease;
    z-index: 1800;
  }
  body.mpro-drawer-open .mpro-backdrop,
  body.mpro-sheet-open .mpro-backdrop {
    opacity: 1;
    pointer-events: auto;
  }

  .mpro-drawer {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: min(82vw, 320px);
    background: #131316;
    border-right: 1px solid rgba(255,255,255,.06);
    padding: calc(env(safe-area-inset-top) + 20px) 20px 24px;
    transform: translateX(-100%);
    transition: transform .26s cubic-bezier(.22,.9,.28,1);
    z-index: 1900;
    overflow-y: auto;
    box-shadow: 8px 0 32px rgba(0,0,0,.28);
    display: flex; flex-direction: column;
    gap: 4px;
  }
  body.mpro-drawer-open .mpro-drawer { transform: translateX(0); }

  .mpro-drawer-head {
    display: flex; align-items: center; gap: 12px;
    padding-bottom: 16px; margin-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,.08);
  }
  .mpro-drawer-head img { height: 36px; width: auto; }
  .mpro-drawer-head .mpro-drawer-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.1rem; font-weight: 600;
    color: #fff; line-height: 1.1;
    display: flex; flex-direction: column;
  }
  .mpro-drawer-head .mpro-drawer-sub {
    font-family: 'Inter', sans-serif;
    font-size: .58rem; letter-spacing: .28em; text-transform: uppercase;
    opacity: .55; font-weight: 500; margin-top: 4px;
  }

  .mpro-drawer a,
  .mpro-drawer button.mpro-drawer-item {
    display: flex; align-items: center; gap: 12px;
    padding: 13px 14px;
    border-radius: 10px;
    color: rgba(255,255,255,.82);
    text-decoration: none;
    font-family: inherit; font-size: .95rem; font-weight: 500;
    background: none; border: none;
    text-align: left; width: 100%;
    cursor: pointer;
    transition: background-color .14s, color .14s, transform .12s;
    -webkit-tap-highlight-color: transparent;
  }
  .mpro-drawer a:hover,
  .mpro-drawer button.mpro-drawer-item:hover {
    background: rgba(255,255,255,.06);
    color: #fff;
  }
  .mpro-drawer a:active,
  .mpro-drawer button.mpro-drawer-item:active {
    transform: scale(.98);
    background: rgba(255,255,255,.10);
  }
  .mpro-drawer a.mpro-active,
  .mpro-drawer button.mpro-active {
    background: rgba(217,119,6,.14);
    color: #f59e0b;
  }
  .mpro-drawer-sep {
    height: 1px; background: rgba(255,255,255,.08);
    margin: 10px 6px;
  }

  /* ---------- 0.5) BOTTOM TAB BAR ---------- */
  .mpro-tabbar {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    height: calc(var(--mpro-tab-h) + env(safe-area-inset-bottom));
    padding-bottom: env(safe-area-inset-bottom);
    background: rgba(19,19,22,.94);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-top: 1px solid rgba(255,255,255,.07);
    z-index: 1700;
    display: none;
    box-shadow: 0 -4px 18px rgba(0,0,0,.22);
  }
  body.mpro-has-tab .mpro-tabbar { display: flex; }

  .mpro-tabbar-inner {
    display: flex; align-items: stretch; justify-content: space-around;
    width: 100%; height: var(--mpro-tab-h);
  }
  .mpro-tab {
    flex: 1 1 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 3px;
    color: rgba(255,255,255,.55);
    text-decoration: none;
    font-family: inherit; font-size: .62rem; font-weight: 500;
    letter-spacing: .01em;
    padding: 6px 4px;
    border: none; background: none; cursor: pointer;
    transition: color .15s, transform .12s;
    -webkit-tap-highlight-color: transparent;
    position: relative;
  }
  .mpro-tab svg {
    width: 20px; height: 20px;
    stroke: currentColor; fill: none;
    stroke-width: 1.9;
  }
  .mpro-tab:active { transform: scale(.94); }
  .mpro-tab.mpro-active {
    color: #f59e0b;
  }
  .mpro-tab.mpro-active::before {
    content: "";
    position: absolute; top: 4px;
    width: 22px; height: 2px;
    background: #f59e0b; border-radius: 2px;
    box-shadow: 0 0 12px rgba(245,158,11,.6);
  }

  /* ---------- 0.6) MODAL → BOTTOM SHEET ---------- */
  .modal {
    align-items: flex-end !important;
    justify-content: center !important;
    padding: 0 !important;
  }
  .modal-card {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    border-radius: 22px 22px 0 0 !important;
    padding: 22px 20px calc(20px + env(safe-area-inset-bottom)) !important;
    max-height: 88dvh !important;
    overflow-y: auto !important;
    transform: translateY(100%);
    transition: transform .3s cubic-bezier(.22,.9,.28,1);
    will-change: transform;
  }
  body.mpro-sheet-open .modal-card { transform: translateY(0); }
  /* Modal içi kapatma tırtığı */
  .mpro-sheet-handle {
    width: 40px; height: 4px;
    background: rgba(0,0,0,.14);
    border-radius: 4px;
    margin: 0 auto 12px;
    display: block;
  }
  [data-theme="dark"] .mpro-sheet-handle,
  html.dark .mpro-sheet-handle { background: rgba(255,255,255,.20); }

  /* ---------- 0.7) TABLOLAR → KART ---------- */
  /* .table-wrap içindeki tablolar için sütun sıkışsa bile okunur kalsın */
  .table-wrap {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -2px;
  }
  .table-wrap table {
    min-width: 520px; /* çok dar tabloyu zorlaştırmasın */
  }
  /* Eğer tablo data-mpro-card işaretliyse kart görünümüne geç */
  table[data-mpro-card] {
    min-width: 0 !important;
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
  }
  table[data-mpro-card] thead { display: none !important; }
  table[data-mpro-card] tr {
    display: block !important;
    background: var(--surface, #fff);
    border: 1px solid var(--border, #e4e4e7);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
  }
  table[data-mpro-card] td {
    display: flex !important;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
    padding: 6px 0 !important;
    border: none !important;
    font-size: .88rem !important;
    text-align: right !important;
  }
  table[data-mpro-card] td::before {
    content: attr(data-label);
    font-size: .72rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: var(--muted, #71717a);
    text-align: left;
    flex: 0 0 auto;
    max-width: 45%;
    line-height: 1.5;
  }
  table[data-mpro-card] td:first-child {
    font-weight: 600;
    font-size: .95rem !important;
    color: var(--ink, #18181b);
    padding-bottom: 10px !important;
    border-bottom: 1px solid var(--border, #e4e4e7) !important;
    margin-bottom: 6px;
  }
  table[data-mpro-card] td:first-child::before { display: none; }

  /* ---------- 0.8) FORM ROW TEK SÜTUN ---------- */
  .form-row,
  .not-filter-form .form-row,
  .admin-form .form-row {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }
  .form-row label.full { grid-column: auto !important; }
  .filter-button {
    display: block !important;
    width: 100% !important;
  }
  .filter-button button,
  .filter-button .btn-primary,
  .filter-button .btn-ghost {
    width: 100% !important;
    max-width: 100% !important;
  }

  /* ---------- 0.9) KARTLAR TEK SÜTUN ---------- */
  .odev-grid {
    grid-template-columns: 1fr !important;
  }
  .ders-grid {
    grid-template-columns: 1fr !important;
  }
  .stat-grid {
    grid-template-columns: 1fr !important;
  }
  .admin-grid-2 {
    grid-template-columns: 1fr !important;
  }
  .admin-stats-row {
    flex-wrap: wrap !important;
    gap: 8px !important;
  }
  .as-item {
    flex: 1 1 calc(50% - 8px) !important;
    min-width: 0 !important;
  }

  /* ---------- 0.10) ADMIN SEKMELERİ ---------- */
  .admin-tabs {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    scroll-snap-type: x mandatory;
    padding-bottom: 6px !important;
    gap: 6px !important;
    scrollbar-width: none;
  }
  .admin-tabs::-webkit-scrollbar { display: none; }
  .admin-tab {
    scroll-snap-align: start;
    flex: 0 0 auto !important;
    padding: 9px 14px !important;
    font-size: .85rem !important;
    white-space: nowrap !important;
  }
  .admin-tab.is-active {
    background: var(--copper, #b45309) !important;
    color: #fff !important;
  }

  /* ---------- 0.11) BİLDİRİM / ÖDEV KARTLARI ---------- */
  .bl-kart, .bm-kart {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
    padding: 14px !important;
  }
  .bl-aksiyonlar {
    flex-direction: row !important;
    flex-wrap: wrap !important;
    min-width: 0 !important;
    gap: 8px !important;
  }
  .bl-aksiyonlar form { flex: 1 1 calc(50% - 4px) !important; }
  .bl-btn { width: 100% !important; }
  .bl-tabs { gap: 4px !important; }
  .bl-tab { padding: 7px 11px !important; font-size: .78rem !important; }

  /* ---------- 0.12) ŞİFRE DEĞİŞTİR / LEGAL ---------- */
  .pwd-page { padding: 0 14px !important; margin: 24px auto 48px !important; }
  .pwd-card { padding: 22px 18px !important; }
  .legal-page { padding: 24px 14px 60px !important; }
  .mail-page { padding: 0 !important; }
  .mail-hero { padding: 20px 18px !important; }
  .mail-card { padding: 20px 16px !important; }

  /* ---------- 0.13) WHATSAPP FLOAT (tab bar üstüne çıkmasın) ---------- */
  body.mpro-has-tab .whatsapp-float {
    bottom: calc(var(--mpro-tab-h) + env(safe-area-inset-bottom) + 14px) !important;
  }
  /* Sorun bildir FAB da aynı */
  body.mpro-has-tab .fb-fab {
    bottom: calc(var(--mpro-tab-h) + env(safe-area-inset-bottom) + 14px) !important;
  }

  /* ---------- 0.14) LOADING STATE ---------- */
  button.mpro-loading,
  .btn-primary.mpro-loading {
    position: relative !important;
    color: transparent !important;
    pointer-events: none !important;
  }
  button.mpro-loading::after,
  .btn-primary.mpro-loading::after {
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    width: 18px; height: 18px;
    margin: -9px 0 0 -9px;
    border: 2px solid rgba(255,255,255,.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: mpro-spin .7s linear infinite;
  }
  @keyframes mpro-spin { to { transform: rotate(360deg); } }

  /* ---------- 0.15) HEADER / PAGE-HEAD ---------- */
  .page-head { padding: 18px 14px 14px !important; }
  .panel-hero {
    padding: 20px 16px !important;
    border-radius: 14px !important;
  }
  .panel-hero-greet { font-size: 1.25rem !important; }

  .st-hero, .tp-hero {
    padding: 22px 0 18px !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 14px !important;
  }
  .st-hero-avatar, .tp-hero-avatar { align-self: flex-end !important; }

  /* ---------- 0.16) TOPBAR MENÜ AÇILINCA SCROLL KİLİT ---------- */
  body.mpro-drawer-open,
  body.mpro-sheet-open {
    overflow: hidden !important;
  }

  /* ---------- 0.17) iOS input zoom engeli (genel) ---------- */
  input, select, textarea {
    font-size: 16px !important;
  }
}

/* Çok küçük ekran: 380px altı */
@media (max-width: 380px) {
  .mpro-tab { font-size: .58rem !important; }
  .mpro-tab svg { width: 18px !important; height: 18px !important; }
  .mpro-tabbar { --mpro-tab-h: 58px; }
}
'''


# ============================================================
# JS
# ============================================================
JS_ICERIK = r'''/* ============================================================
   C-Peak · MOBİL PRO KATMANI v1
   Hamburger drawer, bottom tab bar, bottom sheet, loading,
   klavye yönetimi, tablo kart dönüşümü.
   Masaüstünde: hepsi erken çıkar (isMobile() guard).
   ============================================================ */
(function () {
  "use strict";
  if (window.__cpeakMProInit) return;
  window.__cpeakMProInit = true;

  /* ---------- yardımcılar ---------- */
  function isMobile() {
    return window.matchMedia && window.matchMedia("(max-width: 900px)").matches;
  }

  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "class") e.className = attrs[k];
      else if (k === "html") e.innerHTML = attrs[k];
      else if (k === "text") e.textContent = attrs[k];
      else if (k.indexOf("on") === 0 && typeof attrs[k] === "function")
        e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    }
    if (children) children.forEach(function (c) { if (c) e.appendChild(c); });
    return e;
  }

  function svgIcon(name) {
    var icons = {
      menu:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="3" y1="7" x2="21" y2="7"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="17" x2="21" y2="17"/></svg>',
      home:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></svg>',
      book:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h11a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3V4z"/><path d="M4 4v13a3 3 0 0 0 3 3h11"/></svg>',
      calendar:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="8" y1="3" x2="8" y2="7"/><line x1="16" y1="3" x2="16" y2="7"/></svg>',
      bell:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>',
      user:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/></svg>',
      logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
      mail:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="3 7 12 13 21 7"/></svg>',
      panel:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>'
    };
    return icons[name] || icons.panel;
  }

  /* Bağlantıya uygun ikon seç */
  function ikonSec(href, text) {
    var h = (href || "").toLowerCase();
    var t = (text || "").toLowerCase();
    if (h.indexOf("dashboard") !== -1 || t.indexOf("panel") !== -1) return "home";
    if (h.indexOf("odev") !== -1 || t.indexOf("ödev") !== -1) return "book";
    if (h.indexOf("program") !== -1 || t.indexOf("program") !== -1) return "calendar";
    if (h.indexOf("bildirim") !== -1 || t.indexOf("bildirim") !== -1) return "bell";
    if (h.indexOf("mail") !== -1 || t.indexOf("mail") !== -1) return "mail";
    if (h.indexOf("logout") !== -1 || t.indexOf("çıkış") !== -1) return "logout";
    return "panel";
  }

  /* ========================================================
     1) HAMBURGER + DRAWER
     ======================================================== */
  function drawerKur() {
    var nav = document.querySelector(".topbar-nav");
    var inner = document.querySelector(".topbar-inner");
    if (!nav || !inner) return;   /* login gibi sayfalarda yok */
    document.body.classList.add("mpro-has-nav");

    /* Hamburger */
    if (!document.querySelector(".mpro-hamburger")) {
      var hb = el("button", {
        class: "mpro-hamburger",
        "aria-label": "Menüyü aç",
        type: "button",
        html: svgIcon("menu")
      });
      hb.addEventListener("click", function (e) {
        e.preventDefault();
        document.body.classList.toggle("mpro-drawer-open");
      });
      inner.insertBefore(hb, inner.firstChild);
    }

    /* Backdrop */
    if (!document.querySelector(".mpro-backdrop")) {
      var bd = el("div", { class: "mpro-backdrop" });
      bd.addEventListener("click", function () {
        document.body.classList.remove("mpro-drawer-open");
        document.body.classList.remove("mpro-sheet-open");
      });
      document.body.appendChild(bd);
    }

    /* Drawer */
    if (!document.querySelector(".mpro-drawer")) {
      var dr = el("aside", { class: "mpro-drawer", role: "navigation" });

      /* Başlık: marka */
      var head = el("div", { class: "mpro-drawer-head" }, [
        el("img", { src: "/static/logochrome.png", alt: "C-Peak" }),
        el("span", { class: "mpro-drawer-title", html: "C-Peak<span class=\"mpro-drawer-sub\">English</span>" })
      ]);
      dr.appendChild(head);

      /* Nav linkleri */
      var links = nav.querySelectorAll("a, button");
      links.forEach(function (a) {
        if (a.classList.contains("topbar-brand")) return;
        var copy = el("a", {
          href: a.getAttribute("href") || "#",
          class: a.className && a.className.indexOf("active") !== -1 ? "mpro-active" : ""
        });
        var ik = ikonSec(a.getAttribute("href") || "", a.textContent || "");
        copy.innerHTML = svgIcon(ik) + "<span>" + (a.textContent || "").trim() + "</span>";
        if (a.tagName === "BUTTON") {
          copy = el("button", { class: "mpro-drawer-item", type: "button" });
          copy.innerHTML = svgIcon(ik) + "<span>" + (a.textContent || "").trim() + "</span>";
          copy.addEventListener("click", function () { a.click(); });
        }
        dr.appendChild(copy);
      });

      /* Ayraç + çıkış */
      dr.appendChild(el("div", { class: "mpro-drawer-sep" }));
      var cikis = nav.querySelector("[data-logout], [href*='logout'], [href*='cikis']");
      if (cikis) {
        var c = el("a", { href: cikis.getAttribute("href") || "#", class: "mpro-drawer-item" });
        c.innerHTML = svgIcon("logout") + "<span>Çıkış Yap</span>";
        dr.appendChild(c);
      }

      document.body.appendChild(dr);
    }
  }

  /* ========================================================
     2) BOTTOM TAB BAR
     ======================================================== */
  function tabbarKur() {
    var nav = document.querySelector(".topbar-nav");
    if (!nav) return;
    var links = Array.from(nav.querySelectorAll("a")).filter(function (a) {
      return a.getAttribute("href") && a.getAttribute("href") !== "#";
    });
    /* En fazla 4 link al */
    if (!links.length) return;
    var secili = links.slice(0, 4);

    /* Zaten var mı? */
    if (document.querySelector(".mpro-tabbar")) {
      document.body.classList.add("mpro-has-tab");
      return;
    }

    var cur = (location.pathname || "/").replace(/\/$/, "");
    var tb = el("nav", { class: "mpro-tabbar", role: "navigation" });
    var inner = el("div", { class: "mpro-tabbar-inner" });

    secili.forEach(function (a) {
      var href = a.getAttribute("href");
      var text = (a.textContent || "").trim();
      var ik = ikonSec(href, text);
      var aktif = href && href !== "#" && (cur === href.replace(/\/$/, "") ||
                                          cur.indexOf(href.replace(/\/$/, "")) === 0);
      var tab = el("a", {
        href: href,
        class: "mpro-tab" + (aktif && text ? " mpro-active" : ""),
        html: svgIcon(ik) + "<span>" + text + "</span>"
      });
      inner.appendChild(tab);
    });

    tb.appendChild(inner);
    document.body.appendChild(tb);
    document.body.classList.add("mpro-has-tab");
  }

  /* ========================================================
     3) MODAL → BOTTOM SHEET
     ======================================================== */
  function sheetKur() {
    var modals = document.querySelectorAll(".modal");
    if (!modals.length) return;
    modals.forEach(function (m) {
      var card = m.querySelector(".modal-card");
      if (!card) return;
      if (!card.querySelector(".mpro-sheet-handle")) {
        var h = el("div", { class: "mpro-sheet-handle" });
        card.insertBefore(h, card.firstChild);
      }
    });

    /* hidden değişimini izle → body.mpro-sheet-open toggle */
    var mo = new MutationObserver(function () {
      var acik = false;
      modals.forEach(function (m) {
        if (!m.hasAttribute("hidden")) acik = true;
      });
      document.body.classList.toggle("mpro-sheet-open", acik);
    });
    modals.forEach(function (m) {
      mo.observe(m, { attributes: true, attributeFilter: ["hidden"] });
    });
  }

  /* ========================================================
     4) TABLO → KART (otomatik data-mpro-card)
     ======================================================== */
  function tabloKur() {
    var tablolar = document.querySelectorAll(".table-wrap table, .table");
    tablolar.forEach(function (t) {
      if (t.hasAttribute("data-mpro-card")) return;
      var basliklar = Array.from(t.querySelectorAll("thead th")).map(function (th) {
        return (th.textContent || "").trim();
      });
      if (!basliklar.length) return;
      /* Çok küçük tablolar (1-2 sütun) karta gerek yok */
      if (basliklar.length <= 2) return;

      t.setAttribute("data-mpro-card", "1");
      var satirlar = t.querySelectorAll("tbody tr");
      satirlar.forEach(function (tr) {
        var tds = tr.querySelectorAll("td");
        tds.forEach(function (td, i) {
          if (!td.hasAttribute("data-label") && basliklar[i]) {
            td.setAttribute("data-label", basliklar[i]);
          }
        });
      });
    });
  }

  /* ========================================================
     5) FORM LOADING STATE
     ======================================================== */
  function formLoadingKur() {
    document.addEventListener("submit", function (e) {
      var f = e.target;
      if (!f || f.tagName !== "FORM") return;
      var btn = f.querySelector("button[type='submit'], .btn-primary[type='submit']");
      if (btn && !btn.classList.contains("mpro-loading")) {
        btn.classList.add("mpro-loading");
        /* 8sn sonra otomatik kaldır (hata vs.) */
        setTimeout(function () { btn.classList.remove("mpro-loading"); }, 8000);
      }
    }, true);
  }

  /* ========================================================
     6) iOS KLAVYE — focus'ta scrollIntoView
     ======================================================== */
  function klavyeKur() {
    document.addEventListener("focusin", function (e) {
      var t = e.target;
      if (!t || !isMobile()) return;
      if (t.tagName !== "INPUT" && t.tagName !== "SELECT" && t.tagName !== "TEXTAREA") return;
      setTimeout(function () {
        try { t.scrollIntoView({ block: "center", behavior: "smooth" }); }
        catch (err) { t.scrollIntoView(); }
      }, 240);
    });
  }

  /* ========================================================
     7) RESIZE — mobil ↔ masaüstü geçişinde temizlik
     ======================================================== */
  function resizeTemizle() {
    var sonMobil = isMobile();
    window.addEventListener("resize", function () {
      var simdi = isMobile();
      if (simdi === sonMobil) return;
      sonMobil = simdi;
      if (!simdi) {
        /* Masaüstüne geçti: drawer/sheet açık kalmasın */
        document.body.classList.remove("mpro-drawer-open");
        document.body.classList.remove("mpro-sheet-open");
      }
    });
  }

  /* ---------- BAŞLAT ---------- */
  function baslat() {
    if (!isMobile()) { resizeTemizle(); return; }
    drawerKur();
    tabbarKur();
    sheetKur();
    tabloKur();
    formLoadingKur();
    klavyeKur();
    resizeTemizle();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(baslat, 60); });
  } else {
    setTimeout(baslat, 60);
  }
  /* Bazı bileşenler geç yüklenebilir */
  setTimeout(function () { if (isMobile()) { tabbarKur(); tabloKur(); sheetKur(); } }, 500);
  setTimeout(function () { if (isMobile()) { tabbarKur(); tabloKur(); } }, 1400);

  /* Sayfa değişimi (tam sayfa reload yoksa) */
  window.addEventListener("pageshow", function () {
    if (isMobile()) { setTimeout(function(){ tabbarKur(); }, 100); }
  });
})();
'''


# ============================================================
# BASE.HTML PATCH
# ============================================================
def base_patchle(html: str) -> str:
    """base.html'e CSS+JS satırlarını idempotent olarak ekler."""
    css_tag = f'<link rel="stylesheet" href="{{{{ url_for(\'static\', filename=\'mobil_pro.css\') }}}}?v={MARKER}">'
    js_tag  = f'<script src="{{{{ url_for(\'static\', filename=\'mobil_pro.js\') }}}}?v={MARKER}" defer></script>'

    if "mobil_pro.css" not in html:
        # </head> öncesine ekle
        idx = html.rfind("</head>")
        if idx == -1:
            raise RuntimeError("base.html'de </head> bulunamadı")
        html = html[:idx] + css_tag + "\n" + html[idx:]

    if "mobil_pro.js" not in html:
        # </body> öncesine ekle
        idx = html.rfind("</body>")
        if idx == -1:
            raise RuntimeError("base.html'de </body> bulunamadı")
        html = html[:idx] + js_tag + "\n" + html[idx:]

    return html


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

    rels = []
    for y in yollar:
        try: rels.append(str(y.resolve().relative_to(kok)))
        except ValueError: pass
    if not rels: print("[GIT] repo dışı — atlandı."); return False

    print(f"[GIT] Repo: {kok}")
    for r in rels: print(f"[GIT] + {r}")

    if git_calistir(kok, "add", *rels).returncode != 0:
        print("[GIT] add başarısız."); return False
    if git_calistir(kok, "diff", "--cached", "--quiet", sessiz=True).returncode == 0:
        print("[GIT] Değişiklik yok."); return False
    if git_calistir(kok, "commit", "-m", COMMIT_MSG).returncode != 0:
        print("[GIT] commit başarısız."); return False
    if git_calistir(kok, "push").returncode != 0:
        print("[GIT] UYARI: push başarısız. Commit yerelde kaldı."); return False
    print("[GIT] ✓ commit + push tamam."); return True


# ============================================================
# ANA
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not BASE.exists():
        print(f"[HATA] {BASE} bulunamadı."); sys.exit(1)

    html = BASE.read_text(encoding="utf-8")
    print(f"[OK] base.html okundu ({len(html)} karakter)")

    zaten_var = "mobil_pro.css" in html and "mobil_pro.js" in html
    if zaten_var:
        print("[BİLGİ] base.html zaten bağlı — sadece CSS/JS içerikleri güncellenecek.")

    if args.dry_run:
        print("[DRY-RUN] Yazılmadı.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1) Yedekler
    yedek_base = YED_DIR / f"base.html.{stamp}.bak"
    shutil.copy2(BASE, yedek_base)
    print(f"[YEDEK] {yedek_base.relative_to(KOK)}")

    # 2) CSS/JS yaz
    STATIC.mkdir(parents=True, exist_ok=True)
    if CSS_YOL.exists():
        shutil.copy2(CSS_YOL, YED_DIR / f"mobil_pro.css.{stamp}.bak")
    if JS_YOL.exists():
        shutil.copy2(JS_YOL, YED_DIR / f"mobil_pro.js.{stamp}.bak")
    CSS_YOL.write_text(CSS_ICERIK, encoding="utf-8")
    JS_YOL.write_text(JS_ICERIK, encoding="utf-8")
    print(f"[YAZILDI] {CSS_YOL.relative_to(KOK)}  ({len(CSS_ICERIK)} byte)")
    print(f"[YAZILDI] {JS_YOL.relative_to(KOK)}   ({len(JS_ICERIK)} byte)")

    # 3) base.html patch (idempotent)
    try:
        yeni = base_patchle(html)
    except Exception as e:
        print(f"[HATA] base.html patch: {e}"); sys.exit(1)

    if yeni != html:
        BASE.write_text(yeni, encoding="utf-8")
        print(f"[OK] base.html güncellendi ({len(yeni)} karakter)")
    else:
        print("[OK] base.html değişmedi (zaten bağlı)")

    # 4) Git
    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(BASE, CSS_YOL, JS_YOL)

    print("\nBitti. Şimdi:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) Masaüstünde gez → hiçbir şey değişmemiş olmalı")
    print("  3) Mobilde gez:")
    print("     • Üstte hamburger çıkacak (panel sayfalarında)")
    print("     • Altta role göre tab bar")
    print("     • Tablolar kart görünümünde")
    print("     • Modallar alttan yukarı açılıyor")
    print("     • Butonlarda basma animasyonu var")
    print("     • Form submit'te spinner")


if __name__ == "__main__":
    main()