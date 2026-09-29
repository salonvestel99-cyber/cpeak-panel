# -*- coding: utf-8 -*-
"""Ders programina Cumartesi ve Pazar gunlerini ekler."""
import os, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(KOK, "app.py")
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

shutil.copy2(APP, os.path.join(YED, f"app.py.{stamp}.bak"))
print(f"[YEDEK] backups/app.py.{stamp}.bak")

with open(APP, "r", encoding="utf-8") as f:
    ac = f.read()

ESKI = 'GUN_ADI = {1: "Pazartesi", 2: "Salı", 3: "Çarşamba", 4: "Perşembe", 5: "Cuma"}'
YENI = 'GUN_ADI = {1: "Pazartesi", 2: "Salı", 3: "Çarşamba", 4: "Perşembe", 5: "Cuma", 6: "Cumartesi", 7: "Pazar"}'

if YENI in ac:
    print("[ATLA] Hafta sonu zaten ekli")
elif ESKI in ac:
    ac = ac.replace(ESKI, YENI, 1)
    with open(APP, "w", encoding="utf-8") as f:
        f.write(ac)
    print("[OK] GUN_ADI'na Cumartesi ve Pazar eklendi")
else:
    print("[UYARI] GUN_ADI tam eslesmedi. Elle kontrol gerek.")
    # Alternatif: kismi eslesme ara
    import re
    m = re.search(r'GUN_ADI\s*=\s*\{[^\}]+\}', ac)
    if m:
        print(f"  Bulunan: {m.group(0)}")

print("""
============================================================
SIMDI:
1. py -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('OK')"
2. git add app.py
3. git commit -m "Ders programina hafta sonu eklendi"
4. git push
5. Telefonda test et: /ders-programi sayfasi
   - 7 gun gorunmeli (Pazartesi-Pazar)
   - Admin olarak /ders-programi/duzenle sayfasinda da 7 gun secilebilmeli
============================================================
""")