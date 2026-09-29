import os, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
YED = os.path.join(KOK, "_backups", "eski_scriptler")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# KORUNACAKLAR
KORU = {
    "app.py",
    "models.py",
    "security.py",
    "run.py",
    "mail_service.py",
    "kur.py",
    "migrator.py",
    "temizle.py",   # kendini silmesin
}

# Bu proje kokunde olup silinecek olanlar
silinecekler = []
for ad in os.listdir(KOK):
    if not ad.endswith(".py"):
        continue
    if ad in KORU:
        continue
    silinecekler.append(ad)

if not silinecekler:
    print("Silinecek py dosyasi yok.")
else:
    print("Silinecek dosyalar:")
    for ad in silinecekler:
        print("  - " + ad)
        # Yedekle
        shutil.copy2(os.path.join(KOK, ad),
                     os.path.join(YED, ad + "." + stamp + ".bak"))
        # Sil
        os.remove(os.path.join(KOK, ad))
    print("")
    print("Toplam " + str(len(silinecekler)) + " dosya silindi.")
    print("Yedekler: _backups/eski_scriptler/")
    print("")
    print("Kalan py dosyalari:")
    for ad in sorted(os.listdir(KOK)):
        if ad.endswith(".py"):
            print("  - " + ad)