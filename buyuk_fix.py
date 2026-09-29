# -*- coding: utf-8 -*-
"""3 sorunu duzeltir: mail_service import, bozuk test-email endpoint, dropdown-fix.js."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================
# 1) MAIL_SERVICE.PY - dogru Brevo import
# ============================================================
MAIL_YOL = os.path.join(KOK, "mail_service.py")
if os.path.exists(MAIL_YOL):
    shutil.copy2(MAIL_YOL, os.path.join(YED, f"mail_service.py.{stamp}.bak"))

MAIL_SERVICE = '''# -*- coding: utf-8 -*-
"""E-posta gonderim servisi - Brevo (sib-api-v3-sdk)."""
import os
import threading
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def _brevo_client():
    cfg = sib_api_v3_sdk.Configuration()
    cfg.api_key["api-key"] = os.environ.get("BREVO_API_KEY", "")
    return sib_api_v3_sdk.ApiClient(cfg)


def _gonder_sync(konu, alicilar, html, duz_metin=None):
    api_key = os.environ.get("BREVO_API_KEY", "")
    if not api_key:
        print("[Brevo] HATA: BREVO_API_KEY tanimli degil.", flush=True)
        return False

    if isinstance(alicilar, str):
        alicilar = [alicilar]

    gonderen_email = os.environ.get("MAIL_DEFAULT_SENDER", "")
    gonderen_isim = os.environ.get("MAIL_SENDER_NAME", "C-Peak Panel")

    if not gonderen_email:
        print("[Brevo] HATA: MAIL_DEFAULT_SENDER tanimli degil.", flush=True)
        return False

    try:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(_brevo_client())
        sender = {"name": gonderen_isim, "email": gonderen_email}
        to = [{"email": e} for e in alicilar]

        email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=konu,
            html_content=html,
            text_content=duz_metin if duz_metin else None,
        )
        response = api_instance.send_transac_email(email)
        print("[Brevo] OK -> " + str(alicilar) + " | " + konu, flush=True)
        return True
    except ApiException as e:
        print("[Brevo] API HATA -> " + str(alicilar) + " | " + konu + " | " + str(e), flush=True)
        return False
    except Exception as e:
        print("[Brevo] HATA -> " + str(alicilar) + " | " + konu + " | " + str(e), flush=True)
        return False


def send_email(konu, alicilar, html, duz_metin=None):
    """Arka planda e-posta gonder."""
    t = threading.Thread(target=_gonder_sync, args=(konu, alicilar, html, duz_metin), daemon=True)
    t.start()
    return True


# ============================================================
# HAZIR SABLONLAR
# ============================================================

def sablon_kayit(ad, tc, sifre, giris_url):
    return (
        "<div style=\\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\\">"
        "<h2 style=\\"color:#18181b;\\">Hos geldiniz, " + str(ad) + "</h2>"
        "<p>C-Peak Panel'e kaydiniz olusturuldu. Giris bilgileriniz:</p>"
        "<table style=\\"background:#f4f4f5;padding:16px;border-radius:8px;width:100%;\\">"
        "<tr><td><b>T.C. Kimlik No</b></td><td>" + str(tc) + "</td></tr>"
        "<tr><td><b>Sifre</b></td><td>" + str(sifre) + "</td></tr>"
        "</table>"
        "<p style=\\"margin-top:20px;\\"><a href=\\"" + str(giris_url) + "\\" "
        "style=\\"background:#f59e0b;color:#fff;padding:12px 24px;border-radius:8px;"
        "text-decoration:none;font-weight:600;\\">Giris Yap</a></p>"
        "</div>"
    )


def sablon_sifre_talebi(ad, tc, email):
    return (
        "<div style=\\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\\">"
        "<h2 style=\\"color:#18181b;\\">Sifre Sifirlama Talebi</h2>"
        "<p>Merhaba " + str(ad) + ",</p>"
        "<p>Sifre sifirlama talebiniz alindi. Yonetim en kisa surede sizinle iletisime gececek "
        "ve yeni sifrenizi iletecektir.</p>"
        "<table style=\\"background:#f4f4f5;padding:16px;border-radius:8px;width:100%;\\">"
        "<tr><td><b>T.C. Kimlik No</b></td><td>" + str(tc) + "</td></tr>"
        "</table>"
        "<p style=\\"color:#71717a;font-size:13px;margin-top:24px;\\">"
        "Bu talebi siz olusturmadiysaniz bu e-postayi dikkate almayin.</p>"
        "</div>"
    )


def sablon_test():
    return (
        "<div style=\\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\\">"
        "<h2 style=\\"color:#18181b;\\">Test E-postasi</h2>"
        "<p>Bu e-posta C-Peak Panel'in e-posta servisinin dogru calistigini dogrulamak icin gonderildi.</p>"
        "<p style=\\"color:#16a34a;font-weight:600;\\">Eger bu e-postayi gorduyseniz, servis calisiyor demektir.</p>"
        "</div>"
    )
'''

with open(MAIL_YOL, "w", encoding="utf-8") as f:
    f.write(MAIL_SERVICE)
print("[OK] mail_service.py sib_api_v3_sdk ile yeniden yazildi")


# ============================================================
# 2) APP.PY - bozuk /admin/test-email endpoint'ini temizle
# ============================================================
APP = os.path.join(KOK, "app.py")
shutil.copy2(APP, os.path.join(YED, f"app.py.{stamp}.bak"))

with open(APP, "r", encoding="utf-8") as f:
    ac = f.read()

# Bozuk blogu bul: @app.route("/admin/test-email" ile baslayan,
# sonraki @app.route VEYA if __name__ oncesine kadar
PATTERN = re.compile(
    r'@app\.route\("/admin/test-email".*?(?=\n@app\.route|\nif\s+__name__)',
    re.DOTALL
)

YENI_ENDPOINT = '''@app.route("/admin/test-email", methods=["GET", "POST"])
@login_required("admin")
def admin_test_email():
    from flask import Response as _R
    if request.method == "POST":
        alici = request.form.get("email", "").strip()
        if not alici or "@" not in alici:
            return _R("Gecersiz e-posta adresi.", mimetype="text/plain"), 400
        try:
            send_email("C-Peak Panel Test", alici, sablon_test())
            msg = "Test e-postasi kuyruga alindi: " + alici
            msg = msg + "<br><br>1-2 dakika icinde gelen kutunuzu kontrol edin."
            msg = msg + "<br>Gelmezse Render Logs'a bakin (Brevo satirlari)."
            return _R("<pre style='font:14px/1.6 monospace;padding:24px;'>" + msg + "</pre>", mimetype="text/html")
        except Exception as e:
            return _R("<pre>HATA: " + str(e) + "</pre>", mimetype="text/html"), 500

    form = '<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">'
    form = form + '<meta name="viewport" content="width=device-width,initial-scale=1">'
    form = form + '<title>Test E-postasi</title></head>'
    form = form + '<body style="font-family:system-ui,sans-serif;background:#fafaf9;margin:0;'
    form = form + 'display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px;">'
    form = form + '<form method="POST" style="background:#fff;padding:28px;border-radius:14px;'
    form = form + 'box-shadow:0 4px 20px rgba(0,0,0,0.06);max-width:440px;width:100%;">'
    form = form + '<h2 style="margin:0 0 8px;color:#18181b;">Test E-postasi</h2>'
    form = form + '<p style="margin:0 0 20px;color:#71717a;font-size:14px;">Kendi e-posta adresinize test mesaji gonderin.</p>'
    form = form + '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
    form = form + '<input type="email" name="email" placeholder="ornek@mail.com" required '
    form = form + 'style="width:100%;padding:12px 14px;border:1px solid #d4d4d8;border-radius:10px;'
    form = form + 'font-size:16px;box-sizing:border-box;">'
    form = form + '<button type="submit" style="margin-top:14px;padding:12px 24px;background:#f59e0b;'
    form = form + 'color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;'
    form = form + 'cursor:pointer;width:100%;">Gonder</button>'
    form = form + '<p style="margin:16px 0 0;font-size:13px;color:#a1a1aa;text-align:center;">'
    form = form + '<a href="/admin" style="color:#71717a;">Admin panele don</a></p>'
    form = form + '</form></body></html>'
    return _R(form, mimetype="text/html")
'''

sayi = 0
while PATTERN.search(ac):
    ac = PATTERN.sub(YENI_ENDPOINT, ac, count=1)
    sayi += 1
    if sayi > 5:
        break

if sayi:
    print(f"[OK] {sayi} adet /admin/test-email blogu temizlendi ve yenisi yazildi")
else:
    print("[UYARI] /admin/test-email blogu bulunamadi")

with open(APP, "w", encoding="utf-8") as f:
    f.write(ac)


# ============================================================
# 3) DROPDOWN-FIX.JS YOKSA OLUSTUR
# ============================================================
DJS = os.path.join(KOK, "static", "dropdown-fix.js")
if not os.path.exists(DJS):
    os.makedirs(os.path.dirname(DJS), exist_ok=True)
    DROPDOWN = '''/* Dropdown toggle + dis tikla + ESC */
(function () {
  "use strict";
  var TOGGLE_SEL = '[data-dropdown-toggle],[data-toggle="dropdown"],[data-bs-toggle="dropdown"],.dropdown-toggle,.user-menu-toggle,.profile-toggle,[aria-haspopup="true"]';
  var MENU_SEL = '[data-dropdown],.dropdown-menu,.user-menu,.profile-menu,.menu-dropdown,.menu-panel';

  function menuBul(btn) {
    var id = btn.getAttribute("aria-controls");
    if (id) { var m = document.getElementById(id); if (m) return m; }
    var t = btn.getAttribute("data-target") || btn.getAttribute("data-bs-target");
    if (t) { try { var m2 = document.querySelector(t); if (m2) return m2; } catch (e) {} }
    if (btn.parentElement) {
      var m3 = btn.parentElement.querySelector(MENU_SEL);
      if (m3) return m3;
    }
    if (btn.nextElementSibling && btn.nextElementSibling.matches(MENU_SEL)) return btn.nextElementSibling;
    return null;
  }
  function acikMi(m) {
    if (!m) return false;
    return m.classList.contains("show") || m.classList.contains("open") ||
           m.classList.contains("active") || m.classList.contains("visible") ||
           m.style.display === "block";
  }
  function ac(m, b) { m.classList.add("show"); if (b) b.setAttribute("aria-expanded", "true"); }
  function kapat(m, b) {
    m.classList.remove("show", "open", "active", "visible");
    if (m.style.display === "block") m.style.display = "";
    if (b) b.setAttribute("aria-expanded", "false");
  }
  function hepsiniKapat(haric) {
    document.querySelectorAll(MENU_SEL).forEach(function (m) {
      if (m === haric) return;
      if (acikMi(m)) kapat(m);
    });
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(TOGGLE_SEL);
    if (!btn) return;
    var menu = menuBul(btn);
    if (!menu) return;
    e.stopImmediatePropagation();
    e.preventDefault();
    if (acikMi(menu)) { kapat(menu, btn); }
    else { hepsiniKapat(menu); ac(menu, btn); }
  }, true);
  document.addEventListener("click", function (e) {
    var icerde = e.target.closest && e.target.closest(TOGGLE_SEL + "," + MENU_SEL);
    if (iceride) return;
    hepsiniKapat(null);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" || e.keyCode === 27) hepsiniKapat(null);
  });
})();
'''
    with open(DJS, "w", encoding="utf-8") as f:
        f.write(DROPDOWN)
    print("[OK] static/dropdown-fix.js olusturuldu")
else:
    print("[ATLA] dropdown-fix.js zaten var")

print("""
============================================================
SIMDI:
1. py -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('OK')"
   -> cikti 'OK' olmali. Hata varsa bana gonder, PUSH ETME.
2. py -c "import ast; ast.parse(open('mail_service.py', encoding='utf-8').read()); print('OK')"
   -> cikti 'OK' olmali.
3. git add app.py mail_service.py static/dropdown-fix.js
4. git commit -m "Mail ve endpoint duzeltmeleri"
5. git push
============================================================
""")