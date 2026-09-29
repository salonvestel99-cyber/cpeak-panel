# -*- coding: utf-8 -*-
"""E-posta altyapisi kurar: mail_service.py + app.py entegrasyonu."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================
# 1) MAIL_SERVICE.PY OLUSTUR
# ============================================================
MAIL_SERVICE = '''# -*- coding: utf-8 -*-
"""E-posta gonderim servisi.

Flask-Mail + threading kullanir. Gonderim arka planda olur,
kullanici beklemez. SMTP bilgileri .env / Render env'den okunur.
"""
import os
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _config():
    return {
        "server":   os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
        "port":     int(os.environ.get("MAIL_PORT", "587")),
        "tls":      os.environ.get("MAIL_USE_TLS", "1") == "1",
        "ssl":      os.environ.get("MAIL_USE_SSL", "0") == "1",
        "user":     os.environ.get("MAIL_USERNAME", ""),
        "pass":     os.environ.get("MAIL_PASSWORD", ""),
        "sender":   os.environ.get("MAIL_DEFAULT_SENDER", ""),
        "sender_name": os.environ.get("MAIL_SENDER_NAME", "C-Peak Panel"),
    }


def _gonder_sync(konu, alicilar, html, duz_metin=None):
    """Senkron gonderim. Ic fonksiyon, arka planda cagrilir."""
    cfg = _config()
    if not cfg["user"] or not cfg["pass"]:
        print("[mail] UYARI: MAIL_USERNAME/MAIL_PASSWORD tanimli degil, gonderim atlandi", flush=True)
        return False

    if isinstance(alicilar, str):
        alicilar = [alicilar]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = konu
    msg["From"] = f'{cfg["sender_name"]} <{cfg["sender"] or cfg["user"]}>'
    msg["To"] = ", ".join(alicilar)

    if duz_metin:
        msg.attach(MIMEText(duz_metin, "plain", "utf-8"))
    if html:
        msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        if cfg["ssl"]:
            s = smtplib.SMTP_SSL(cfg["server"], cfg["port"], timeout=20)
        else:
            s = smtplib.SMTP(cfg["server"], cfg["port"], timeout=20)
            if cfg["tls"]:
                s.starttls()
        s.login(cfg["user"], cfg["pass"])
        s.sendmail(cfg["sender"] or cfg["user"], alicilar, msg.as_string())
        s.quit()
        print(f"[mail] OK -> {alicilar} | {konu}", flush=True)
        return True
    except Exception as e:
        print(f"[mail] HATA -> {alicilar} | {konu} | {e}", flush=True)
        return False


def send_email(konu, alicilar, html, duz_metin=None):
    """Arka planda e-posta gonder. Hemen doner."""
    t = threading.Thread(
        target=_gonder_sync,
        args=(konu, alicilar, html, duz_metin),
        daemon=True,
    )
    t.start()
    return True


# ============================================================
# HAZIR SABLONLAR
# ============================================================

def sablon_kayit(ad, tc, sifre, giris_url):
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;">
      <h2 style="color:#18181b;">Hos geldiniz, {ad}</h2>
      <p>C-Peak Panel'e kaydiniz olusturuldu. Giris bilgileriniz:</p>
      <table style="background:#f4f4f5;padding:16px;border-radius:8px;width:100%;font-size:15px;">
        <tr><td><b>T.C. Kimlik No</b></td><td>{tc}</td></tr>
        <tr><td><b>Sifre</b></td><td>{sifre}</td></tr>
      </table>
      <p style="margin-top:20px;">
        <a href="{giris_url}" style="background:#f59e0b;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;">Giris Yap</a>
      </p>
      <p style="color:#71717a;font-size:13px;margin-top:24px;">
        Guvenliginiz icin giris yaptiktan sonra sifrenizi degistirmenizi oneririz.
      </p>
    </div>
    """


def sablon_sifre_talebi(ad, tc, email):
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;">
      <h2 style="color:#18181b;">Sifre Sifirlama Talebi</h2>
      <p>Merhaba {ad},</p>
      <p>Sifre sifirlama talebiniz alindi. Yonetim en kisa surede sizinle iletisime gececek
      ve yeni sifrenizi iletecektir.</p>
      <table style="background:#f4f4f5;padding:16px;border-radius:8px;width:100%;font-size:15px;">
        <tr><td><b>T.C. Kimlik No</b></td><td>{tc}</td></tr>
      </table>
      <p style="color:#71717a;font-size:13px;margin-top:24px;">
        Bu talebi siz olusturmadiysaniz bu e-postayi dikkate almayin.
      </p>
    </div>
    """


def sablon_test():
    return """
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;">
      <h2 style="color:#18181b;">Test E-postasi</h2>
      <p>Bu e-posta C-Peak Panel'in e-posta servisinin dogru calistigini dogrulamak icin gonderildi.</p>
      <p style="color:#16a34a;font-weight:600;">Eger bu e-postayi gorduyseniz, servis calisiyor demektir.</p>
    </div>
    """
'''

mail_yol = os.path.join(KOK, "mail_service.py")
if os.path.exists(mail_yol):
    shutil.copy2(mail_yol, os.path.join(YED, f"mail_service.py.{stamp}.bak"))
with open(mail_yol, "w", encoding="utf-8") as f:
    f.write(MAIL_SERVICE)
print("[OK] mail_service.py olusturuldu")


# ============================================================
# 2) REQUIREMENTS.TXT'E Flask-Mail EKLE
# ============================================================
req_yol = os.path.join(KOK, "requirements.txt")
with open(req_yol, "r", encoding="utf-8") as f:
    req = f.read()
if "Flask-Mail" not in req and "flask-mail" not in req.lower():
    with open(req_yol, "a", encoding="utf-8") as f:
        if not req.endswith("\n"):
            f.write("\n")
        f.write("\n# --- E-posta ---\nFlask-Mail>=0.10.0\n")
    print("[OK] requirements.txt'e Flask-Mail eklendi")
else:
    print("[ATLA] Flask-Mail zaten requirements.txt'te")


# ============================================================
# 3) APP.PY'YE ENTEGRE ET
# ============================================================
APP = os.path.join(KOK, "app.py")
shutil.copy2(APP, os.path.join(YED, f"app.py.{stamp}.bak"))
print(f"[YEDEK] backups/app.py.{stamp}.bak")

with open(APP, "r", encoding="utf-8") as f:
    ac = f.read()

degisiklik = 0

# 3.1) Import ekle
if "from mail_service import" not in ac:
    # from models import get_db satirindan sonra ekle
    if "from models import get_db" in ac:
        ac = ac.replace(
            "from models import get_db",
            "from models import get_db\n"
            "from mail_service import send_email, sablon_sifre_talebi, sablon_test",
            1
        )
        print("[OK] mail_service import'u eklendi")
        degisiklik += 1
    else:
        print("[UYARI] 'from models import get_db' bulunamadi")
else:
    print("[ATLA] mail_service zaten import edilmis")

# 3.2) sifremi_unuttum route'una email gonderim ekle
# Mevcut kod: flash("Talebiniz alindi...") ve return redirect
# Oncesine email gonderen kodu ekle
ESKI_SIFRE = '''        conn.commit()
    conn.close()
    flash("Talebiniz alındı. Yönetim en kısa sürede sizinle iletişime geçecek.", "success")
    return redirect(url_for("login"))'''

YENI_SIFRE = '''        conn.commit()
        # E-posta gonder (arka planda)
        if email:
            try:
                giris_url = request.url_root.rstrip("/") + url_for("login")
                send_email(
                    "Sifre Sifirlama Talebiniz Alindi",
                    email,
                    sablon_sifre_talebi(u["name"], tc, email),
                )
            except Exception as _e:
                print(f"[sifremi_unuttum] email hata: {_e}", flush=True)
    conn.close()
    flash("Talebiniz alındı. Yönetim en kısa sürede sizinle iletişime geçecek.", "success")
    return redirect(url_for("login"))'''

if ESKI_SIFRE in ac:
    ac = ac.replace(ESKI_SIFRE, YENI_SIFRE, 1)
    print("[OK] /sifremi-unuttum route'una email gonderim eklendi")
    degisiklik += 1
else:
    print("[UYARI] /sifremi-unuttum pattern tam eslesmedi (elle kontrol gerek)")

# 3.3) Admin test email endpoint ekle
if "/admin/test-email" not in ac:
    TEST_ENDPOINT = '''

# ============================================================
# ADMIN TEST E-POSTA
# ============================================================
@app.route("/admin/test-email", methods=["GET", "POST"])
@login_required("admin")
def admin_test_email():
    from flask import Response as _R
    if request.method == "POST":
        alici = request.form.get("email", "").strip()
        if not alici or "@" not in alici:
            return _R("Gecersiz e-posta adresi.", mimetype="text/plain"), 400
        try:
            send_email("C-Peak Panel Test", alici, sablon_test())
            return _R(
                f"<pre>Test e-postasi kuyruga alindi: {alici}\\n"
                f"1-2 dakika icinde gelen kutunuzu kontrol edin.\\n"
                f"Gelmezse Render Logs'a bakin (mail ile ilgili satirlar).</pre>",
                mimetype="text/html"
            )
        except Exception as e:
            return _R(f"<pre>HATA: {e}</pre>", mimetype="text/html"), 500
    # GET -> basit form
    return _R(
        '<form method="POST" style="font-family:system-ui;padding:40px;max-width:480px;margin:0 auto;">'
        '<h2>Test E-postasi</h2>'
        '<input type="email" name="email" placeholder="ornek@mail.com" required '
        'style="width:100%;padding:12px;border:1px solid #ccc;border-radius:8px;font-size:16px;">'
        '<button type="submit" style="margin-top:12px;padding:12px 24px;background:#f59e0b;'
        'color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;">Gonder</button>'
        '</form>',
        mimetype="text/html"
    )
# ============================================================
'''
    # if __name__ oncesine ekle
    m = re.search(r'^if\s+__name__\s*==\s*["\']__main__["\']\s*:', ac, re.MULTILINE)
    if m:
        ac = ac[:m.start()] + TEST_ENDPOINT + "\n" + ac[m.start():]
        print("[OK] /admin/test-email endpoint'i eklendi")
        degisiklik += 1
    else:
        print("[UYARI] 'if __name__' bulunamadi")
else:
    print("[ATLA] /admin/test-email zaten var")

with open(APP, "w", encoding="utf-8") as f:
    f.write(ac)

print(f"\n[BITTI] {degisiklik} degisiklik yapildi")
print("""
============================================================
SIMDI YAPILACAKLAR
============================================================

1) PUSH ET:
   git add mail_service.py app.py requirements.txt
   git commit -m "E-posta servisi eklendi"
   git push

2) RENDER'DA ORTAM DEGISKENLERI (Environment sekmesi):
   MAIL_SERVER          = smtp.gmail.com
   MAIL_PORT            = 587
   MAIL_USE_TLS         = 1
   MAIL_USERNAME        = seninmail@gmail.com
   MAIL_PASSWORD        = xxxx xxxx xxxx xxxx   (Gmail Uygulama Sifresi)
   MAIL_DEFAULT_SENDER  = seninmail@gmail.com
   MAIL_SENDER_NAME     = C-Peak Panel

   GMAIL UYGULAMA SIFRESI NASIL ALINIR:
   - Google Hesabi -> Guvenlik -> 2 Adimli Dogrulama (acik olmali)
   - Guvenlik -> Uygulama Sifreleri -> "Posta" sec -> 16 haneli kod
   - Bu kodu MAIL_PASSWORD'e yaz (bosluklar dahil)

3) DEPLOY BITINCE TEST ET:
   - https://cpeak-panel.onrender.com/admin/test-email
   - Kendi e-posta adresini gir -> Gonder
   - 1-2 dakika icinde gelen kutusunu kontrol et
   - Gelmezse Render -> Logs -> "[mail]" satirlarina bak

4) TEST BASARILIYSA:
   - /sifremi-unuttum formundan bir talep olustur
   - E-posta adresine onay e-postasi gelmeli

============================================================
""")