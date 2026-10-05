# -*- coding: utf-8 -*-
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
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", metin, re.DOTALL)
    if not m:
        return {}, metin
    fm, body = m.group(1), m.group(2)
    meta = {}
    for satir in fm.split("\n"):
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
        parcalar = [p.strip() for p in metin.split("\n\n") if p.strip()]
        return "\n".join(f"<p>{p}</p>" for p in parcalar)
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
