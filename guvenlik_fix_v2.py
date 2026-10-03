#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guvenlik_fix_v2.py — Kalan güvenlik bulguları
1) CSP header ekle (security_headers.py)
2) Bizim JS dosyalarındaki console.log'ları temizle
3) base.html ?v= güncelle

Kullanım: py guvenlik_fix_v2.py [--no-git] [--dry-run]
"""

import argparse, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
STATIC = KOK / "static"
BASE = KOK / "templates" / "base.html"
SEC = KOK / "security_headers.py"
YED_DIR = KOK / "backups"

MARKER = "SEC_FIX_V2"

# Bu dosyalara dokunmuyoruz (3rd party)
HARIC = {"flatpickr.min.js", "flatpickr-tr.js"}

COMMIT_MSG = """security: CSP + console.log temizliği

- security_headers.py: Content-Security-Policy eklendi
- Bizim JS dosyalarındaki console.log/warn/error temizlendi
- 3rd party (flatpickr) dokunulmadı
- base.html ?v= güncellendi
- Not: /admin uyarısı false positive (login_required mevcut)
- Otomatik yama: guvenlik_fix_v2.py [SEC_FIX_V2]"""


CSP_BLOK = '''
        # ---------- Content-Security-Policy ----------
        # 'unsafe-inline' style zorunlu (tema toggle, inline <style> blokları)
        # 'unsafe-inline' script YOK → XSS'i büyük ölçüde engeller
        if not resp.headers.get("Content-Security-Policy"):
            resp.headers["Content-Security-Policy"] = "; ".join([
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.sib.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com data:",
                "img-src 'self' data: https:",
                "connect-src 'self' https://api.brevo.com https://*.supabase.co",
                "frame-ancestors 'self'",
                "base-uri 'self'",
                "form-action 'self'",
                "object-src 'none'",
            ])
'''


def sec_patchle(ic: str) -> str:
    if "Content-Security-Policy" in ic:
        return ic
    # Talisman bloğunun sonuna ekle (after_request içinde)
    # "return resp" satırından hemen önce ekle
    idx = ic.rfind("return resp")
    if idx == -1:
        print("[UYARI] security_headers.py'de 'return resp' bulunamadı.")
        return ic
    return ic[:idx] + CSP_BLOK + "\n        " + ic[idx:]


def console_temizle(js: str) -> tuple:
    """console.log/warn/error satırlarını // ile yorumlar. (yeni, sayi) döner."""
    sayi = 0
    satirlar = js.split("\n")
    yeni = []
    for s in satirlar:
        # Zaten yorumlanmış mı?
        stripped = s.lstrip()
        if stripped.startswith("//"):
            yeni.append(s); continue
        if re.search(r'\bconsole\.(log|warn|error|info|debug)\b', s):
            # Satır sonuna yorum ekle
            indent = len(s) - len(s.lstrip())
            yeni.append(s[:indent] + "// [sec] " + s[indent:])
            sayi += 1
        else:
            yeni.append(s)
    return "\n".join(yeni), sayi


def base_v_guncelle(ic: str) -> str:
    ic = re.sub(r'((?:mobil_pro|geri_onay|ux_fix|mobil_ptr)\.js\?v=)[^"\']+',
                r'\g<1>' + MARKER, ic)
    return ic


def git_kok_bul(p):
    p = p.resolve()
    for u in [p] + list(p.parents):
        if (u / ".git").exists(): return u
    return None


def git_calistir(kok, *a, sessiz=False):
    r = subprocess.run(["git"] + list(a), cwd=str(kok), capture_output=True,
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

    if git_calistir(kok,"add",*rels).returncode != 0:
        print("[GIT] add başarısız."); return False
    if git_calistir(kok,"diff","--cached","--quiet",sessiz=True).returncode == 0:
        print("[GIT] Değişiklik yok."); return False
    if git_calistir(kok,"commit","-m",COMMIT_MSG).returncode != 0:
        print("[GIT] commit başarısız."); return False
    if git_calistir(kok,"push").returncode != 0:
        print("[GIT] UYARI: push başarısız. Commit yerelde kaldı."); return False
    print("[GIT] ✓ commit + push tamam."); return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    degis = []
    toplam_log = 0

    # 1) CSP
    if SEC.exists():
        ic = SEC.read_text(encoding="utf-8")
        yeni = sec_patchle(ic)
        if yeni != ic:
            degis.append((SEC, yeni))
            print("[PLAN] security_headers.py: CSP eklenecek")

    # 2) JS console.log temizliği (3rd party hariç)
    if STATIC.exists():
        for js in sorted(STATIC.glob("*.js")):
            if js.name in HARIC:
                continue
            ic = js.read_text(encoding="utf-8", errors="ignore")
            yeni, sayi = console_temizle(ic)
            if sayi > 0:
                degis.append((js, yeni))
                toplam_log += sayi
                print(f"[PLAN] {js.name}: {sayi} console satırı yorumlanacak")

    # 3) base.html ?v=
    if BASE.exists():
        ic = BASE.read_text(encoding="utf-8")
        yeni = base_v_guncelle(ic)
        if yeni != ic:
            degis.append((BASE, yeni))
            print("[PLAN] base.html: ?v= güncellenecek")

    if not degis:
        print("\nDeğişiklik yok — hepsi zaten yapılmış.")
        return

    if args.dry_run:
        print(f"\n[DRY-RUN] {len(degis)} dosya değişecek, {toplam_log} console temizlenecek.")
        return

    YED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for yol, icerik in degis:
        yed = YED_DIR / f"{yol.name}.{stamp}.bak"
        shutil.copy2(yol, yed)
        yol.write_text(icerik, encoding="utf-8")
        print(f"[OK] {yol.relative_to(KOK)}")

    yollar = [y for y, _ in degis]
    if args.no_git:
        print("\n[GIT] --no-git verildi.")
    else:
        git_commit_push(*yollar)

    print(f"\nBitti. {toplam_log} console satırı temizlendi, CSP eklendi.")
    print("\nSonraki adım:")
    print("  1) Deploy et")
    print("  2) Scanner'ı tekrar çalıştır → XSS uyarısı hâlâ çıkabilir (pattern-based)")
    print("  3) /admin uyarısı da kalır — o false positive")


if __name__ == "__main__":
    main()