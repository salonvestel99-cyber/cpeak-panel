# -*- coding: utf-8 -*-
"""Projedeki tum mail adreslerini cpeakenglish@gmail.com ile degistirir."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

YENI_MAIL = "cpeakenglish@gmail.com"

# Taranacak uzantilar
UZANTILAR = (".html", ".py", ".js", ".css", ".md", ".txt", ".json", ".example", ".env")
ATLA_KLASOR = {"__pycache__", ".git", "node_modules", ".venv", "venv",
               "backups", "_backups", "logs", "migrations"}

# Placeholder/test mailler - bunlara DOKUNMA
ATLA_MAIL = {
    "ornek@mail.com", "example@example.com", "test@test.com",
    "noreply@example.com", "user@example.com", "you@example.com",
    "your@email.com", "sizinmail@gmail.com", "seninmail@gmail.com",
    "mail@mail.com", "a@a.com",
}

MAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

toplam_degisiklik = 0
etkilenen_dosyalar = []
bulunan_mailler = {}

for kok, klasorler, dosyalar in os.walk(KOK):
    klasorler[:] = [k for k in klasorler if k not in ATLA_KLASOR]

    for ad in dosyalar:
        if not ad.endswith(UZANTILAR):
            continue
        yol = os.path.join(kok, ad)
        try:
            with open(yol, "r", encoding="utf-8") as f:
                icerik = f.read()
        except (UnicodeDecodeError, OSError):
            continue

        # Bu dosyadaki tum mailleri bul
        bulunanlar = set(MAIL_RE.findall(icerik))
        # Sadece degistirilecekleri filtrele
        degistirilecekler = {m for m in bulunanlar
                             if m.lower() != YENI_MAIL.lower()
                             and m.lower() not in ATLA_MAIL}

        if not degistirilecekler:
            continue

        # Yedek al (sadece ilk degisiklikte)
        rel = os.path.relpath(yol, KOK).replace("\\", "_").replace("/", "_")
        shutil.copy2(yol, os.path.join(YED, f"{rel}.{stamp}.bak"))

        # Degistir
        yeni_icerik = icerik
        for eski_mail in degistirilecekler:
            # Placeholder veya zaten yeni ise atla
            yeni_icerik = yeni_icerik.replace(eski_mail, YENI_MAIL)
            bulunan_mailler.setdefault(eski_mail, []).append(
                os.path.relpath(yol, KOK))
            toplam_degisiklik += 1

        if yeni_icerik != icerik:
            with open(yol, "w", encoding="utf-8") as f:
                f.write(yeni_icerik)
            etkilenen_dosyalar.append(os.path.relpath(yol, KOK))

# RAPOR
print("=" * 60)
print("MAIL DEGISIKLIK RAPORU")
print("=" * 60)
if not bulunan_mailler:
    print("\nHicbir mail adresi bulunamadi veya hepsi zaten dogru.")
else:
    print(f"\nYeni adres: {YENI_MAIL}\n")
    print("Bulunan ve degistirilen mail adresleri:")
    for mail, dosyalar in sorted(bulunan_mailler.items()):
        print(f"\n  {mail}")
        for d in sorted(set(dosyalar)):
            print(f"    -> {d}")

print(f"\nToplam degisiklik : {toplam_degisiklik}")
print(f"Etkilenen dosya   : {len(etkilenen_dosyalar)}")

if etkilenen_dosyalar:
    print("\nEtkilenen dosyalar:")
    for d in sorted(etkilenen_dosyalar):
        print(f"  - {d}")

print("""
============================================================
SIMDI YAPILACAKLAR
============================================================

1) SYNTAX KONTROLU (py dosyalari icin):
   py -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('OK')"
   py -c "import ast; ast.parse(open('mail_service.py', encoding='utf-8').read()); print('OK')"

2) PUSH ET:
   git add .
   git commit -m "Tum mail adresleri cpeakenglish@gmail.com yapildi"
   git push

3) RENDER'DA ENV DEGISKENI:
   Render -> cpeak-panel -> Environment:
     MAIL_DEFAULT_SENDER = cpeakenglish@gmail.com
   Save -> deploy bekle

4) BREVO'DA SENDER DOGRULAMASI:
   Brevo -> Senders, Domains & IPs -> Senders
   "Add a sender":
     From name  : C-Peak Panel
     From email : cpeakenglish@gmail.com
   Gmail'e gelen onay linkine tikla.

5) TEST:
   https://cpeak-panel.onrender.com/admin/test-email
   Kendi Gmail adresini yaz -> Gonder

============================================================
""")