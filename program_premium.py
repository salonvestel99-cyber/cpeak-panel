# -*- coding: utf-8 -*-
"""Ders programini mobilde gun-kart premium tasarima cevirir."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(KOK, "templates", "ders_programi.html")
CSS = os.path.join(KOK, "static", "mobile.css")
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# 1) SABLON
shutil.copy2(TPL, os.path.join(YED, f"ders_programi.html.{stamp}.bak"))
print(f"[YEDEK] backups/ders_programi.html.{stamp}.bak")

with open(TPL, "r", encoding="utf-8") as f:
    tpl = f.read()

# Tablo wrapper'a dp-desktop class ekle
if 'class="table-wrap dp-desktop"' not in tpl:
    tpl = tpl.replace('<div class="table-wrap">',
                      '<div class="table-wrap dp-desktop">', 1)
    print("[OK] Table-wrap'a 'dp-desktop' class eklendi")

# Mobil kart blogu
MOBIL_BLOK = """
  <!-- Mobil gorunum: gun gun kartlar -->
  <div class="dp-mobil">
    {% for g, ad in gunler.items() %}
      {% set gun_dersleri = [] %}
      {% for saat in saatler %}
        {% if program.get((g, saat)) %}
          {% set _ = gun_dersleri.append((saat, program[(g, saat)])) %}
        {% endif %}
      {% endfor %}
      <div class="dp-gun-card{% if not gun_dersleri %} dp-gun-card-bos{% endif %}">
        <div class="dp-gun-head">
          <span class="dp-gun-ad">{{ ad }}</span>
          {% if gun_dersleri %}
            <span class="dp-gun-sayi">{{ gun_dersleri|length }}</span>
          {% endif %}
        </div>
        {% if gun_dersleri %}
          {% for saat, ders in gun_dersleri %}
            <div class="dp-ders-satir">
              <span class="dp-saat-badge">{{ saat }}</span>
              <span class="dp-ders-ad">{{ ders }}</span>
            </div>
          {% endfor %}
        {% else %}
          <div class="dp-bos">Ders yok</div>
        {% endif %}
      </div>
    {% endfor %}
  </div>
"""

# Tablonun hemen ardindaki kapanis bloklarini bul, mobil blogu ekle
PATTERN = re.compile(r'(</table>\s*</div>\s*</div>)', re.DOTALL)
if 'class="dp-mobil"' in tpl:
    print("[ATLA] dp-mobil zaten var")
elif PATTERN.search(tpl):
    tpl = PATTERN.sub(r'\1' + MOBIL_BLOK, tpl, count=1)
    print("[OK] Mobil kart blogu eklendi")
else:
    print("[UYARI] Tablo kapanis pattern bulunamadi")

with open(TPL, "w", encoding="utf-8") as f:
    f.write(tpl)

# 2) CSS
CSS_BLOK = """

/* ============================================================
   DERS PROGRAMI - PREMIUM MOBIL TASARIM
   ============================================================ */
.dp-mobil { display: none; }

@media (max-width: 768px) {

  .dp-desktop { display: none !important; }
  .dp-mobil { display: block !important; }

  .dp-mobil .dp-gun-card {
    background: var(--card, #fff);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.05);
    overflow: hidden;
  }

  .dp-mobil .dp-gun-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px dashed rgba(0,0,0,0.08);
  }

  .dp-mobil .dp-gun-ad {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink, #18181b);
    letter-spacing: -0.01em;
  }

  .dp-mobil .dp-gun-sayi {
    background: linear-gradient(135deg, #f59e0b, #f97316);
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    min-width: 24px;
    text-align: center;
  }

  .dp-mobil .dp-ders-satir {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(0,0,0,0.04);
  }

  .dp-mobil .dp-ders-satir:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .dp-mobil .dp-saat-badge {
    flex-shrink: 0;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(245,158,11,0.12);
    color: #d97706;
    font-weight: 800;
    font-size: 0.85rem;
    border-radius: 10px;
    border: 1px solid rgba(245,158,11,0.2);
  }

  .dp-mobil .dp-ders-ad {
    flex: 1;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--ink, #27272a);
    line-height: 1.3;
    word-break: break-word;
  }

  .dp-mobil .dp-gun-card-bos { opacity: 0.55; }

  .dp-mobil .dp-bos {
    text-align: center;
    color: var(--muted, #a1a1aa);
    font-size: 0.88rem;
    font-style: italic;
    padding: 8px 0;
  }
}

@media (max-width: 380px) {
  .dp-mobil .dp-gun-card { padding: 14px; border-radius: 14px; }
  .dp-mobil .dp-gun-ad { font-size: 0.98rem; }
  .dp-mobil .dp-ders-ad { font-size: 0.9rem; }
  .dp-mobil .dp-saat-badge { width: 30px; height: 30px; font-size: 0.78rem; }
}

html[data-theme="dark"] .dp-mobil .dp-gun-card,
html.dark .dp-mobil .dp-gun-card {
  background: rgba(255,255,255,0.03);
  border-color: rgba(255,255,255,0.06);
}
html[data-theme="dark"] .dp-mobil .dp-gun-ad,
html.dark .dp-mobil .dp-gun-ad,
html[data-theme="dark"] .dp-mobil .dp-ders-ad,
html.dark .dp-mobil .dp-ders-ad { color: #fafaf9; }
html[data-theme="dark"] .dp-mobil .dp-gun-head,
html.dark .dp-mobil .dp-gun-head { border-bottom-color: rgba(255,255,255,0.08); }
html[data-theme="dark"] .dp-mobil .dp-ders-satir,
html.dark .dp-mobil .dp-ders-satir { border-bottom-color: rgba(255,255,255,0.04); }
html[data-theme="dark"] .dp-mobil .dp-saat-badge,
html.dark .dp-mobil .dp-saat-badge {
  background: rgba(245,158,11,0.18);
  color: #fbbf24;
  border-color: rgba(245,158,11,0.3);
}
"""

with open(CSS, "a", encoding="utf-8") as f:
    f.write(CSS_BLOK)
print("[OK] Premium mobil CSS eklendi")

print("""
============================================================
SIMDI:
1. git add templates/ders_programi.html static/mobile.css
2. git commit -m "Ders programi mobil premium tasarim"
3. git push
4. Telefonda /ders-programi sayfasini GIZLI SEKMEDE ac
============================================================
""")