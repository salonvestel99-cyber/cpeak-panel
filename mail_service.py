# -*- coding: utf-8 -*-
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
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Hos geldiniz, " + str(ad) + "</h2>"
        "<p>C-Peak Panel'e kaydiniz olusturuldu. Giris bilgileriniz:</p>"
        "<table style=\"background:#f4f4f5;padding:16px;border-radius:8px;width:100%;\">"
        "<tr><td><b>T.C. Kimlik No</b></td><td>" + str(tc) + "</td></tr>"
        "<tr><td><b>Sifre</b></td><td>" + str(sifre) + "</td></tr>"
        "</table>"
        "<p style=\"margin-top:20px;\"><a href=\"" + str(giris_url) + "\" "
        "style=\"background:#f59e0b;color:#fff;padding:12px 24px;border-radius:8px;"
        "text-decoration:none;font-weight:600;\">Giris Yap</a></p>"
        "</div>"
    )


def sablon_sifre_talebi(ad, tc, email):
    return (
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Sifre Sifirlama Talebi</h2>"
        "<p>Merhaba " + str(ad) + ",</p>"
        "<p>Sifre sifirlama talebiniz alindi. Yonetim en kisa surede sizinle iletisime gececek "
        "ve yeni sifrenizi iletecektir.</p>"
        "<table style=\"background:#f4f4f5;padding:16px;border-radius:8px;width:100%;\">"
        "<tr><td><b>T.C. Kimlik No</b></td><td>" + str(tc) + "</td></tr>"
        "</table>"
        "<p style=\"color:#71717a;font-size:13px;margin-top:24px;\">"
        "Bu talebi siz olusturmadiysaniz bu e-postayi dikkate almayin.</p>"
        "</div>"
    )


def sablon_test():
    return (
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Test E-postasi</h2>"
        "<p>Bu e-posta C-Peak Panel'in e-posta servisinin dogru calistigini dogrulamak icin gonderildi.</p>"
        "<p style=\"color:#16a34a;font-weight:600;\">Eger bu e-postayi gorduyseniz, servis calisiyor demektir.</p>"
        "</div>"
    )


# ============================================================
# YENI SABLONLAR
# ============================================================

def sablon_sifre_degisti(ad, tc):
    return (
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Sifreniz Degistirildi</h2>"
        "<p>Merhaba " + str(ad) + ",</p>"
        "<p>Hesabinizin sifresi az once basariyla degistirildi.</p>"
        "<table style=\"background:#f4f4f5;padding:16px;border-radius:8px;width:100%;\">"
        "<tr><td><b>T.C. Kimlik No</b></td><td>" + str(tc) + "</td></tr>"
        "</table>"
        "<p style=\"color:#dc2626;font-size:13px;margin-top:24px;font-weight:600;\">"
        "Bu islemi siz yapmadiysaniz lutfen derhal yonetime ulasin.</p>"
        "</div>"
    )


def sablon_sifre_sifirlandi(ad, yeni_sifre):
    return (
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Sifreniz Yenilendi</h2>"
        "<p>Merhaba " + str(ad) + ",</p>"
        "<p>Sifreniz yonetim tarafindan yenilendi. Yeni giris bilgileriniz:</p>"
        "<table style=\"background:#f4f4f5;padding:16px;border-radius:8px;width:100%;\">"
        "<tr><td><b>Yeni Sifre</b></td><td><b>" + str(yeni_sifre) + "</b></td></tr>"
        "</table>"
        "<p style=\"color:#71717a;font-size:13px;margin-top:24px;\">"
        "Guvenliginiz icin giris yaptiktan sonra sifrenizi degistirmenizi oneririz.</p>"
        "</div>"
    )


def sablon_devamsizlik(ogrenci_ad, sinif, tarih):
    return (
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Devamsizlik Bildirimi</h2>"
        "<p>Sayin veli,</p>"
        "<p><b>" + str(ogrenci_ad) + "</b> adli ogrenci asagidaki tarihte okula gelmemistir.</p>"
        "<table style=\"background:#fef3c7;padding:16px;border-radius:8px;width:100%;border-left:4px solid #f59e0b;\">"
        "<tr><td><b>Sinif</b></td><td>" + str(sinif) + "</td></tr>"
        "<tr><td><b>Tarih</b></td><td>" + str(tarih) + "</td></tr>"
        "</table>"
        "<p style=\"margin-top:20px;\">Bir hata oldugunu dusunuyorsaniz lutfen okul yonetimiyle iletisime gecin.</p>"
        "<p style=\"color:#71717a;font-size:13px;margin-top:24px;\">C-Peak Panel</p>"
        "</div>"
    )


def sablon_not_girildi(ogrenci_ad, ders, sinav, puan):
    try:
        p = float(puan)
    except Exception:
        p = 0
    if p >= 85:
        renk = "#16a34a"; arka = "#dcfce7"; durum = "Harika!"
    elif p >= 70:
        renk = "#0891b2"; arka = "#cffafe"; durum = "Iyi"
    elif p >= 50:
        renk = "#d97706"; arka = "#fef3c7"; durum = "Geciyor"
    else:
        renk = "#dc2626"; arka = "#fee2e2"; durum = "Dusuk"

    return (
        "<div style=\"font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;padding:24px;\">"
        "<h2 style=\"color:#18181b;\">Yeni Notunuz Aciklandi</h2>"
        "<p>Merhaba " + str(ogrenci_ad) + ",</p>"
        "<p><b>" + str(ders) + "</b> dersinden <b>" + str(sinav) + "</b> sinavinin sonucu aciklandi:</p>"
        "<div style=\"background:" + arka + ";padding:24px;border-radius:12px;text-align:center;margin:20px 0;border-left:4px solid " + renk + ";\">"
        "<div style=\"font-size:42px;font-weight:800;color:" + renk + ";line-height:1;\">" + str(puan) + "</div>"
        "<div style=\"font-size:14px;color:" + renk + ";font-weight:600;margin-top:6px;\">" + durum + "</div>"
        "</div>"
        "<p style=\"color:#71717a;font-size:13px;margin-top:24px;\">C-Peak Panel</p>"
        "</div>"
    )
