# -*- coding: utf-8 -*-
"""
security_headers.py — Ek HTTP güvenlik başlıkları.

app.py'de init_security(app)'ten sonra çağrılır:
    from security_headers import init_headers
    init_headers(app)
"""
from flask import request, session


def init_headers(app):

    AUTH_PREFIXES = (
        "/admin", "/panel", "/dashboard", "/ogrenci", "/ogretmen", "/veli",
        "/ders", "/odev", "/bildirim", "/devamsizlik", "/not-",
        "/sifre", "/mail", "/talep",
    )

    @app.after_request
    def _guvenlik_basliklari(resp):
        path = request.path or ""
        statik_mi = path.startswith("/static/")
        auth_var = bool(session.get("user_id"))

        # ---------- Cache-Control ----------
        if statik_mi:
            resp.headers.setdefault(
                "Cache-Control",
                "public, max-age=31536000, immutable",
            )
        elif auth_var or any(path.startswith(p) for p in AUTH_PREFIXES):
            resp.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, "
                "max-age=0, private"
            )
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
        else:
            resp.headers.setdefault("Cache-Control", "no-cache, private")

        # ---------- Cross-Origin-Resource-Policy ----------
        resp.headers.setdefault(
            "Cross-Origin-Resource-Policy", "same-origin"
        )

        # ---------- Ek dayanıklılık (Talisman varsa da zararsız) ----------
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        resp.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=()",
        )

        
        # ---------- Content-Security-Policy ----------
        # 'unsafe-inline' style zorunlu (tema toggle, inline <style> blokları)
        # 'unsafe-inline' script YOK → XSS'i büyük ölçüde engeller
        if not resp.headers.get("Content-Security-Policy"):
            resp.headers["Content-Security-Policy"] = "; ".join([
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.sib.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com data:",
                "img-src 'self' data: https:",
                "connect-src 'self' https://api.brevo.com https://*.supabase.co",
                "frame-src 'self' https://www.openstreetmap.org https://www.google.com",
                "frame-ancestors 'self'",
                "base-uri 'self'",
                "form-action 'self'",
                "object-src 'none'",
            ])

        return resp
