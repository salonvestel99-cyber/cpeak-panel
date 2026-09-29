# -*- coding: utf-8 -*-
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
