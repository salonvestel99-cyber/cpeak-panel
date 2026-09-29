# -*- coding: utf-8 -*-
"""test-email endpoint'ini render_template_string ile duzeltir (CSRF calissin)."""
import os, re, shutil, datetime

KOK = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(KOK, "app.py")
YED = os.path.join(KOK, "backups")
os.makedirs(YED, exist_ok=True)
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

shutil.copy2(APP, os.path.join(YED, f"app.py.{stamp}.bak"))
print(f"[YEDEK] backups/app.py.{stamp}.bak")

with open(APP, "r", encoding="utf-8") as f:
    ac = f.read()

PATTERN = re.compile(
    r'@app\.route\("/admin/test-email".*?(?=\n@app\.route|\nif\s+__name__)',
    re.DOTALL
)

# render_template_string KULLAN - boylece {{ csrf_token() }} render edilir
YENI_ENDPOINT = '''@app.route("/admin/test-email", methods=["GET", "POST"])
@login_required("admin")
def admin_test_email():
    from flask import Response as _R, render_template_string as _rts

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

    html = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Test E-postasi</title>
</head>
<body style="font-family:system-ui,sans-serif;background:#fafaf9;margin:0;display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px;">
  <form method="POST" style="background:#fff;padding:28px;border-radius:14px;box-shadow:0 4px 20px rgba(0,0,0,0.06);max-width:440px;width:100%;">
    <h2 style="margin:0 0 8px;color:#18181b;">Test E-postasi</h2>
    <p style="margin:0 0 20px;color:#71717a;font-size:14px;">Kendi e-posta adresinize test mesaji gonderin.</p>
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="email" name="email" placeholder="ornek@mail.com" required
           style="width:100%;padding:12px 14px;border:1px solid #d4d4d8;border-radius:10px;font-size:16px;box-sizing:border-box;">
    <button type="submit" style="margin-top:14px;padding:12px 24px;background:#f59e0b;color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;cursor:pointer;width:100%;">Gonder</button>
    <p style="margin:16px 0 0;font-size:13px;color:#a1a1aa;text-align:center;">
      <a href="/admin" style="color:#71717a;">Admin panele don</a>
    </p>
  </form>
</body>
</html>"""
    return _rts(html)
'''

sayi = 0
while PATTERN.search(ac) and sayi < 5:
    ac = PATTERN.sub(YENI_ENDPOINT, ac, count=1)
    sayi += 1

if sayi:
    with open(APP, "w", encoding="utf-8") as f:
        f.write(ac)
    print(f"[OK] {sayi} adet /admin/test-email blogu render_template_string ile degistirildi")
else:
    print("[UYARI] /admin/test-email blogu bulunamadi")

print("""
============================================================
SIMDI:
1. py -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('OK')"
   -> 'OK' gormelisin. Hata varsa PUSH ETME, bana gonder.
2. git add app.py
3. git commit -m "test-email CSRF render_template_string ile duzeltildi"
4. git push
5. Deploy bitince TEKRAR DENE
============================================================
""")