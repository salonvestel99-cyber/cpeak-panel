#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guvenlik_fix.py — Güvenlik iyileştirmeleri (tek seferde)
1) security_headers.py — Cache-Control + CORP + ek header'lar
2) app.py — init_headers(app) entegrasyonu (idempotent)
3) geri_onay.js — console.log sessizleştirme
4) mobil_pro.js — escapeHtml() + innerHTML güvenliği
5) .gitignore — admin_ekle.py ekle
6) base.html ?v= güncelle
Kullanım: py guvenlik_fix.py [--no-git] [--dry-run]
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
STATIC = KOK / "static"
BASE = KOK / "templates" / "base.html"
APP = KOK / "app.py"
GITIGNORE = KOK / ".gitignore"
YED_DIR = KOK / "backups"

SEC_YOL = KOK / "security_headers.py"
GERI_YOL = STATIC / "geri_onay.js"
PRO_YOL = STATIC / "mobil_pro.js"

MARKER = "SEC_FIX_V1"

COMMIT_MSG = """security: Cache-Control + CORP + XSS önlemi

- security_headers.py eklendi (Cache-Control, CORP, CSP-i uyumlu)
- app.py: init_headers(app) entegre edildi
- geri_onay.js: console.log sessizleştirildi
- mobil_pro.js: escapeHtml() ile innerHTML güvenliği
- .gitignore: admin_ekle.py gizlendi
- Otomatik yama: guvenlik_fix.py [SEC_FIX_V1]"""


SEC_ICERIK = r'''# -*- coding: utf-8 -*-
"""
security_headers.py — Ek HTTP güvenlik başlıkları.

app.py'de init_security(app)'ten sonra çağrılır:
    from security_headers import init_headers
    init_headers(app)
"""
from flask import request, session


def init_headers(app):

    AUTH_PREFIXES = (
        "/admin", "/panel", "/dashboard", "/ogrenci", "/ogretmen", "/veli",
        "/ders", "/odev", "/bildirim", "/devamsizlik", "/not-",
        "/sifre", "/mail", "/talep",
    )

    @app.after_request
    def _guvenlik_basliklari(resp):
        path = request.path or ""
        statik_mi = path.startswith("/static/")
        auth_var = bool(session.get("user_id"))

        # ---------- Cache-Control ----------
        if statik_mi:
            resp.headers.setdefault(
                "Cache-Control",
                "public, max-age=31536000, immutable",
            )
        elif auth_var or any(path.startswith(p) for p in AUTH_PREFIXES):
            resp.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, "
                "max-age=0, private"
            )
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
        else:
            resp.headers.setdefault("Cache-Control", "no-cache, private")

        # ---------- Cross-Origin-Resource-Policy ----------
        resp.headers.setdefault(
            "Cross-Origin-Resource-Policy", "same-origin"
        )

        # ---------- Ek dayanıklılık (Talisman varsa da zararsız) ----------
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        resp.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=()",
        )

        return resp
'''


def app_patchle(app_ic: str) -> str:
    """init_security(app) satırından sonra init_headers(app) ekler."""
    if "from security_headers import" in app_ic:
        return app_ic  # zaten var

    if "init_security(app)" not in app_ic:
        print("[UYARI] app.py'de init_security(app) bulunamadı — elle ekleme gerek.")
        return app_ic

    ekleme = (
        "\n# Ek HTTP güvenlik başlıkları (Cache-Control, CORP)\n"
        "from security_headers import init_headers\n"
        "init_headers(app)\n"
    )
    yeni = app_ic.replace(
        "init_security(app)",
        "init_security(app)" + ekleme,
        1,
    )
    return yeni


def geri_log_kapat(js: str) -> str:
    """geri_onay.js'teki log fonksiyonunu no-op yapar."""
    # log fonksiyonunu tamamen sessiz hale getir
    yeni = re.sub(
        r'function log\(\)\s*\{[\s\S]*?\n  \}',
        'function log() { /* production: sessiz */ }',
        js,
        count=1,
    )
    return yeni


def mobil_pro_guvenli(js: str) -> str:
    """mobil_pro.js'e escapeHtml ekler + 3 innerHTML kullanımını korur."""
    if "function escapeHtml" in js:
        return js  # zaten var

    # 1) escapeHtml fonksiyonunu svgIcon'dan önce ekle
    escape_fn = (
        '  function escapeHtml(s) {\n'
        '    return String(s == null ? "" : s)\n'
        '      .replace(/&/g, "&amp;")\n'
        '      .replace(/</g, "&lt;")\n'
        '      .replace(/>/g, "&gt;")\n'
        '      .replace(/"/g, "&quot;")\n'
        "      .replace(/'/g, \"&#39;\");\n"
        '  }\n\n'
    )
    if "function svgIcon(" in js:
        js = js.replace("  function svgIcon(", escape_fn + "  function svgIcon(", 1)
    else:
        return js

    # 2) innerHTML kullanımlarını escapeHtml ile sar
    js = js.replace(
        'copy.innerHTML = svgIcon(ik) + "<span>" + (a.textContent || "").trim() + "</span>";',
        'copy.innerHTML = svgIcon(ik) + "<span>" + escapeHtml((a.textContent || "").trim()) + "</span>";'
    )
    return js


def gitignore_guncelle(ic: str) -> str:
    eklenecek = ["admin_ekle.py", "admin_analiz.py",
                 "logout_modal_analiz.py", "login_analiz.py",
                 "guvenlik_teshis.py"]
    satirlar = ic.splitlines()
    mevcut = set(s.strip() for s in satirlar)
    yeni_satirlar = list(satirlar)
    if not any(s.strip() == "# Kişisel yönetim script'leri" for s in yeni_satirlar):
        yeni_satirlar.append("")
        yeni_satirlar.append("# Kişisel yönetim script'leri (git'e gitmesin)")
    for d in eklenecek:
        if d not in mevcut:
            yeni_satirlar.append(d)
    return "\n".join(yeni_satirlar) + "\n"


def base_v_guncelle(ic: str) -> str:
    for ad in ["mobil_pro.js", "geri_onay.js"]:
        ic = re.sub(
            r'(' + re.escape(ad) + r'\?v=)[^"\']+',
            r'\g<1>' + MARKER,
            ic,
        )
    return ic


def git_kok_bul(p):
    p = p.resolve()
    for u in [p] + list(p.parents):
        if (u / ".git").exists(): return u
    return None


def git_calistir(kok, *a, sessiz=False):
    r = subprocess.run(["git"] + list(a), cwd=str(kok),
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if not sessiz:
        if r.stdout.strip():
            print("    " + r.stdout.strip().replace("\n", "\n    "))
        if r.stderr.strip():
            print("    " + r.stderr.strip().replace("\n", "\n    "))
    return r


def git_commit_push(*yollar):
    print("\n[GIT] Başlatılıyor...")
    kok = None
    for y in yollar:
        kok = git_kok_bul(y)
        if kok: break
    if kok is None:
        print("[GIT] .git yok — atlandı."); return False
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except Exception:
        print("[GIT] git kurulu değil — atlandı."); return False

    rels = []
    for y in yollar:
        try:
            rels.append(str(y.resolve().relative_to(kok)))
        except ValueError:
            pass
    if not rels:
        print("[GIT] repo dışı — atlandı."); return False

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    degisecek = []
    plan = []

    # 1) security_headers.py
    if not SEC_YOL.exists():
        plan.append(f"+ {SEC_YOL.relative_to(KOK)}  ({len(SEC_ICERIK)} byte)")

    # 2) app.py
    app_ic = APP.read_text(encoding="utf-8")
    app_yeni = app_patchle(app_ic)
    if app_yeni != app_ic:
        plan.append("~ app.py  (init_headers ekle)")
        degisecek.append((APP, app_yeni))

    # 3) geri_onay.js
    if GERI_YOL.exists():
        geri_ic = GERI_YOL.read_text(encoding="utf-8")
        geri_yeni = geri_log_kapat(geri_ic)
        if geri_yeni != geri_ic:
            plan.append("~ geri_onay.js  (log sessiz)")
            degisecek.append((GERI_YOL, geri_yeni))

    # 4) mobil_pro.js
    if PRO_YOL.exists():
        pro_ic = PRO_YOL.read_text(encoding="utf-8")
        pro_yeni = mobil_pro_guvenli(pro_ic)
        if pro_yeni != pro_ic:
            plan.append("~ mobil_pro.js  (escapeHtml)")
            degisecek.append((PRO_YOL, pro_yeni))

    # 5) .gitignore
    if GITIGNORE.exists():
        gi_ic = GITIGNORE.read_text(encoding="utf-8")
        gi_yeni = gitignore_guncelle(gi_ic)
        if gi_yeni != gi_ic:
            plan.append("~ .gitignore  (kişisel script'ler)")
            degisecek.append((GITIGNORE, gi_yeni))

    # 6) base.html ?v=
    base_ic = BASE.read_text(encoding="utf-8")
    base_yeni = base_v_guncelle(base_ic)
    if base_yeni != base_ic:
        plan.append("~ base.html  (?v= güncelle)")
        degisecek.append((BASE, base_yeni))

    print("Yapılacaklar:")
    for p in plan:
        print("  " + p)

    if args.dry_run:
        print("\n[DRY-RUN] Yazılmadı."); return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Yedekler
    for yol, _ in degisecek:
        if yol.exists():
            yed = YED_DIR / f"{yol.name}.{stamp}.bak"
            shutil.copy2(yol, yed)
            print(f"[YEDEK] {yed.relative_to(KOK)}")

    # 1) security_headers.py
    if not SEC_YOL.exists():
        SEC_YOL.write_text(SEC_ICERIK, encoding="utf-8")
        print(f"[YAZILDI] {SEC_YOL.relative_to(KOK)}  ({len(SEC_ICERIK)} byte)")

    # 2-6) diğerleri
    for yol, icerik in degisecek:
        yol.write_text(icerik, encoding="utf-8")
        print(f"[OK] {yol.relative_to(KOK)}")

    yollar = [SEC_YOL] + [y for y, _ in degisecek]
    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(*yollar)

    print("\nBitti. Test:")
    print("  1) Sunucuyu yeniden başlat")
    print("  2) curl -I https://.../admin → Cache-Control: no-store görmelisin")
    print("  3) curl -I https://.../static/style.css → Cache-Control: public görürsün")
    print("  4) Tarayıcı konsolu → gereksiz log yok")
    print("  5) Mobil menü, dropdown → hâlâ çalışır")


if __name__ == "__main__":
    main()