# -*- coding: utf-8 -*-
"""Merkezi guvenlik modulu. app.py'de init_security(app) cagrilir."""
import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler

from flask import request, abort, render_template


def _uretilen_secret():
    import secrets as _s
    return _s.token_urlsafe(48)


def init_security(app):
    """Tum guvenlik katmanlarini uygular."""

    # Logging en basta
    import logging
    app.logger.setLevel(logging.INFO)

    # Flask 2.3+ FLASK_ENV'i kaldirdi; app.debug ve FLASK_DEBUG kontrol edilir
    _flask_env = (os.environ.get("FLASK_ENV") or "").lower()
    _flask_debug = (os.environ.get("FLASK_DEBUG") or "").lower() in ("1","true","yes","on")
    _gercek_debug = bool(getattr(app, "debug", False)) or _flask_debug or _flask_env == "development"
    # --- Mod tespiti ---
    # Varsayilan: DEVELOPMENT. Production sadece acikca belirtilirse aktif olur.
    # Sinyaller:
    #   production: FLASK_ENV=production | FLASK_DEBUG=0/false | gunicorn/uwsgi
    #   development: python app.py | FLASK_DEBUG=1 | app.debug=True
    import sys as _sys

    _env    = (os.environ.get("FLASK_ENV") or "").lower()
    _dbg    = (os.environ.get("FLASK_DEBUG") or "").lower()
    _argv   = " ".join(_sys.argv).lower()
    _wsgi   = any(x in _argv for x in ("gunicorn", "uwsgi", "waitress"))

    _prod_sinyal = (
        _env == "production"
        or _dbg in ("0", "false", "no", "off")
        or _wsgi
    )
    _dev_sinyal = (
        _env in ("development", "dev")
        or _dbg in ("1", "true", "yes", "on")
        or getattr(app, "debug", False) is True
    )

    if _prod_sinyal and not _dev_sinyal:
        uretim = True
    else:
        uretim = False
    # --------------------

    # ---------- 0) Temel config ----------
    app.config.update(
        SESSION_COOKIE_SECURE=uretim,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=4 * 1024 * 1024,   # 4 MB
        JSON_SORT_KEYS=False,
        TEMPLATES_AUTO_RELOAD=not uretim,
    )

    # ---------- 1) SECRET_KEY ----------
    secret = os.environ.get("SECRET_KEY", "").strip()
    if len(secret) < 32:
        if uretim:
            raise RuntimeError(
                "SECRET_KEY ortam degiskeni tanimli ve >=32 karakter olmali. "
                "Ornek: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
        secret = _uretilen_secret()
        app.logger.warning("SECRET_KEY yok, dev icin gecici anahtar uretildi")
    app.secret_key = secret

    # ---------- 2) ProxyFix (Nginx arkasinda dogru IP/protokol) ----------
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )
    except Exception as e:
        app.logger.warning("ProxyFix yuklenemedi: %s", e)

    # ---------- 3) Talisman: HTTPS, HSTS, CSP ----------
    try:
        from flask_talisman import Talisman

        # CSP: site icerigi inline style/script kullaniyorsa unsafe-inline sart.
        # Dis kaynak yuklemiyorsan asagidaki liste guvenli.
        csp = {
            "default-src": "'self'",
            "script-src": [
                "'self'",
                "'unsafe-inline'",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
                "https://fonts.googleapis.com",
            ],
            "font-src": [
                "'self'",
                "data:",
                "https://fonts.gstatic.com",
            ],
            "img-src": [
                "'self'",
                "data:",
                "https:",
            ],
            "connect-src": ["'self'"],
            "frame-ancestors": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
            "object-src": "'none'",
        }

        Talisman(
            app,
            force_https=uretim,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            strict_transport_security_include_subdomains=True,
            strict_transport_security_preload=True,
            content_security_policy=csp,
            referrer_policy="strict-origin-when-cross-origin",
            feature_policy={
                "geolocation": "'none'",
                "camera": "'none'",
                "microphone": "'none'",
                "payment": "'none'",
                "usb": "'none'",
            },
            session_cookie_secure=uretim,
            frame_options="DENY",
        )
        app.logger.info("Talisman aktif (HTTPS/HSTS/CSP)")
    except ImportError:
        app.logger.warning("flask-talisman yok, atlandi")

    # ---------- 4) CSRF ----------
    try:
        from flask_wtf.csrf import CSRFProtect
        CSRFProtect(app)
        app.logger.info("CSRF korumasi aktif")
    except ImportError:
        app.logger.warning("flask-wtf yok, atlandi")

    # ---------- 5) Rate Limiting ----------
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=["200 per day", "60 per hour"],
            storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
            headers_enabled=True,
            strategy="fixed-window",
            default_limits_exempt_when=lambda: False,
        )
        app.limiter = limiter
        app.logger.info("Rate limiting aktif")

        # Login rotasina ozel sikilastirma
        # app.py'de kullanim: @app.limiter.limit("5 per minute")
    except ImportError:
        app.logger.warning("flask-limiter yok, atlandi")

    # ---------- 6) Loglama ----------
    if not app.debug:
        os.makedirs("logs", exist_ok=True)
        handler = RotatingFileHandler(
            "logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=10,
            encoding="utf-8",
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        if not app.logger.handlers:
            app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    # ---------- 7) Host header kontrolu ----------
    @app.before_request
    def _host_kontrol():
        izinli = [h.strip().lower() for h in
                  os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
        if izinli:
            gelen = (request.host or "").split(":")[0].lower()
            if gelen not in izinli:
                app.logger.warning("Gecersiz Host header: %s", gelen)
                abort(400)

    # ---------- 8) Hata sayfalari ----------
    def _hata(kod, baslik, mesaj):
        def handler(e):
            if kod >= 500:
                import traceback as _tb, sys as _sys2
                # Hem log'a hem stdout'a
                app.logger.exception("%s: %s", kod, e)
                print(f"=== 500 HATA ===", file=_sys2.stderr, flush=True)
                _tb.print_exception(type(e), e, e.__traceback__,
                                    file=_sys2.stderr)
                print(f"=== /500 HATA ===", file=_sys2.stderr, flush=True)
            try:
                return render_template(f"errors/{kod}.html",
                                       baslik=baslik, mesaj=mesaj), kod
            except Exception:
                return f"<h1>{kod} {baslik}</h1><p>{mesaj}</p>", kod
        return handler

    app.register_error_handler(400, _hata(400, "Geçersiz istek",
        "İstek doğrulanamadı. Sayfayı yenileyip tekrar deneyin."))
    app.register_error_handler(403, _hata(403, "Erişim reddedildi",
        "Bu sayfaya erisim yetkiniz yok."))
    app.register_error_handler(404, _hata(404, "Sayfa bulunamadı",
        "Aradığınız sayfa taşınmış veya hiç var olmamış olabilir."))
    app.register_error_handler(429, _hata(429, "Çok fazla istek",
        "Kısa süre içinde cok fazla istek gönderdiniz. Lütfen bekleyin."))
    app.register_error_handler(500, _hata(500, "Sunucu hatası",
        "Beklenmeyen bir hata oluştu. Ekibimiz bilgilendirildi."))

    app.logger.info("Guvenlik katmanlari hazir (uretim=%s)", uretim)
    return app
