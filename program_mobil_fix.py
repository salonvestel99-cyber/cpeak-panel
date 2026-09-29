# -*- coding: utf-8 -*-
"""Ders programi tablosuna ozel mobil duzeltme."""
import os

KOK = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(KOK, "static", "mobile.css")

EKLENTI = '''

/* ============================================================
   DERS PROGRAMI TABLOSU - MOBIL OZEL
   ============================================================ */
@media (max-width: 768px) {

  /* Sarmalayici: yatay kaydirma */
  .table-wrap {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -14px !important;
    padding: 0 14px !important;
  }

  /* Ders programi tablosu */
  table.ders-programi-tablo {
    display: table !important;
    width: auto !important;
    min-width: 560px !important;
    table-layout: fixed !important;
    border-collapse: separate !important;
    border-spacing: 4px !important;
  }

  /* Header satiri */
  table.ders-programi-tablo thead {
    display: table-header-group !important;
  }

  table.ders-programi-tablo thead th {
    font-size: 0.72rem !important;
    padding: 6px 4px !important;
    text-align: center !important;
    white-space: nowrap !important;
    background: var(--card, #fff) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 2 !important;
  }

  /* Saat sutunu - sabit kalsin */
  table.ders-programi-tablo th:first-child,
  table.ders-programi-tablo td.saat-cell {
    width: 46px !important;
    min-width: 46px !important;
    max-width: 46px !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-align: center !important;
    padding: 8px 2px !important;
    position: sticky !important;
    left: 0 !important;
    background: var(--card, #fff) !important;
    z-index: 1 !important;
    box-shadow: 2px 0 4px rgba(0,0,0,0.04) !important;
  }

  /* Ders hucreleri */
  table.ders-programi-tablo td.ders-cell {
    width: 92px !important;
    min-width: 92px !important;
    padding: 6px 4px !important;
    vertical-align: middle !important;
    text-align: center !important;
  }

  /* Ders chip */
  table.ders-programi-tablo .ders-chip {
    display: inline-block !important;
    font-size: 0.7rem !important;
    padding: 4px 6px !important;
    line-height: 1.2 !important;
    border-radius: 6px !important;
    word-break: break-word !important;
    max-width: 100% !important;
  }

  /* Bos chip */
  table.ders-programi-tablo .bos-chip {
    font-size: 0.75rem !important;
    opacity: 0.4 !important;
  }
}

/* Cok kucuk telefonlar */
@media (max-width: 380px) {
  table.ders-programi-tablo {
    min-width: 500px !important;
  }
  table.ders-programi-tablo td.ders-cell {
    width: 82px !important;
    min-width: 82px !important;
  }
  table.ders-programi-tablo .ders-chip {
    font-size: 0.65rem !important;
  }
}
'''

# Dosyanin sonuna ekle (idempotent kontrol)
with open(CSS, "r", encoding="utf-8") as f:
    icerik = f.read()

if "DERS PROGRAMI TABLOSU - MOBIL OZEL" in icerik:
    print("[ATLA] Bu kurallar zaten mobile.css'te var")
else:
    with open(CSS, "a", encoding="utf-8") as f:
        f.write(EKLENTI)
    print("[OK] Ders programi mobil kurallari mobile.css'e eklendi")

print("""
============================================================
SIMDI:
1. git add static/mobile.css
2. git commit -m "Mobil ders programi tablosu duzeltmesi"
3. git push
4. Telefonda /ders-programi sayfasini gizli sekmede ac
============================================================
""")