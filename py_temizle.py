#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
py_temizle.py — Gereksiz Python dosyalarını arşive taşır.
Silmez — _backups/silinmis_py_YYYYMMDD_HHMMSS/ altına taşır.
Uygulama dosyalarına DOKUNMAZ.

Kullanım:
    py py_temizle.py            # önce dry-run gösterir
    py py_temizle.py --uygula   # gerçekten taşır
    py py_temizle.py --uygula --no-git
"""

import argparse, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
ARSIV = KOK / "_backups" / f"silinmis_py_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# ============================================================
# 1) KORUNACAKLAR — uygulamanın çalışması için kritik
# ============================================================
KORU = {
    # Ana uygulama
    "app.py",
    "models.py",
    "security.py",
    "security_headers.py",
    "mail_service.py",
    "run.py",
    "migrator.py",
    "kur.py",

    # Kişisel yönetim (git'e gitmiyor ama lazım)
    "admin_ekle.py",
    "py_temizle.py",  # kendi kendini de korusun

    # Bu script'in kendisi
    "mobil_pro.py",     # idempotent — ileride güncellemek isteyebilirsin
    "guvenlik_fix.py",  # aynı sebeple
    "guvenlik_fix_v2.py",
}

# ============================================================
# 2) SİLİNECEK — tek seferlik yamalar / analiz script'leri
# ============================================================
# Bu liste elle kontrol edilmiş — hepsi "bir kere çalıştırıldı bitti" tipi.
SIL = {
    # ---- Tek seferlik tema/login yamaları ----
    "cpeak_mobile_login_patch.py",
    "hero_geri_getir.py",
    "login_final.py",
    "login_v9.py",
    "son_temizlik.py",
    "aa.py",

    # ---- Mobil giriş iterasyonları (v2→v11) ----
    "mobil_giris_v2.py",
    "mobil_giris_v3.py",
    "mobil_giris_v4.py",
    "mobil_giris_v5.py",
    "mobil_giris_v6.py",
    "mobil_giris_v7.py",
    "mobil_giris_v8.py",
    "mobil_giris_v9.py",
    "mobil_giris_v10.py",
    "mobil_giris_v11.py",

    # ---- Diğer tek seferlik yamalar ----
    "mobil_ptr.py",
    "mobil_ptr_fix.py",
    "ux_fix.py",
    "geri_onay.py",
    "geri_onay_v2.py",
    "geri_onay_v3.py",
    "geri_onay_v4.py",
    "akiskan_tasarim.py",

    # ---- Analiz / tanı script'leri ----
    "intel.py",
    "site_harita.py",
    "login_analiz.py",
    "admin_analiz.py",
    "logout_modal_analiz.py",
    "guvenlik_teshis.py",
}


# ============================================================
# GIT
# ============================================================
def git_kok_bul(p):
    p = p.resolve()
    for u in [p] + list(p.parents):
        if (u / ".git").exists(): return u
    return None


def git_calistir(kok, *a, sessiz=False):
    r = subprocess.run(["git"] + list(a), cwd=str(kok), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if not sessiz:
        if r.stdout.strip(): print("    " + r.stdout.strip().replace("\n", "\n    "))
        if r.stderr.strip(): print("    " + r.stderr.strip().replace("\n", "\n    "))
    return r


def git_commit_push(yollar):
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
    for r in rels[:20]: print(f"[GIT] + {r}")
    if len(rels) > 20:
        print(f"[GIT] ... +{len(rels)-20} dosya daha")

    if git_calistir(kok, "add", "-A").returncode != 0:
        print("[GIT] add başarısız."); return False
    if git_calistir(kok, "diff", "--cached", "--quiet", sessiz=True).returncode == 0:
        print("[GIT] Değişiklik yok."); return False
    if git_calistir(kok, "commit", "-m",
                    "chore: gereksiz py script'leri temizlendi\n\n"
                    "Tek seferlik yamalar ve analiz script'leri _backups/ altına taşındı.\n"
                    "Uygulama dosyaları (app.py, models.py vs.) dokunulmadı.\n"
                    "Otomatik: py_temizle.py").returncode != 0:
        print("[GIT] commit başarısız."); return False
    if git_calistir(kok, "push").returncode != 0:
        print("[GIT] UYARI: push başarısız. Commit yerelde kaldı."); return False
    print("[GIT] ✓ commit + push tamam."); return True


# ============================================================
# ANA
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uygula", action="store_true",
                    help="Gerçekten taşı (varsayılan: sadece listeler)")
    ap.add_argument("--no-git", action="store_true",
                    help="Git commit/push yapma")
    args = ap.parse_args()

    # Klasördeki tüm py dosyaları
    mevcut = set(p.name for p in KOK.glob("*.py"))
    mevcut.discard("py_temizle.py")

    # Gerçekten var olan + silinecek olanlar
    silinecek = sorted(mevcut & SIL)
    bulunamayan = sorted(SIL - mevcut)

    # Klasörde olup listede olmayan dosyalar (beklenmedik)
    belirsiz = sorted(mevcut - SIL - KORU)

    print("=" * 60)
    print(f"  PY TEMİZLİĞİ ({'UYGULA' if args.uygula else 'DRY-RUN'})")
    print("=" * 60)

    print(f"\n📁 Toplam py dosyası: {len(mevcut)}")
    print(f"🗑  Silinecek       : {len(silinecek)}")
    print(f"✅ Korunacak        : {len(mevcut & KORU)}")
    if belirsiz:
        print(f"❓ Bilinmeyen       : {len(belirsiz)}")
    if bulunamayan:
        print(f"⚠️  Listede olmayan : {len(bulunamayan)}")

    # ---- Silinecek listesi ----
    if silinecek:
        print("\n" + "=" * 60)
        print("  SİLİNECEK (arşive taşınacak)")
        print("=" * 60)
        for f in silinecek:
            boyut = (KOK / f).stat().st_size
            print(f"  🗑  {f:40s}  {boyut:>8} byte")

    # ---- Bilinmeyen ----
    if belirsiz:
        print("\n" + "=" * 60)
        print("  BİLİNMEYEN (silinmeyecek — emin değilim)")
        print("=" * 60)
        for f in belirsiz:
            print(f"  ❓ {f}")

    # ---- Uygula ----
    if not args.uygula:
        print("\n" + "=" * 60)
        print("  DRY-RUN — hiçbir şey taşınmadı.")
        print("  Gerçekten taşımak için: py py_temizle.py --uygula")
        print("=" * 60)
        return

    if not silinecek:
        print("\nSilinecek dosya yok — hepsi temiz zaten.")
        return

    # Arşiv klasörü
    ARSIV.mkdir(parents=True, exist_ok=True)
    print(f"\n📦 Arşiv: {ARSIV.relative_to(KOK)}")

    tasinan = []
    for f in silinecek:
        kaynak = KOK / f
        hedef = ARSIV / f
        try:
            shutil.move(str(kaynak), str(hedef))
            tasinan.append(f)
            print(f"  ✓ {f}")
        except Exception as e:
            print(f"  ✗ {f} — {e}")

    print(f"\n✅ {len(tasinan)} dosya arşive taşındı.")

    # Git
    if args.no_git:
        print("[GIT] --no-git verildi, atlandı.")
    else:
        yollar = [KOK / f for f in tasinan] + [ARSIV]
        git_commit_push(yollar)

    print("\nGeri almak istersen:")
    print(f"  copy {ARSIV.relative_to(KOK)}\\DOSYA.py .")
    print("\nYa da topluca:")
    print(f"  copy {ARSIV.relative_to(KOK)}\\*.py .")


if __name__ == "__main__":
    main()