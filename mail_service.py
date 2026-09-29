# -*- coding: utf-8 -*-
"""E-posta gonderim servisi - Brevo (sib-api-v3-sdk).

Kurumsal premium sablonlar. Okul bilgileri ve sosyal medya
hesaplari ortam degiskenlerinden okunur.
"""
import os
import threading
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


# ============================================================
# KURUMSAL BILGILER (Render env'den okunur)
# ============================================================
def _kurum():
    return {
        "ad":        os.environ.get("OKUL_ADI", "C-Peak English"),
        "adres":     os.environ.get("OKUL_ADRES", ""),
        "telefon":   os.environ.get("OKUL_TELEFON", ""),
        "eposta":    os.environ.get("OKUL_EPOSTA", "cpeakenglish@gmail.com"),
        "web":       os.environ.get("OKUL_WEB", "https://cpeak-panel.onrender.com"),
        "logo":      os.environ.get("OKUL_LOGO_URL", "https://cpeak-panel.onrender.com/static/logochrome.png"),
        "instagram": os.environ.get("SOSYAL_INSTAGRAM", ""),
        "youtube":   os.environ.get("SOSYAL_YOUTUBE", ""),
        "whatsapp":  os.environ.get("SOSYAL_WHATSAPP", ""),
    }


# ============================================================
# BREVO GONDERIM
# ============================================================
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

    gonderen_email = os.environ.get("MAIL_DEFAULT_SENDER", "cpeakenglish@gmail.com")
    gonderen_isim = os.environ.get("MAIL_SENDER_NAME", "C-Peak Panel")

    try:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(_brevo_client())
        sender = {"name": gonderen_isim, "email": gonderen_email}
        to = [{"email": e} for e in alicilar]
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=to, sender=sender, subject=konu,
            html_content=html,
            text_content=duz_metin if duz_metin else None,
        )
        api_instance.send_transac_email(email)
        print("[Brevo] OK -> " + str(alicilar) + " | " + konu, flush=True)
        return True
    except ApiException as e:
        print("[Brevo] API HATA -> " + str(alicilar) + " | " + str(e), flush=True)
        return False
    except Exception as e:
        print("[Brevo] HATA -> " + str(alicilar) + " | " + str(e), flush=True)
        return False


def send_email(konu, alicilar, html, duz_metin=None):
    """Arka planda e-posta gonder."""
    t = threading.Thread(
        target=_gonder_sync,
        args=(konu, alicilar, html, duz_metin),
        daemon=True,
    )
    t.start()
    return True


# ============================================================
# ORTAK SABLON ISKELETI (kurumsal kimlik)
# ============================================================
def _sablon(sayfa_basligi, icerik, vurgu_renk="#f59e0b", vurgu_gradient=None):
    """Tum mailler icin ortak iskelet.

    sayfa_basligi : mail ust basligi (orn: "Hos Geldiniz")
    icerik        : HTML icerik
    vurgu_renk    : mail turune gore ana renk (hex)
    vurgu_gradient: gradient varsa (orn: "linear-gradient(135deg,#f59e0b,#f97316)")
    """
    k = _kurum()
    grad = vurgu_gradient or ("linear-gradient(135deg, " + vurgu_renk + ", " + vurgu_renk + ")")

    # Sosyal medya linkleri
    sosyal = ""
    if k["instagram"]:
        sosyal += (
            '<a href="' + k["instagram"] + '" style="display:inline-block;margin:0 6px;'
            'padding:8px 14px;background:#f4f4f5;border-radius:8px;text-decoration:none;'
            'color:#52525b;font-size:13px;font-weight:600;">Instagram</a>'
        )
    if k["youtube"]:
        sosyal += (
            '<a href="' + k["youtube"] + '" style="display:inline-block;margin:0 6px;'
            'padding:8px 14px;background:#f4f4f5;border-radius:8px;text-decoration:none;'
            'color:#52525b;font-size:13px;font-weight:600;">YouTube</a>'
        )
    if k["whatsapp"]:
        sosyal += (
            '<a href="' + k["whatsapp"] + '" style="display:inline-block;margin:0 6px;'
            'padding:8px 14px;background:#f4f4f5;border-radius:8px;text-decoration:none;'
            'color:#52525b;font-size:13px;font-weight:600;">WhatsApp</a>'
        )

    # Iletisim satiri
    iletisim = ""
    if k["adres"]:
        iletisim += '<div style="margin:4px 0;color:#a1a1aa;font-size:12px;">' + k["adres"] + '</div>'
    if k["telefon"]:
        iletisim += '<div style="margin:4px 0;color:#a1a1aa;font-size:12px;">Tel: ' + k["telefon"] + '</div>'
    iletisim += '<div style="margin:4px 0;color:#a1a1aa;font-size:12px;">' + k["eposta"] + '</div>'

    return (
        '<!DOCTYPE html><html lang="tr"><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + sayfa_basligi + '</title>'
        '</head>'
        '<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'
        "'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#18181b;\">"

        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="background:#f4f4f5;padding:32px 16px;">'
        '<tr><td align="center">'

        # Ana kart
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
        'style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;'
        'box-shadow:0 4px 24px rgba(0,0,0,0.06);">'

        # Ust renkli serit
        '<tr><td style="height:6px;background:' + grad + ';"></td></tr>'

        # Header (logo + marka)
        '<tr><td style="padding:28px 32px 12px;text-align:center;">'
        '<img src="' + k["logo"] + '" alt="' + k["ad"] + '" '
        'style="height:44px;max-width:220px;display:block;margin:0 auto 8px;">'
        '<div style="font-size:13px;color:#a1a1aa;letter-spacing:0.05em;text-transform:uppercase;'
        'font-weight:600;">' + k["ad"] + '</div>'
        '</td></tr>'

        # Icerik
        '<tr><td style="padding:8px 32px 32px;">'
        + icerik +
        '</td></tr>'

        # Ayrac
        '<tr><td style="padding:0 32px;"><div style="height:1px;background:#e4e4e7;"></div></td></tr>'

        # Footer - sosyal medya
        + ('<tr><td style="padding:20px 32px 8px;text-align:center;">' + sosyal + '</td></tr>'
           if sosyal else '') +

        # Footer - iletisim
        '<tr><td style="padding:8px 32px 28px;text-align:center;">'
        + iletisim +
        '<div style="margin-top:12px;color:#d4d4d8;font-size:11px;">'
        'Bu e-posta otomatik gonderilmistir. Lutfen yanitlamayin.'
        '</div>'
        '</td></tr>'

        '</table>'
        # /Ana kart

        '<div style="margin-top:16px;color:#a1a1aa;font-size:11px;text-align:center;">'
        '&copy; ' + k["ad"] + ' &middot; <a href="' + k["web"] + '" '
        'style="color:#a1a1aa;text-decoration:none;">' + k["web"].replace("https://","").replace("http://","") + '</a>'
        '</div>'

        '</td></tr></table>'
        '</body></html>'
    )


def _baslik(metin, renk="#18181b"):
    return ('<h1 style="margin:0 0 12px;font-size:22px;font-weight:700;color:' + renk + ';'
            'letter-spacing:-0.01em;line-height:1.3;">' + metin + '</h1>')


def _p(metin, renk="#52525b"):
    return ('<p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:' + renk + ';">'
            + metin + '</p>')


def _kutu(icerik, arka="#f4f4f5", kenar=None):
    sol = ""
    if kenar:
        sol = "border-left:4px solid " + kenar + ";"
    return ('<div style="background:' + arka + ';padding:16px 20px;border-radius:12px;'
            'margin:18px 0;' + sol + '">' + icerik + '</div>')


def _buton(metin, link, renk="#f59e0b"):
    return ('<div style="margin:24px 0 8px;">'
            '<a href="' + link + '" style="display:inline-block;padding:14px 28px;'
            'background:' + renk + ';color:#ffffff;text-decoration:none;border-radius:10px;'
            'font-size:15px;font-weight:600;letter-spacing:0.01em;">' + metin + '</a>'
            '</div>')


def _satir(etiket, deger):
    return ('<tr>'
            '<td style="padding:8px 0;font-size:14px;color:#71717a;width:40%;">' + etiket + '</td>'
            '<td style="padding:8px 0;font-size:14px;color:#18181b;font-weight:600;">' + deger + '</td>'
            '</tr>')


def _tablo(satirlar):
    return ('<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
            'style="width:100%;border-collapse:collapse;">' + satirlar + '</table>')


# ============================================================
# HAZIR SABLONLAR
# ============================================================

def sablon_kayit(ad, tc, sifre, giris_url):
    """Yeni hesap acildiginda - YESIL tema."""
    icerik = (
        _baslik("Hos geldiniz, " + ad + "!")
        + _p("Hesabiniz basariyla olusturuldu. Asagidaki bilgilerle sisteme giris yapabilirsiniz.")
        + _kutu(
            _tablo(
                _satir("T.C. Kimlik No", tc)
                + _satir("Sifre", sifre)
            ),
            arka="#f0fdf4", kenar="#16a34a"
        )
        + _buton("Sisteme Giris Yap", giris_url, "#16a34a")
        + _p("Guvenliginiz icin giris yaptiktan sonra sifrenizi degistirmenizi oneririz.",
             "#71717a")
    )
    return _sablon("Hos Geldiniz", icerik, "#16a34a", "linear-gradient(135deg,#16a34a,#22c55e)")


def sablon_sifre_talebi(ad, tc, email):
    """Sifremi unuttum talebi - TURUNCU tema."""
    icerik = (
        _baslik("Sifre Sifirlama Talebiniz Alindi")
        + _p("Merhaba " + ad + ",")
        + _p("Sifre sifirlama talebiniz basariyla alindi. Yonetim en kisa surede "
             "sizinle iletisime gececek ve yeni sifrenizi iletecektir.")
        + _kutu(
            _tablo(_satir("T.C. Kimlik No", tc)),
            arka="#fff7ed", kenar="#f59e0b"
        )
        + _p("Bu talebi siz olusturmadiysaniz bu e-postayi dikkate almayin.", "#71717a")
    )
    return _sablon("Sifre Sifirlama", icerik, "#f59e0b", "linear-gradient(135deg,#f59e0b,#f97316)")


def sablon_sifre_degisti(ad, tc):
    """Kullanici sifresini degistirdi - KIRMIZI tema (guvenlik)."""
    icerik = (
        _baslik("Sifreniz Degistirildi", "#dc2626")
        + _p("Merhaba " + ad + ",")
        + _p("Hesabinizin sifresi az once basariyla degistirildi.")
        + _kutu(
            _tablo(_satir("T.C. Kimlik No", tc)),
            arka="#fef2f2", kenar="#dc2626"
        )
        + ('<div style="background:#fef2f2;border-radius:10px;padding:14px 18px;margin-top:16px;">'
           '<p style="margin:0;color:#dc2626;font-size:14px;font-weight:700;">'
           'Bu islemi siz yapmadiysaniz lutfen derhal yonetime ulasin.'
           '</p></div>')
    )
    return _sablon("Guvenlik Uyarisi", icerik, "#dc2626", "linear-gradient(135deg,#dc2626,#ef4444)")


def sablon_sifre_sifirlandi(ad, yeni_sifre):
    """Admin sifre sifirladi - MAVI tema."""
    icerik = (
        _baslik("Sifreniz Yenilendi")
        + _p("Merhaba " + ad + ",")
        + _p("Sifreniz yonetim tarafindan yenilendi. Yeni giris bilgileriniz:")
        + _kutu(
            _tablo(_satir("Yeni Sifre", yeni_sifre)),
            arka="#eff6ff", kenar="#2563eb"
        )
        + _p("Guvenliginiz icin giris yaptiktan sonra sifrenizi degistirmenizi oneririz.",
             "#71717a")
    )
    return _sablon("Sifre Yenilendi", icerik, "#2563eb", "linear-gradient(135deg,#2563eb,#3b82f6)")


def sablon_devamsizlik(ogrenci_ad, sinif, tarih):
    """Devamsizlik bildirimi - TURUNCU tema."""
    icerik = (
        _baslik("Devamsizlik Bildirimi")
        + _p("Sayin veli,")
        + _p("<b>" + ogrenci_ad + "</b> adli ogrenci asagidaki tarihte okula gelmemistir.")
        + _kutu(
            _tablo(
                _satir("Sinif", sinif)
                + _satir("Tarih", tarih)
            ),
            arka="#fff7ed", kenar="#f59e0b"
        )
        + _p("Bir hata oldugunu dusunuyorsaniz lutfen okul yonetimiyle iletisime gecin.",
             "#71717a")
    )
    return _sablon("Devamsizlik", icerik, "#f59e0b", "linear-gradient(135deg,#f59e0b,#f97316)")


def sablon_not_girildi(ogrenci_ad, ders, sinav, puan):
    """Not bildirimi - nota gore renk."""
    try:
        p = float(puan)
    except Exception:
        p = 0

    if p >= 85:
        renk = "#16a34a"; arka = "#f0fdf4"; durum = "Harika!"
    elif p >= 70:
        renk = "#0891b2"; arka = "#ecfeff"; durum = "Iyi"
    elif p >= 50:
        renk = "#d97706"; arka = "#fff7ed"; durum = "Geciyor"
    else:
        renk = "#dc2626"; arka = "#fef2f2"; durum = "Dusuk"

    icerik = (
        _baslik("Yeni Notunuz Aciklandi")
        + _p("Merhaba " + ogrenci_ad + ",")
        + _p("<b>" + ders + "</b> dersinden <b>" + sinav + "</b> sinavinin sonucu aciklandi:")
        + ('<div style="background:' + arka + ';padding:28px 20px;border-radius:14px;'
           'text-align:center;margin:20px 0;border-left:4px solid ' + renk + ';">'
           '<div style="font-size:52px;font-weight:800;color:' + renk + ';line-height:1;'
           'letter-spacing:-0.02em;">' + str(puan) + '</div>'
           '<div style="font-size:14px;color:' + renk + ';font-weight:700;margin-top:10px;'
           'text-transform:uppercase;letter-spacing:0.08em;">' + durum + '</div>'
           '</div>')
    )
    return _sablon("Not Aciklandi", icerik, renk, "linear-gradient(135deg," + renk + "," + renk + ")")


def sablon_test():
    """Test maili - TURUNCU tema."""
    icerik = (
        _baslik("Test E-postasi")
        + _p("Bu e-posta C-Peak Panel'in e-posta servisinin dogru calistigini "
             "dogrulamak icin gonderildi.")
        + _kutu(
            '<p style="margin:0;color:#16a34a;font-weight:700;font-size:15px;">'
            'Eger bu e-postayi gorduyseniz, servis calisiyor demektir.'
            '</p>',
            arka="#f0fdf4", kenar="#16a34a"
        )
        + _p("Tum mail sablonlari asagidaki gibi gorsel olarak kurumsal kimlik "
             "ile tasarlanmistir.", "#71717a")
    )
    return _sablon("Test", icerik, "#f59e0b", "linear-gradient(135deg,#f59e0b,#f97316)")
