# -*- coding: utf-8 -*-
"""Dropdown duzeltmesi: toggle butonu ac/kapat + dis tikla kapat + ESC ile kapat."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(KOK, "templates", "base.html")
STATIC = os.path.join(KOK, "static")
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

DROPDOWN_JS = '''/* ============================================================
   Dropdown Duzeltmesi
   - Toggle butonuna basinca: acik ise kapat, kapali ise ac
   - Bos yere tiklayinca: kapat
   - ESC tusu: kapat
   Mevcut toggle kodunu override eder.
   ============================================================ */
(function () {
  'use strict';

  var TOGGLE_SEL = [
    '[data-dropdown-toggle]',
    '[data-toggle="dropdown"]',
    '[data-bs-toggle="dropdown"]',
    '.dropdown-toggle',
    '.user-menu-toggle',
    '.profile-toggle',
    '.menu-toggle',
    '[aria-haspopup="true"]'
  ].join(',');

  var MENU_SEL = [
    '[data-dropdown]',
    '.dropdown-menu',
    '.user-menu',
    '.profile-menu',
    '.menu-dropdown',
    '.menu-panel'
  ].join(',');

  function menuBul(btn) {
    var id = btn.getAttribute('aria-controls');
    if (id) {
      var m = document.getElementById(id);
      if (m) return m;
    }
    var target = btn.getAttribute('data-target') || btn.getAttribute('data-bs-target');
    if (target) {
      try { var m2 = document.querySelector(target); if (m2) return m2; } catch (e) {}
    }
    if (btn.parentElement) {
      var m3 = btn.parentElement.querySelector(MENU_SEL);
      if (m3) return m3;
    }
    if (btn.nextElementSibling && btn.nextElementSibling.matches &&
        btn.nextElementSibling.matches(MENU_SEL)) {
      return btn.nextElementSibling;
    }
    return null;
  }

  function acikMi(menu) {
    if (!menu) return false;
    return menu.classList.contains('show') ||
           menu.classList.contains('open') ||
           menu.classList.contains('active') ||
           menu.classList.contains('visible') ||
           menu.style.display === 'block';
  }

  function ac(menu, btn) {
    menu.classList.add('show');
    if (btn) btn.setAttribute('aria-expanded', 'true');
  }

  function kapat(menu, btn) {
    menu.classList.remove('show', 'open', 'active', 'visible');
    if (menu.style.display === 'block') menu.style.display = '';
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }

  function hepsiniKapat(haric) {
    document.querySelectorAll(MENU_SEL).forEach(function (m) {
      if (m === haric) return;
      if (acikMi(m)) kapat(m);
    });
  }

  /* Toggle butonlari - capture phase'de mevcut kodu blokla */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest(TOGGLE_SEL);
    if (!btn) return;
    var menu = menuBul(btn);
    if (!menu) return;

    e.stopImmediatePropagation();
    e.preventDefault();

    if (acikMi(menu)) {
      kapat(menu, btn);
    } else {
      hepsiniKapat(menu);
      ac(menu, btn);
    }
  }, true);

  /* Disina tiklayinca kapat */
  document.addEventListener('click', function (e) {
    var icerde = e.target.closest &&
                 e.target.closest(TOGGLE_SEL + ',' + MENU_SEL);
    if (iceride) return;
    hepsiniKapat(null);
  });

  /* ESC ile kapat */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.keyCode === 27) {
      hepsiniKapat(null);
    }
  });
})();
'''

# 1) JS dosyasini yaz
if not os.path.isdir(STATIC):
    os.makedirs(STATIC, exist_ok=True)
js_yol = os.path.join(STATIC, "dropdown-fix.js")
if os.path.exists(js_yol):
    shutil.copy2(js_yol, os.path.join(YED, f"dropdown-fix.js.{stamp}.bak"))
with open(js_yol, "w", encoding="utf-8") as f:
    f.write(DROPDOWN_JS)
print(f"[OK] static/dropdown-fix.js olusturuldu ({len(DROPDOWN_JS)} karakter)")

# 2) base.html'e </body> oncesi ekle
if not os.path.exists(TPL):
    print(f"[HATA] {TPL} bulunamadi")
    exit(1)

shutil.copy2(TPL, os.path.join(YED, f"base.html.{stamp}.bak"))
print(f"[YEDEK] backups/base.html.{stamp}.bak")

with open(TPL, "r", encoding="utf-8") as f:
    html = f.read()

if "dropdown-fix.js" in html:
    print("[ATLA] dropdown-fix.js zaten base.html'de")
else:
    SCRIPT_TAG = (
        '    <!-- Dropdown duzeltmesi -->\n'
        '    <script src="{{ url_for(\'static\', filename=\'dropdown-fix.js\') }}" defer></script>\n'
    )
    m = re.search(r'(\s*</body>)', html, re.IGNORECASE)
    if m:
        html = html[:m.start()] + "\n" + SCRIPT_TAG + html[m.start():]
        with open(TPL, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] dropdown-fix.js base.html'e eklendi (</body> oncesi)")
    else:
        print("[UYARI] </body> etiketi bulunamadi")

print("""
============================================================
SIMDI:
1. git add static/dropdown-fix.js templates/base.html
2. git commit -m "Dropdown toggle ve dis tikla kapat duzeltmesi"
3. git push
4. Render deploy'unu bekle
5. Test et: dropdown ac/kapat, bos yere tikla kapat, ESC ile kapat
============================================================
""")