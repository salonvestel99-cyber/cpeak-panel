# -*- coding: utf-8 -*-
"""E-posta gönderim servisi - Brevo. Premium kurumsal şablonlar."""
import os
import threading
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


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


def _brevo_client():
    cfg = sib_api_v3_sdk.Configuration()
    cfg.api_key["api-key"] = os.environ.get("BREVO_API_KEY", "")
    return sib_api_v3_sdk.ApiClient(cfg)


def _gonder_sync(konu, alicilar, html, duz_metin=None):
    api_key = os.environ.get("BREVO_API_KEY", "")
    if not api_key:
        print("[Brevo] HATA: BREVO_API_KEY yok.", flush=True)
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
        print("[Brevo] API HATA -> " + str(e), flush=True)
        return False
    except Exception as e:
        print("[Brevo] HATA -> " + str(e), flush=True)
        return False


def send_email(konu, alicilar, html, duz_metin=None):
    t = threading.Thread(target=_gonder_sync, args=(konu, alicilar, html, duz_metin), daemon=True)
    t.start()
    return True


# ============================================================
# ORTAK CSS (email-safe, mobile + dark mode)
# ============================================================
CSS = """
body,table,td,p,a,li,blockquote{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}
table,td{mso-table-lspace:0;mso-table-rspace:0;border-collapse:collapse}
img{-ms-interpolation-mode:bicubic;border:0;height:auto;line-height:100%;outline:none;text-decoration:none}
body{margin:0;padding:0;width:100%!important;height:100%!important}
a{text-decoration:none}
@media only screen and (max-width:600px){
.wrap{padding:20px 10px!important}
.header{padding:24px 22px 18px!important}
.content{padding:6px 22px 26px!important}
.footer{padding:14px 22px 24px!important}
.h1{font-size:21px!important;line-height:1.3!important}
.p{font-size:15px!important;line-height:1.6!important}
.box{padding:14px 16px!important;border-radius:12px!important}
.btn{display:block!important;width:100%!important;text-align:center!important;box-sizing:border-box!important;padding:15px 18px!important}
.social-btn{display:block!important;margin:0 0 8px!important;width:100%!important;box-sizing:border-box!important;text-align:center!important}
.logo{height:40px!important}
.brand{font-size:11px!important;letter-spacing:0.1em!important}
.info-label{display:block!important;padding:0 0 2px!important;width:100%!important;font-size:13px!important}
.info-value{display:block!important;padding:0 0 12px!important;width:100%!important;font-size:16px!important}
}
@media (prefers-color-scheme: dark){
.body-bg{background-color:#09090b!important}
.card{background-color:#18181b!important;box-shadow:0 4px 24px rgba(0,0,0,0.5)!important;border:1px solid #27272a!important}
.h1{color:#fafaf9!important}
.p{color:#a1a1aa!important}
.muted{color:#71717a!important}
.divider{background-color:#27272a!important}
.box{background-color:#27272a!important}
.info-label{color:#a1a1aa!important}
.info-value{color:#fafaf9!important}
.social-btn{background-color:#27272a!important;color:#e4e4e7!important;border-color:#3f3f46!important}
.brand{color:#71717a!important}
.footer-link{color:#71717a!important}
}
"""


def _sablon(sayfa_basligi, icerik, vurgu_renk="#f59e0b", vurgu_gradient=None):
    k = _kurum()
    grad = vurgu_gradient or ("linear-gradient(135deg, " + vurgu_renk + " 0%, " + vurgu_renk + " 100%)")

    # Sosyal medya butonlari
    sosyal_buttons = ""
    if k["instagram"]:
        sosyal_buttons += (
            '<a href="' + k["instagram"] + '" class="social-btn" style="display:inline-block;'
            'margin:0 4px 6px;padding:10px 18px;background-color:#f4f4f5;border:1px solid #e4e4e7;'
            'border-radius:10px;color:#52525b;font-size:13px;font-weight:600;">Instagram</a>'
        )
    if k["youtube"]:
        sosyal_buttons += (
            '<a href="' + k["youtube"] + '" class="social-btn" style="display:inline-block;'
            'margin:0 4px 6px;padding:10px 18px;background-color:#f4f4f5;border:1px solid #e4e4e7;'
            'border-radius:10px;color:#52525b;font-size:13px;font-weight:600;">YouTube</a>'
        )
    if k["whatsapp"]:
        sosyal_buttons += (
            '<a href="' + k["whatsapp"] + '" class="social-btn" style="display:inline-block;'
            'margin:0 4px 6px;padding:10px 18px;background-color:#f4f4f5;border:1px solid #e4e4e7;'
            'border-radius:10px;color:#52525b;font-size:13px;font-weight:600;">WhatsApp</a>'
        )
    sosyal_html = ""
    if sosyal_buttons:
        sosyal_html = (
            '<tr><td align="center" style="padding:22px 32px 8px;">'
            + sosyal_buttons + '</td></tr>'
        )

    iletisim = ""
    if k["adres"]:
        iletisim += '<div class="muted" style="margin:4px 0;color:#a1a1aa;font-size:12px;line-height:1.55;">' + k["adres"] + '</div>'
    if k["telefon"]:
        iletisim += '<div class="muted" style="margin:4px 0;color:#a1a1aa;font-size:12px;line-height:1.55;">Tel: ' + k["telefon"] + '</div>'
    if k["eposta"]:
        iletisim += '<div class="muted" style="margin:4px 0;color:#a1a1aa;font-size:12px;line-height:1.55;">' + k["eposta"] + '</div>'

    web_kisa = k["web"].replace("https://", "").replace("http://", "")
    preheader = k["ad"] + " \u00b7 " + sayfa_basligi

    return (
        '<!DOCTYPE html><html lang="tr"><head>'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<meta name="x-apple-disable-message-reformatting">'
        '<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">'
        '<title>' + sayfa_basligi + '</title>'
        '<style>' + CSS + '</style>'
        '</head>'
        '<body class="body-bg" style="margin:0;padding:0;background-color:#f4f4f5;'
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;"
        'color:#18181b;">'

        '<div style="display:none;font-size:1px;color:#f4f4f5;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">'
        + preheader + '</div>'

        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
        'class="body-bg" style="background-color:#f4f4f5;">'
        '<tr><td align="center" class="wrap" style="padding:32px 16px;">'

        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" '
        'class="card" style="max-width:600px;width:100%;background-color:#ffffff;'
        'border-radius:20px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.06);">'

        '<tr><td style="height:5px;background:' + grad + ';line-height:5px;font-size:0;">&nbsp;</td></tr>'

        '<tr><td class="header" align="center" style="padding:32px 32px 22px;">'
        '<img src="' + k["logo"] + '" alt="' + k["ad"] + '" class="logo" '
        'style="height:48px;max-width:220px;display:block;margin:0 auto 10px;">'
        '<div class="brand" style="font-size:12px;letter-spacing:0.12em;text-transform:uppercase;'
        'font-weight:700;color:#a1a1aa;">' + k["ad"] + '</div>'
        '</td></tr>'

        '<tr><td style="padding:0 32px;">'
        '<div class="divider" style="height:1px;background-color:#e4e4e7;line-height:1px;font-size:0;">&nbsp;</div>'
        '</td></tr>'

        '<tr><td class="content" style="padding:8px 32px 30px;">' + icerik + '</td></tr>'

        '<tr><td style="padding:0 32px;">'
        '<div class="divider" style="height:1px;background-color:#e4e4e7;line-height:1px;font-size:0;">&nbsp;</div>'
        '</td></tr>'

        + sosyal_html +

        '<tr><td class="footer" align="center" style="padding:18px 32px 28px;">'
        + iletisim +
        '<div class="muted" style="margin-top:14px;font-size:11px;color:#a1a1aa;line-height:1.5;">'
        'Bu e-posta otomatik g\u00f6nderilmi\u015ftir, l\u00fctfen yan\u0131tlamay\u0131n.</div>'
        '</td></tr>'

        '</table>'

        '<div class="muted" style="margin-top:18px;font-size:11px;color:#a1a1aa;text-align:center;">'
        '&copy; 2026 ' + k["ad"] + ' &nbsp;&middot;&nbsp; '
        '<a class="footer-link" href="' + k["web"] + '" '
        'style="color:#a1a1aa;text-decoration:none;">' + web_kisa + '</a>'
        '</div>'

        '</td></tr></table>'
        '</body></html>'
    )


# ============================================================
# HTML YARDIMCI PARCALARI
# ============================================================
def _h1(metin, renk="#18181b"):
    return ('<h1 class="h1" style="margin:16px 0 14px;font-size:24px;font-weight:700;'
            'color:' + renk + ';letter-spacing:-0.02em;line-height:1.3;">' + metin + '</h1>')


def _p(metin, renk="#52525b"):
    return ('<p class="p" style="margin:0 0 14px;font-size:16px;line-height:1.65;'
            'color:' + renk + ';">' + metin + '</p>')


def _kutu(icerik, arka="#f9fafb", kenar="#f59e0b"):
    return ('<div class="box" style="background-color:' + arka + ';padding:18px 22px;'
            'border-radius:14px;margin:18px 0;border-left:4px solid ' + kenar + ';">'
            + icerik + '</div>')


def _buton(metin, link, renk="#f59e0b"):
    return ('<div style="margin:24px 0 6px;">'
            '<a href="' + link + '" class="btn" style="display:inline-block;padding:14px 28px;'
            'background-color:' + renk + ';color:#ffffff;border-radius:10px;'
            'font-size:15px;font-weight:700;">'
            + metin + ' &rarr;</a></div>')


def _satir(etiket, deger):
    return ('<tr>'
            '<td class="info-label" style="padding:6px 0;font-size:14px;color:#71717a;'
            'vertical-align:top;width:44%;">' + etiket + '</td>'
            '<td class="info-value" style="padding:6px 0;font-size:15px;color:#18181b;'
            'font-weight:600;vertical-align:top;">' + deger + '</td>'
            '</tr>')


def _tablo(satirlar):
    return ('<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
            'style="width:100%;">' + satirlar + '</table>')


# ============================================================
# SABLONLAR
# ============================================================

def sablon_kayit(ad, tc, sifre, giris_url):
    icerik = (
        _h1("Ho\u015f geldiniz, " + ad + "!")
        + _p("Hesab\u0131n\u0131z ba\u015far\u0131yla olu\u015fturuldu. "
             "A\u015fa\u011f\u0131daki bilgilerle sisteme giri\u015f yapabilirsiniz.")
        + _kutu(
            _tablo(
                _satir("T.C. Kimlik No", tc)
                + _satir("\u015eifre", sifre)
            ),
            arka="#f0fdf4", kenar="#16a34a"
        )
        + _buton("Sisteme Giri\u015f Yap", giris_url, "#16a34a")
        + _p("G\u00fcvenli\u011finiz i\u00e7in giri\u015f yapt\u0131ktan sonra "
             "\u015fifrenizi de\u011fi\u015ftirmenizi \u00f6neririz.", "#71717a")
    )
    return _sablon("Ho\u015f Geldiniz", icerik, "#16a34a", "linear-gradient(135deg,#16a34a,#22c55e)")


def sablon_sifre_talebi(ad, tc, email):
    icerik = (
        _h1("\u015eifre S\u0131f\u0131rlama Talebiniz Al\u0131nd\u0131")
        + _p("Merhaba " + ad + ",")
        + _p("\u015eifre s\u0131f\u0131rlama talebiniz ba\u015far\u0131yla al\u0131nd\u0131. "
             "Y\u00f6netim en k\u0131sa s\u00fcrede sizinle ileti\u015fime ge\u00e7ecek ve "
             "yeni \u015fifrenizi iletecektir.")
        + _kutu(_tablo(_satir("T.C. Kimlik No", tc)), arka="#fff7ed", kenar="#f59e0b")
        + _p("Bu talebi siz olu\u015fturmad\u0131ysan\u0131z bu e-postay\u0131 dikkate almay\u0131n.", "#71717a")
    )
    return _sablon("\u015eifre S\u0131f\u0131rlama", icerik, "#f59e0b", "linear-gradient(135deg,#f59e0b,#f97316)")


def sablon_sifre_degisti(ad, tc):
    icerik = (
        _h1("\u015eifreniz De\u011fi\u015ftirildi", "#dc2626")
        + _p("Merhaba " + ad + ",")
        + _p("Hesab\u0131n\u0131z\u0131n \u015fifresi az \u00f6nce ba\u015far\u0131yla de\u011fi\u015ftirildi.")
        + _kutu(_tablo(_satir("T.C. Kimlik No", tc)), arka="#fef2f2", kenar="#dc2626")
        + ('<div style="background:#fef2f2;border-radius:10px;padding:14px 18px;margin-top:16px;">'
           '<p style="margin:0;color:#dc2626;font-size:14px;font-weight:700;">'
           'Bu i\u015flemi siz yapmad\u0131ysan\u0131z l\u00fctfen derhal y\u00f6netime ula\u015f\u0131n.</p></div>')
    )
    return _sablon("G\u00fcvenlik Uyar\u0131s\u0131", icerik, "#dc2626", "linear-gradient(135deg,#dc2626,#ef4444)")


def sablon_sifre_sifirlandi(ad, yeni_sifre):
    icerik = (
        _h1("\u015eifreniz Yenilendi")
        + _p("Merhaba " + ad + ",")
        + _p("\u015eifreniz y\u00f6netim taraf\u0131ndan yenilendi. Yeni giri\u015f bilgileriniz:")
        + _kutu(_tablo(_satir("Yeni \u015eifre", yeni_sifre)), arka="#eff6ff", kenar="#2563eb")
        + _p("G\u00fcvenli\u011finiz i\u00e7in giri\u015f yapt\u0131ktan sonra \u015fifrenizi de\u011fi\u015ftirmenizi \u00f6neririz.", "#71717a")
    )
    return _sablon("\u015eifre Yenilendi", icerik, "#2563eb", "linear-gradient(135deg,#2563eb,#3b82f6)")


def sablon_devamsizlik(ogrenci_ad, sinif, tarih):
    icerik = (
        _h1("Devams\u0131zl\u0131k Bildirimi")
        + _p("Say\u0131n veli,")
        + _p("<b>" + ogrenci_ad + "</b> adl\u0131 \u00f6\u011frenci a\u015fa\u011f\u0131daki tarihte okula gelmemi\u015ftir.")
        + _kutu(_tablo(_satir("S\u0131n\u0131f", sinif) + _satir("Tarih", tarih)),
                arka="#fff7ed", kenar="#f59e0b")
        + _p("Bir hata oldu\u011funu d\u00fc\u015f\u00fcn\u00fcyorsan\u0131z l\u00fctfen okul y\u00f6netimiyle ileti\u015fime ge\u00e7in.", "#71717a")
    )
    return _sablon("Devams\u0131zl\u0131k", icerik, "#f59e0b", "linear-gradient(135deg,#f59e0b,#f97316)")


def sablon_not_girildi(ogrenci_ad, ders, sinav, puan):
    try:
        p = float(puan)
    except Exception:
        p = 0
    if p >= 85:
        renk = "#16a34a"; arka = "#f0fdf4"; durum = "Harika!"
    elif p >= 70:
        renk = "#0891b2"; arka = "#ecfeff"; durum = "\u0130yi"
    elif p >= 50:
        renk = "#d97706"; arka = "#fff7ed"; durum = "Ge\u00e7iyor"
    else:
        renk = "#dc2626"; arka = "#fef2f2"; durum = "D\u00fc\u015f\u00fck"
    icerik = (
        _h1("Yeni Notunuz A\u00e7\u0131kland\u0131")
        + _p("Merhaba " + ogrenci_ad + ",")
        + _p("<b>" + ders + "</b> dersinden <b>" + sinav + "</b> s\u0131nav\u0131n\u0131n sonucu a\u00e7\u0131kland\u0131:")
        + ('<div style="background:' + arka + ';padding:28px 20px;border-radius:14px;'
           'text-align:center;margin:20px 0;border-left:4px solid ' + renk + ';">'
           '<div style="font-size:52px;font-weight:800;color:' + renk + ';line-height:1;'
           'letter-spacing:-0.02em;">' + str(puan) + '</div>'
           '<div style="font-size:14px;color:' + renk + ';font-weight:700;margin-top:10px;'
           'text-transform:uppercase;letter-spacing:0.08em;">' + durum + '</div>'
           '</div>')
    )
    return _sablon("Not A\u00e7\u0131kland\u0131", icerik, renk, "linear-gradient(135deg," + renk + "," + renk + ")")


def sablon_test():
    icerik = (
        _h1("Test E-postas\u0131")
        + _p("Bu e-posta C-Peak Panel'in e-posta servisinin do\u011fru \u00e7al\u0131\u015ft\u0131\u011f\u0131n\u0131 do\u011frulamak i\u00e7in g\u00f6nderildi.")
        + _kutu(
            '<p style="margin:0;color:#16a34a;font-weight:700;font-size:15px;">'
            'E\u011fer bu e-postay\u0131 g\u00f6rd\u00fcyseniz, servis \u00e7al\u0131\u015f\u0131yor demektir.</p>',
            arka="#f0fdf4", kenar="#16a34a"
        )
        + _p("T\u00fcm mail \u015fablonlar\u0131 bu g\u00f6rsel kurumsal kimlik ile tasarlanm\u0131\u015ft\u0131r.", "#71717a")
    )
    return _sablon("Test", icerik, "#f59e0b", "linear-gradient(135deg,#f59e0b,#f97316)")


# ============================================================
# OZEL / SERBEST ICERIKLI MAIL
# ============================================================
def sablon_ozel(baslik, icerik_html, vurgu_renk="#f59e0b"):
    """Admin panelinden yazilan serbest icerikli mail.
    Logo, sosyal medya, adres sabit kalir; sadece icerik degisir.
    """
    govde = (
        _h1(baslik)
        + '<div style="font-size:15px;line-height:1.75;color:#52525b;">'
        + (icerik_html or "")
        + '</div>'
    )
    return _sablon(
        baslik, govde, vurgu_renk,
        "linear-gradient(135deg," + vurgu_renk + " 0%," + vurgu_renk + " 100%)"
    )


# ============================================================
# HAZIR SABLONLAR (admin panelden secilebilir)
# ============================================================
HAZIR_SABLONLAR = {
    "ozel": {
        "ad":     "Ozel Metin",
        "konu":   "",
        "icerik": "",
        "renk":   "#f59e0b",
    },
    "duyuru": {
        "ad":     "Duyuru",
        "konu":   "Yeni Duyuru",
        "icerik": (
            "<p>Sayin kullanici,"             "</p><p>Okulumuzla ilgili onemli bir duyurumuz bulunmaktadir:</p>"             "<p><b>[DUYURU ICERIGI]</b></p>"             "<p>Detayli bilgi icin lutfen okul yonetimi ile iletisime gecin.</p>"             "<p>Saygilarimizla,<br>C-Peak English</p>"
        ),
        "renk":   "#f59e0b",
    },
    "hatirlatma": {
        "ad":     "Hatirlatma",
        "konu":   "Hatirlatma",
        "icerik": (
            "<p>Sayin kullanici,</p>"             "<p>Asagidaki konu hakkinda size bir hatirlatma yapmak istiyoruz:</p>"             "<p><b>[HATIRLATMA KONUSU]</b></p>"             "<p>Konuyla ilgili gerekli islemleri en kisa surede tamamlamanizi rica ederiz.</p>"             "<p>Saygilarimizla,<br>C-Peak English</p>"
        ),
        "renk":   "#0891b2",
    },
    "kutlama": {
        "ad":     "Kutlama / Tebrik",
        "konu":   "Tebrikler",
        "icerik": (
            "<p>Sevgili ogrencimiz,</p>"             "<p>Gosterdiginiz basaridan dolayi sizi tebrik ederiz.</p>"             "<p><b>[BASARI DETAYI]</b></p>"             "<p>Basari ve mutluluklarinizin devamini dileriz.</p>"             "<p>Saygilarimizla,<br>C-Peak English</p>"
        ),
        "renk":   "#16a34a",
    },
    "bilgilendirme": {
        "ad":     "Bilgilendirme",
        "konu":   "Bilgilendirme",
        "icerik": (
            "<p>Sayin kullanici,</p>"             "<p>Asagidaki konuda sizi bilgilendirmek istiyoruz:</p>"             "<p><b>[BILGILENDIRME ICERIGI]</b></p>"             "<p>Saygilarimizla,<br>C-Peak English</p>"
        ),
        "renk":   "#2563eb",
    },
    "tesekkur": {
        "ad":     "Tesekkur",
        "konu":   "Tesekkurler",
        "icerik": (
            "<p>Sayin kullanici,</p>"             "<p>Gosterdiginiz ilgi ve emek icin tesekkur ederiz.</p>"             "<p><b>[TESSEKKUR NOTU]</b></p>"             "<p>Saygilarimizla,<br>C-Peak English</p>"
        ),
        "renk":   "#7c3aed",
    },
}
