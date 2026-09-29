# -*- coding: utf-8 -*-
"""Brevo (Sendinblue) API ile e-posta gönderimi."""
import os
from brevo import Brevo
from brevo.transactional_emails import SendSmtpEmail

def send_email(konu, alici, html, duz_metin=None):
    """Brevo üzerinden e-posta gönderir."""
    api_key = os.environ.get("BREVO_API_KEY")
    if not api_key:
        print("[Brevo] HATA: BREVO_API_KEY tanimli degil.", flush=True)
        return False
    
    try:
        brevo = Brevo(api_key=api_key)
        
        # Alıcı listesini hazırla
        if isinstance(alici, str):
            alicilar = [{"email": alici}]
        else:
            alicilar = [{"email": e} for e in alici]
        
        # Gönderici bilgisi
        gonderen_email = os.environ.get("MAIL_DEFAULT_SENDER")
        gonderen_isim = os.environ.get("MAIL_SENDER_NAME", "C-Peak Panel")
        
        # E-posta objesi oluştur
        email = SendSmtpEmail(
            to=alicilar,
            sender={"name": gonderen_isim, "email": gonderen_email},
            subject=konu,
            html_content=html,
            text_content=duz_metin if duz_metin else None
        )
        
        # Gönder
        response = brevo.transactional_emails.send_transac_email(email)
        print(f"[Brevo] E-posta gönderildi: {response}", flush=True)
        return True
        
    except Exception as e:
        print(f"[Brevo] HATA: {e}", flush=True)
        return False