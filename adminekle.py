#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
admin_ekle.py — Yeni yönetici (admin) ekler.

Kullanım:
    py admin_ekle.py                          # interaktif sorar
    py admin_ekle.py 12345678901 "Ali Veli" "sifre123"
    py admin_ekle.py 12345678901 "Ali Veli" "sifre123" "ali@mail.com"

Var olan TC'yi güncellemez — sadece yeni kayıt ekler.
"""

import os
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
os.chdir(KOK)

# .env yükle
try:
    from dotenv import load_dotenv
    load_dotenv(KOK / ".env")
except ImportError:
    print("[UYARI] python-dotenv yok. Ortam değişkenleri elle ayarlanmalı.")

# models.get_db kullan (PostgreSQL bağlantısı orada)
try:
    from models import get_db
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"[HATA] import başarısız: {e}")
    print("       requirements.txt kurulu mu? Sanal ortam aktif mi?")
    sys.exit(1)


def mevcut_mu(conn, tc):
    row = conn.execute("SELECT id, name, role FROM users WHERE tc_no = ?", (tc,)).fetchone()
    return row


def admin_ekle(tc, isim, sifre, email=None):
    tc = tc.strip()
    isim = isim.strip()

    if not tc.isdigit() or len(tc) != 11:
        print(f"[HATA] TC 11 haneli rakam olmalı. Verilen: {tc}")
        return False
    if not isim:
        print("[HATA] İsim boş olamaz.")
        return False
    if not sifre or len(sifre) < 6:
        print("[HATA] Şifre en az 6 karakter olmalı.")
        return False

    conn = get_db()
    try:
        var = mevcut_mu(conn, tc)
        if var:
            print(f"[ATLA] Bu TC zaten kayıtlı:")
            print(f"       → id={var['id']}  name={var['name']}  role={var['role']}")
            print(f"       Yeni kayıt eklenmedi.")
            return False

        pw_hash = generate_password_hash(sifre)
        conn.execute(
            "INSERT INTO users (tc_no, password_hash, name, role, student_id, email) "
            "VALUES (?, ?, ?, 'admin', NULL, ?)",
            (tc, pw_hash, isim, email or None)
        )
        conn.commit()

        print()
        print("=" * 50)
        print("  ✓ YENİ YÖNETİCİ EKLENDİ")
        print("=" * 50)
        print(f"  T.C.   : {tc}")
        print(f"  İsim   : {isim}")
        print(f"  Rol    : admin")
        if email:
            print(f"  E-posta: {email}")
        print(f"  Şifre  : (girilen şifre)")
        print("=" * 50)
        return True
    finally:
        conn.close()


def interaktif():
    print("=" * 50)
    print("  YENİ YÖNETİCİ EKLE")
    print("=" * 50)
    tc = input("T.C. Kimlik No (11 hane): ").strip()
    isim = input("Ad Soyad              : ").strip()
    sifre = input("Şifre (min 6)         : ").strip()
    email = input("E-posta (opsiyonel)   : ").strip() or None
    return tc, isim, sifre, email


def main():
    if len(sys.argv) == 1:
        tc, isim, sifre, email = interaktif()
    elif len(sys.argv) >= 4:
        tc = sys.argv[1]
        isim = sys.argv[2]
        sifre = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else None
    else:
        print("Kullanım:")
        print('  py admin_ekle.py')
        print('  py admin_ekle.py 12345678901 "Ali Veli" "sifre123"')
        print('  py admin_ekle.py 12345678901 "Ali Veli" "sifre123" "ali@mail.com"')
        sys.exit(1)

    basarili = admin_ekle(tc, isim, sifre, email)
    sys.exit(0 if basarili else 1)


if __name__ == "__main__":
    main()