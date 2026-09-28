# -*- coding: utf-8 -*-
"""
kur.py — Tek seferlik kurulum.

Eski dosyaları siler, yeni Flask backend'ini kurar,
bağımlılıkları yükler, veritabanını hazırlar.

Kullanım:
    py kur.py
"""

import os
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
os.chdir(KOK)

# ============================================================
# TEMİZLİK
# ============================================================

print("\n" + "=" * 60)
print("  C · PEAK ENGLISH — KURULUM")
print("=" * 60 + "\n")

print("[1/6] Eski dosyalar temizleniyor...")

eski_dosyalar = ["app.py", "run.py", "database.py", "seed.py", "models.py", "egitim.db"]
for f in eski_dosyalar:
    p = os.path.join(KOK, f)
    if os.path.exists(p):
        try:
            os.remove(p)
            print(f"  ✓ silindi: {f}")
        except Exception as e:
            print(f"  ! silinemedi {f}: {e}")

eski_klasorler = ["templates", "static/css", "__pycache__", "migrations/__pycache__"]
for d in eski_klasorler:
    p = os.path.join(KOK, d)
    if os.path.isdir(p):
        try:
            shutil.rmtree(p)
            print(f"  ✓ silindi: {d}/")
        except Exception as e:
            print(f"  ! silinemedi {d}/: {e}")


# ============================================================
# YARDIMCI
# ============================================================

def yaz(yol, icerik):
    tam = os.path.join(KOK, yol)
    os.makedirs(os.path.dirname(tam) or KOK, exist_ok=True)
    with open(tam, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)
    print(f"  ✓ {yol}")


# ============================================================
# DOSYALARI YAZ
# ============================================================

print("\n[2/6] Backend dosyaları yazılıyor...")

yaz("requirements.txt", "Flask==3.0.3\npython-dotenv==1.0.1\ngunicorn==22.0.0\n")

yaz(".env.example", """# Bu dosyayı .env olarak kopyalayın ve değerleri değiştirin.
SECRET_KEY=degistir-bunu-rastgele-uzun-bir-yazi-yap
ADMIN_TC=11111111111
ADMIN_PASSWORD=admin123
ADMIN_NAME=Sistem Yoneticisi
DB_PATH=egitim.db
""")

yaz(".gitignore", """__pycache__/
*.py[cod]
.venv/
venv/
env/
.env
*.db
egitim.db
_backups/
_applied.json
.vscode/
.idea/
.DS_Store
""")

yaz("run.py", '''# -*- coding: utf-8 -*-
"""Geliştirme sunucusunu başlatır."""

import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from models import init_db, seed_admin

if __name__ == "__main__":
    init_db()
    seed_admin()
    print("\\n  >>> http://127.0.0.1:5000  adresinden acabilirsiniz.\\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
''')

yaz("models.py", '''# -*- coding: utf-8 -*-
"""SQLite veritabani katmani."""

import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "egitim.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tc_no TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student','parent','teacher','admin')),
    student_id INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    sinif TEXT NOT NULL,
    numara INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT NOT NULL,
    ogretmen_id INTEGER,
    FOREIGN KEY(ogretmen_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    sinav TEXT NOT NULL,
    puan REAL NOT NULL,
    tarih TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    tarih TEXT NOT NULL,
    durum TEXT NOT NULL CHECK(durum IN ('geldi','gelmedi','izinli')),
    aciklama TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baslik TEXT NOT NULL,
    icerik TEXT NOT NULL,
    tarih TEXT NOT NULL,
    yazar_id INTEGER,
    FOREIGN KEY(yazar_id) REFERENCES users(id) ON DELETE SET NULL
);
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def seed_admin():
    from werkzeug.security import generate_password_hash
    tc = os.environ.get("ADMIN_TC", "11111111111")
    sifre = os.environ.get("ADMIN_PASSWORD", "admin123")
    ad = os.environ.get("ADMIN_NAME", "Sistem Yoneticisi")
    conn = get_db()
    var = conn.execute("SELECT 1 FROM users WHERE tc_no = ?", (tc,)).fetchone()
    if var:
        conn.close()
        return
    conn.execute(
        "INSERT INTO users (tc_no, password_hash, name, role, student_id) VALUES (?,?,?,?,?)",
        (tc, generate_password_hash(sifre), ad, "admin", None)
    )
    conn.commit()
    conn.close()
    print(f"  [seed] Admin olusturuldu -> T.C.: {tc}  |  Sifre: {sifre}")
''')

yaz("app.py", '''# -*- coding: utf-8 -*-
"""Ana Flask uygulamasi."""

import os
from datetime import date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

from models import get_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


def login_required(role=None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Bu sayfaya erisim yetkiniz yok.", "error")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return deco


def _ogrenci_verisi(student_id):
    conn = get_db()
    notlar = conn.execute("""
        SELECT c.ad AS ders, g.sinav, g.puan
        FROM grades g JOIN courses c ON c.id = g.course_id
        WHERE g.student_id = ?
        ORDER BY c.ad, g.id
    """, (student_id,)).fetchall()
    att = conn.execute("""
        SELECT durum, COUNT(*) AS adet FROM attendance
        WHERE student_id = ? GROUP BY durum
    """, (student_id,)).fetchall()
    duyurular = conn.execute("""
        SELECT baslik, icerik, tarih FROM announcements
        ORDER BY tarih DESC, id DESC LIMIT 10
    """).fetchall()
    conn.close()

    dersler = {}
    for n in notlar:
        dersler.setdefault(n["ders"], []).append({"sinav": n["sinav"], "puan": n["puan"]})

    dev = {"toplam": 0, "izinli": 0, "gelmedi": 0}
    for a in att:
        dev["toplam"] += a["adet"]
        if a["durum"] == "izinli":
            dev["izinli"] = a["adet"]
        elif a["durum"] == "gelmedi":
            dev["gelmedi"] = a["adet"]

    ort_list = [sum(x["puan"] for x in s) / len(s) for s in dersler.values() if s]
    ortalama = round(sum(ort_list) / len(ort_list), 2) if ort_list else 0

    return {"dersler": dersler, "devamsizlik": dev,
            "duyurular": [dict(d) for d in duyurular], "ortalama": ortalama}


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/giris", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tc = request.form.get("tc", "").strip()
        sifre = request.form.get("sifre", "")
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE tc_no = ?", (tc,)).fetchone()
        conn.close()
        if u and check_password_hash(u["password_hash"], sifre):
            session["user_id"] = u["id"]
            session["role"] = u["role"]
            session["name"] = u["name"]
            session["student_id"] = u["student_id"]
            return redirect(url_for("dashboard"))
        flash("T.C. kimlik no veya sifre hatali.", "error")
    return render_template("login.html")


@app.route("/cikis")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/panel")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for({
        "student": "student_panel",
        "parent": "parent_panel",
        "teacher": "teacher_panel",
        "admin": "admin_panel",
    }[session["role"]]))


@app.route("/ogrenci")
@login_required("student")
def student_panel():
    conn = get_db()
    s = conn.execute("SELECT * FROM students WHERE user_id = ?", (session["user_id"],)).fetchone()
    conn.close()
    if not s:
        flash("Ogrenci kaydiniz bulunamadi.", "error")
        return redirect(url_for("logout"))
    data = _ogrenci_verisi(s["id"])
    return render_template("student.html", ogrenci=dict(s), **data)


@app.route("/veli")
@login_required("parent")
def parent_panel():
    sid = session.get("student_id")
    if not sid:
        flash("Veliye bagli ogrenci bulunamadi.", "error")
        return redirect(url_for("logout"))
    conn = get_db()
    s = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    if not s:
        conn.close()
        return redirect(url_for("logout"))
    ogr_u = conn.execute("SELECT name FROM users WHERE id = ?", (s["user_id"],)).fetchone()
    conn.close()
    data = _ogrenci_verisi(sid)
    return render_template("parent.html", ogrenci=dict(s), ogrenci_ad=ogr_u["name"], **data)


@app.route("/ogretmen")
@login_required("teacher")
def teacher_panel():
    conn = get_db()
    dersler = conn.execute("SELECT * FROM courses WHERE ogretmen_id = ? ORDER BY ad",
                           (session["user_id"],)).fetchall()
    ogrenciler = conn.execute("""
        SELECT s.id, u.name AS ad, s.sinif, s.numara
        FROM students s JOIN users u ON u.id = s.user_id
        ORDER BY s.sinif, s.numara
    """).fetchall()
    conn.close()
    return render_template("teacher.html",
                           dersler=[dict(d) for d in dersler],
                           ogrenciler=[dict(o) for o in ogrenciler])


@app.route("/admin")
@login_required("admin")
def admin_panel():
    conn = get_db()
    sayilar = {
        "ogrenci": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "ogretmen": conn.execute("SELECT COUNT(*) FROM users WHERE role='teacher'").fetchone()[0],
        "veli": conn.execute("SELECT COUNT(*) FROM users WHERE role='parent'").fetchone()[0],
        "ders": conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
        "not": conn.execute("SELECT COUNT(*) FROM grades").fetchone()[0],
        "devamsizlik": conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0],
    }
    ogrenciler = conn.execute("""
        SELECT s.id, u.name AS ad, u.tc_no, s.sinif, s.numara
        FROM students s JOIN users u ON u.id = s.user_id
        ORDER BY s.sinif, s.numara
    """).fetchall()
    ogretmenler = conn.execute(
        "SELECT id, name, tc_no FROM users WHERE role='teacher' ORDER BY name"
    ).fetchall()
    dersler = conn.execute("""
        SELECT c.id, c.ad, u.name AS ogretmen
        FROM courses c LEFT JOIN users u ON u.id = c.ogretmen_id
        ORDER BY c.ad
    """).fetchall()
    conn.close()
    return render_template("admin.html", sayilar=sayilar,
                           ogrenciler=[dict(o) for o in ogrenciler],
                           ogretmenler=[dict(o) for o in ogretmenler],
                           dersler=[dict(d) for d in dersler])


@app.route("/admin/ogrenci-ekle", methods=["POST"])
@login_required("admin")
def admin_add_student():
    ad = request.form.get("ad", "").strip()
    tc = request.form.get("tc", "").strip()
    sifre = request.form.get("sifre", "").strip()
    sinif = request.form.get("sinif", "").strip()
    numara = request.form.get("numara", "").strip()
    if not (ad and tc and sifre and sinif and numara):
        flash("Tum alanlar zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (tc_no, password_hash, name, role) VALUES (?,?,?,?)",
                    (tc, generate_password_hash(sifre), ad, "student"))
        uid = cur.lastrowid
        cur.execute("INSERT INTO students (user_id, sinif, numara) VALUES (?,?,?)",
                    (uid, sinif, int(numara)))
        sid = cur.lastrowid
        v_ad = request.form.get("veli_ad", "").strip()
        v_tc = request.form.get("veli_tc", "").strip()
        v_sifre = request.form.get("veli_sifre", "").strip()
        if v_ad and v_tc and v_sifre:
            cur.execute("INSERT INTO users (tc_no, password_hash, name, role, student_id) VALUES (?,?,?,?,?)",
                        (v_tc, generate_password_hash(v_sifre), v_ad, "parent", sid))
        conn.commit()
        flash(f"Ogrenci eklendi: {ad}", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))


@app.route("/admin/ogretmen-ekle", methods=["POST"])
@login_required("admin")
def admin_add_teacher():
    ad = request.form.get("ad", "").strip()
    tc = request.form.get("tc", "").strip()
    sifre = request.form.get("sifre", "").strip()
    if not (ad and tc and sifre):
        flash("Tum alanlar zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (tc_no, password_hash, name, role) VALUES (?,?,?,?)",
                     (tc, generate_password_hash(sifre), ad, "teacher"))
        conn.commit()
        flash(f"Ogretmen eklendi: {ad}", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))


@app.route("/admin/ders-ekle", methods=["POST"])
@login_required("admin")
def admin_add_course():
    ad = request.form.get("ad", "").strip()
    ogr_id = request.form.get("ogretmen_id") or None
    if not ad:
        flash("Ders adi zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO courses (ad, ogretmen_id) VALUES (?,?)",
                     (ad, int(ogr_id) if ogr_id else None))
        conn.commit()
        flash(f"Ders eklendi: {ad}", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))


@app.route("/admin/not-ekle", methods=["POST"])
@login_required("admin")
def admin_add_grade():
    sid = request.form.get("student_id")
    cid = request.form.get("course_id")
    sinav = request.form.get("sinav", "").strip()
    puan = request.form.get("puan", "").strip()
    if not (sid and cid and sinav and puan):
        flash("Tum alanlar zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO grades (student_id, course_id, sinav, puan, tarih) VALUES (?,?,?,?,?)",
                     (int(sid), int(cid), sinav, float(puan), date.today().isoformat()))
        conn.commit()
        flash(f"Not eklendi: {sinav} = {puan}", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))


@app.route("/admin/devamsizlik-ekle", methods=["POST"])
@login_required("admin")
def admin_add_attendance():
    sid = request.form.get("student_id")
    tarih = request.form.get("tarih", "").strip()
    durum = request.form.get("durum", "").strip()
    aciklama = request.form.get("aciklama", "").strip()
    if not (sid and tarih and durum):
        flash("Ogrenci, tarih ve durum zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO attendance (student_id, tarih, durum, aciklama) VALUES (?,?,?,?)",
                     (int(sid), tarih, durum, aciklama or None))
        conn.commit()
        flash("Devamsizlik kaydi eklendi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))


@app.route("/admin/duyuru-ekle", methods=["POST"])
@login_required("admin")
def admin_add_announcement():
    baslik = request.form.get("baslik", "").strip()
    icerik = request.form.get("icerik", "").strip()
    if not (baslik and icerik):
        flash("Baslik ve icerik zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO announcements (baslik, icerik, tarih, yazar_id) VALUES (?,?,?,?)",
                     (baslik, icerik, date.today().strftime("%d.%m.%Y"), session["user_id"]))
        conn.commit()
        flash("Duyuru yayinlandi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))


@app.route("/admin/sil/<tip>/<int:oid>", methods=["POST"])
@login_required("admin")
def admin_delete(tip, oid):
    conn = get_db()
    try:
        if tip == "ogrenci":
            conn.execute("DELETE FROM users WHERE id = (SELECT user_id FROM students WHERE id = ?)", (oid,))
        elif tip == "ogretmen":
            conn.execute("DELETE FROM users WHERE id = ? AND role='teacher'", (oid,))
        elif tip == "ders":
            conn.execute("DELETE FROM courses WHERE id = ?", (oid,))
        elif tip == "duyuru":
            conn.execute("DELETE FROM announcements WHERE id = ?", (oid,))
        conn.commit()
        flash("Kayit silindi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))
''')


# ============================================================
# TEMPLATES
# ============================================================

print("\n[3/6] HTML sablonlari yaziliyor...")

yaz("templates/base.html", """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{% block title %}C · Peak English{% endblock %}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='hero.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='panel.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='login.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='admin.css') }}">
{% block head %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
{% block body %}
<header class="topbar">
  <div class="container topbar-inner">
    <a href="{{ url_for('dashboard') }}" class="brand">C · Peak English</a>
    <div class="menu">
      <span class="user">{{ session.name }}</span>
      <a href="{{ url_for('logout') }}" class="btn-ghost">Cikis</a>
    </div>
  </div>
</header>
<main class="container">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for cat, msg in messages %}
      <div class="alert alert-{{ 'error' if cat == 'error' else 'success' }}">{{ msg }}</div>
    {% endfor %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
{% endblock %}
</body>
</html>
""")

yaz("templates/login.html", """{% extends "base.html" %}
{% block title %}Giris Yap{% endblock %}
{% block body_class %}login-page{% endblock %}
{% block body %}
<div class="login-wrap">
  <aside class="login-hero">
    <div class="hero-content">
      <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        <span class="hero-eyebrow-text">INGILIZCE EGITIM MERKEZI</span>
      </div>
      <div class="hero-brand">
        <div class="hero-brand-mark">
          <img src="{{ url_for('static', filename='logo.png') }}" alt="C Peak English">
        </div>
        <div class="hero-brand-text">
          <span class="hero-brand-title">C-Peak</span>
          <span class="hero-brand-sub" lang="en">ENGLISH</span>
        </div>
      </div>
      <h1>Zirveye giden yol,<br>Ingilizceden gecer.</h1>
      <p class="hero-lead">Ogrenci, veli ve ogretmenler icin tek panelde not, devamsizlik ve duyuru takibi.</p>
      <ul class="hero-list">
        <li>Notlarini aninda gor</li>
        <li>Devamsizligini takip et</li>
        <li>Duyurulari kacirma</li>
      </ul>
      <div class="hero-stats">
        <div class="hero-stat"><strong>150<em>+</em></strong><span>Mutlu Ogrenci</span></div>
        <div class="hero-stat"><strong>Kucuk</strong><span>Sinif Mevcudu</span></div>
        <div class="hero-stat"><strong>A1-C1</strong><span>CEFR Uyumlu</span></div>
      </div>
    </div>
    <div class="hero-orb"></div>
  </aside>

  <main class="login-main">
    <div class="login-card">
      <h2>Hos geldin</h2>
      <p class="lead">T.C. kimlik numaran ve sifrenle giris yap.</p>
      {% with messages = get_flashed_messages(with_categories=true) %}
        {% for cat, msg in messages %}
          <div class="alert alert-{{ 'error' if cat == 'error' else 'success' }}">{{ msg }}</div>
        {% endfor %}
      {% endwith %}
      <form method="post" action="{{ url_for('login') }}" autocomplete="off">
        <label>
          <span>T.C. Kimlik No</span>
          <input type="text" name="tc" id="tcInput" inputmode="numeric" maxlength="11" placeholder="11 haneli kimlik no" required autofocus>
        </label>
        <label>
          <span>Sifre</span>
          <div class="input-wrap">
            <input type="password" name="sifre" id="sifreInput" placeholder="********" required>
            <button type="button" id="togglePw" class="input-eye" aria-label="Sifreyi goster">
              <svg class="eye-open" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg class="eye-closed" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </label>
        <button type="submit" class="btn-primary">Giris Yap</button>
      </form>
      <p class="muted small" style="text-align:center;margin-top:18px">Sifrenizi bilmiyorsaniz okul yonetimine basvurun.</p>
    </div>
  </main>
</div>
<script>
document.getElementById("tcInput").addEventListener("input", function(e){
  var v = e.target.value.replace(/[^0-9]/g, "");
  if (v.length > 11) v = v.slice(0, 11);
  e.target.value = v;
});
var pw = document.getElementById("sifreInput");
document.getElementById("togglePw").addEventListener("click", function(){
  var g = pw.type === "password";
  pw.type = g ? "text" : "password";
  this.classList.toggle("is-visible", g);
});
</script>
{% endblock %}
""")

yaz("templates/student.html", """{% extends "base.html" %}
{% block title %}Ogrenci Paneli{% endblock %}
{% block content %}
<div class="panel-hero">
  <div class="panel-hero-text">
    <div class="panel-hero-greet">Merhaba, {{ session.name }} 👋</div>
    <div class="panel-hero-sub">{{ ogrenci.sinif }} · {{ ogrenci.numara }} numarali ogrenci</div>
  </div>
  <div class="panel-hero-avatar">{{ session.name[0]|upper }}</div>
</div>

<div class="stat-grid">
  <div class="stat-card devamsizlik {% if devamsizlik.toplam <= 5 %}durum-iyi{% elif devamsizlik.toplam <= 10 %}durum-dikkat{% elif devamsizlik.toplam <= 15 %}durum-uyari{% else %}durum-kritik{% endif %}">
    <div class="stat-card-head"><span class="stat-card-ico">📅</span><span class="stat-card-etiket">Devamsizlik</span></div>
    <div class="stat-card-deger">{{ devamsizlik.toplam }} <small>gun</small></div>
    <div class="progress"><div class="progress-bar" style="width:{{ [100, (devamsizlik.toplam / 20 * 100)]|min }}%"></div></div>
    <div class="stat-card-alt">
      <span><span class="dot ozurlu"></span>Izinli: {{ devamsizlik.izinli }}</span>
      <span><span class="dot ozursuz"></span>Gelmedi: {{ devamsizlik.gelmedi }}</span>
    </div>
  </div>
  <div class="stat-card">
    <div class="stat-card-head"><span class="stat-card-ico">📊</span><span class="stat-card-etiket">Ortalama</span></div>
    <div class="stat-card-deger">{{ ortalama }}</div>
    <div class="stat-card-alt">{{ dersler|length }} ders</div>
  </div>
  <div class="stat-card">
    <div class="stat-card-head"><span class="stat-card-ico">📢</span><span class="stat-card-etiket">Duyuru</span></div>
    <div class="stat-card-deger">{{ duyurular|length }}</div>
    <div class="stat-card-alt">Guncel</div>
  </div>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📚</span> Notlarim</h3></div>
  {% if dersler %}
  <div class="ders-grid">
    {% for ders, sinavlar in dersler.items() %}
      {% set ort = (sinavlar|map(attribute='puan')|sum) / (sinavlar|length) %}
      <div class="ders-card">
        <div class="ders-head"><span class="ders-ad">{{ ders }}</span><span class="ders-harf">{{ ort|round(1) }}</span></div>
        <div class="ders-chips">{% for s in sinavlar %}<span class="sinav-chip"><em>{{ s.sinav }}</em>{{ s.puan }}</span>{% endfor %}</div>
        <div class="ders-bar"><div class="ders-bar-fill" style="width:{{ ort }}%"></div></div>
      </div>
    {% endfor %}
  </div>
  {% else %}<p class="muted">Henuz not kaydi yok.</p>{% endif %}
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📢</span> Duyurular</h3></div>
  {% if duyurular %}
  <div class="timeline">
    {% for d in duyurular %}
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-body">
        <div class="timeline-head"><strong>{{ d.baslik }}</strong><span class="timeline-tarih">{{ d.tarih }}</span></div>
        <p>{{ d.icerik }}</p>
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}<p class="muted">Duyuru yok.</p>{% endif %}
</div>
{% endblock %}
""")

yaz("templates/parent.html", """{% extends "base.html" %}
{% block title %}Veli Paneli{% endblock %}
{% block content %}
<div class="panel-hero">
  <div class="panel-hero-text">
    <div class="panel-hero-greet">Hos geldiniz, {{ session.name }}</div>
    <div class="panel-hero-sub">Ogrenciniz: {{ ogrenci_ad }} · {{ ogrenci.sinif }} / {{ ogrenci.numara }}</div>
  </div>
  <div class="panel-hero-avatar">{{ session.name[0]|upper }}</div>
</div>

<div class="alert alert-info"><strong>{{ ogrenci_ad }}</strong> adli ogrencinin bilgilerini goruntuluyorsunuz.</div>

<div class="stat-grid">
  <div class="stat-card devamsizlik {% if devamsizlik.toplam <= 5 %}durum-iyi{% elif devamsizlik.toplam <= 10 %}durum-dikkat{% elif devamsizlik.toplam <= 15 %}durum-uyari{% else %}durum-kritik{% endif %}">
    <div class="stat-card-head"><span class="stat-card-ico">📅</span><span class="stat-card-etiket">Devamsizlik</span></div>
    <div class="stat-card-deger">{{ devamsizlik.toplam }} <small>gun</small></div>
    <div class="progress"><div class="progress-bar" style="width:{{ [100, (devamsizlik.toplam / 20 * 100)]|min }}%"></div></div>
    <div class="stat-card-alt">
      <span><span class="dot ozurlu"></span>Izinli: {{ devamsizlik.izinli }}</span>
      <span><span class="dot ozursuz"></span>Gelmedi: {{ devamsizlik.gelmedi }}</span>
    </div>
  </div>
  <div class="stat-card">
    <div class="stat-card-head"><span class="stat-card-ico">📊</span><span class="stat-card-etiket">Ortalama</span></div>
    <div class="stat-card-deger">{{ ortalama }}</div>
    <div class="stat-card-alt">{{ dersler|length }} ders</div>
  </div>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📚</span> Notlar</h3></div>
  {% if dersler %}
  <div class="ders-grid">
    {% for ders, sinavlar in dersler.items() %}
      {% set ort = (sinavlar|map(attribute='puan')|sum) / (sinavlar|length) %}
      <div class="ders-card">
        <div class="ders-head"><span class="ders-ad">{{ ders }}</span><span class="ders-harf">{{ ort|round(1) }}</span></div>
        <div class="ders-chips">{% for s in sinavlar %}<span class="sinav-chip"><em>{{ s.sinav }}</em>{{ s.puan }}</span>{% endfor %}</div>
        <div class="ders-bar"><div class="ders-bar-fill" style="width:{{ ort }}%"></div></div>
      </div>
    {% endfor %}
  </div>
  {% else %}<p class="muted">Henuz not kaydi yok.</p>{% endif %}
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📢</span> Duyurular</h3></div>
  {% if duyurular %}
  <div class="timeline">
    {% for d in duyurular %}
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-body">
        <div class="timeline-head"><strong>{{ d.baslik }}</strong><span class="timeline-tarih">{{ d.tarih }}</span></div>
        <p>{{ d.icerik }}</p>
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}<p class="muted">Duyuru yok.</p>{% endif %}
</div>
{% endblock %}
""")

yaz("templates/teacher.html", """{% extends "base.html" %}
{% block title %}Ogretmen Paneli{% endblock %}
{% block content %}
<div class="panel-hero">
  <div class="panel-hero-text">
    <div class="panel-hero-greet">Merhaba, {{ session.name }} 👋</div>
    <div class="panel-hero-sub">Ogretmen Paneli · Tum siniflar ve ogrenciler</div>
  </div>
  <div class="panel-hero-avatar">{{ session.name[0]|upper }}</div>
</div>

<div class="stat-grid">
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">👥</span><span class="stat-card-etiket">Ogrenci</span></div><div class="stat-card-deger">{{ ogrenciler|length }}</div><div class="stat-card-alt">Toplam kayitli</div></div>
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">📘</span><span class="stat-card-etiket">Dersim</span></div><div class="stat-card-deger">{{ dersler|length }}</div><div class="stat-card-alt">Size atanmis</div></div>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📘</span> Verdigim Dersler</h3></div>
  {% if dersler %}
  <div class="chip-list">{% for d in dersler %}<span class="chip chip-buyuk">{{ d.ad }}</span>{% endfor %}</div>
  {% else %}<p class="muted">Sistemde size atanmis ders yok.</p>{% endif %}
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">👥</span> Ogrenci Listesi</h3><span class="muted small">{{ ogrenciler|length }} ogrenci</span></div>
  {% if ogrenciler %}
  <div class="table-wrap">
    <table class="table">
      <thead><tr><th>Ad Soyad</th><th>Sinif</th><th>No</th></tr></thead>
      <tbody>{% for o in ogrenciler %}<tr><td><strong>{{ o.ad }}</strong></td><td><span class="chip">{{ o.sinif }}</span></td><td>{{ o.numara }}</td></tr>{% endfor %}</tbody>
    </table>
  </div>
  {% else %}<p class="muted">Kayitli ogrenci yok.</p>{% endif %}
</div>

<div class="card bilgi"><p class="muted">Not girisi ve devamsizlik isaretleme yonetim panelinden yapilir.</p></div>
{% endblock %}
""")

yaz("templates/admin.html", """{% extends "base.html" %}
{% block title %}Yonetim Paneli{% endblock %}
{% block content %}
<div class="panel-hero">
  <div class="panel-hero-text">
    <div class="panel-hero-greet">Yonetim Paneli</div>
    <div class="panel-hero-sub">Sistem genel bakis ve yonetim</div>
  </div>
  <div class="panel-hero-avatar">{{ session.name[0]|upper }}</div>
</div>

<div class="stat-grid">
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">👥</span><span class="stat-card-etiket">Ogrenci</span></div><div class="stat-card-deger">{{ sayilar.ogrenci }}</div></div>
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">👨‍🏫</span><span class="stat-card-etiket">Ogretmen</span></div><div class="stat-card-deger">{{ sayilar.ogretmen }}</div></div>
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">👨‍👩‍👧</span><span class="stat-card-etiket">Veli</span></div><div class="stat-card-deger">{{ sayilar.veli }}</div></div>
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">📘</span><span class="stat-card-etiket">Ders</span></div><div class="stat-card-deger">{{ sayilar.ders }}</div></div>
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">📝</span><span class="stat-card-etiket">Not</span></div><div class="stat-card-deger">{{ sayilar.not }}</div></div>
  <div class="stat-card"><div class="stat-card-head"><span class="stat-card-ico">📅</span><span class="stat-card-etiket">Devamsizlik</span></div><div class="stat-card-deger">{{ sayilar.devamsizlik }}</div></div>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">➕</span> Yeni Ogrenci Ekle</h3></div>
  <form method="post" action="{{ url_for('admin_add_student') }}" class="admin-form">
    <div class="form-row">
      <label><span>Ad Soyad</span><input name="ad" required></label>
      <label><span>T.C. Kimlik No</span><input name="tc" maxlength="11" required></label>
      <label><span>Sifre</span><input name="sifre" required></label>
    </div>
    <div class="form-row">
      <label><span>Sinif</span><input name="sinif" placeholder="9-A" required></label>
      <label><span>Numara</span><input name="numara" type="number" required></label>
    </div>
    <p class="muted small">Istege bagli - veli bilgileri:</p>
    <div class="form-row">
      <label><span>Veli Ad Soyad</span><input name="veli_ad"></label>
      <label><span>Veli T.C.</span><input name="veli_tc" maxlength="11"></label>
      <label><span>Veli Sifre</span><input name="veli_sifre"></label>
    </div>
    <button class="btn-primary" type="submit">Ogrenci Ekle</button>
  </form>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">➕</span> Yeni Ogretmen Ekle</h3></div>
  <form method="post" action="{{ url_for('admin_add_teacher') }}" class="admin-form">
    <div class="form-row">
      <label><span>Ad Soyad</span><input name="ad" required></label>
      <label><span>T.C. Kimlik No</span><input name="tc" maxlength="11" required></label>
      <label><span>Sifre</span><input name="sifre" required></label>
    </div>
    <button class="btn-primary" type="submit">Ogretmen Ekle</button>
  </form>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">➕</span> Yeni Ders Ekle</h3></div>
  <form method="post" action="{{ url_for('admin_add_course') }}" class="admin-form">
    <div class="form-row">
      <label><span>Ders Adi</span><input name="ad" required></label>
      <label><span>Ogretmen</span>
        <select name="ogretmen_id"><option value="">- Seciniz -</option>
          {% for o in ogretmenler %}<option value="{{ o.id }}">{{ o.name }}</option>{% endfor %}
        </select>
      </label>
    </div>
    <button class="btn-primary" type="submit">Ders Ekle</button>
  </form>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📝</span> Not Ekle</h3></div>
  <form method="post" action="{{ url_for('admin_add_grade') }}" class="admin-form">
    <div class="form-row">
      <label><span>Ogrenci</span>
        <select name="student_id" required><option value="">- Seciniz -</option>
          {% for o in ogrenciler %}<option value="{{ o.id }}">{{ o.ad }} ({{ o.sinif }}/{{ o.numara }})</option>{% endfor %}
        </select>
      </label>
      <label><span>Ders</span>
        <select name="course_id" required><option value="">- Seciniz -</option>
          {% for d in dersler %}<option value="{{ d.id }}">{{ d.ad }}</option>{% endfor %}
        </select>
      </label>
      <label><span>Sinav</span><input name="sinav" placeholder="Vize / Final" required></label>
      <label><span>Puan</span><input name="puan" type="number" step="0.1" min="0" max="100" required></label>
    </div>
    <button class="btn-primary" type="submit">Not Ekle</button>
  </form>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📅</span> Devamsizlik Kaydi</h3></div>
  <form method="post" action="{{ url_for('admin_add_attendance') }}" class="admin-form">
    <div class="form-row">
      <label><span>Ogrenci</span>
        <select name="student_id" required><option value="">- Seciniz -</option>
          {% for o in ogrenciler %}<option value="{{ o.id }}">{{ o.ad }} ({{ o.sinif }}/{{ o.numara }})</option>{% endfor %}
        </select>
      </label>
      <label><span>Tarih</span><input name="tarih" type="date" required></label>
      <label><span>Durum</span>
        <select name="durum" required>
          <option value="geldi">Geldi</option>
          <option value="gelmedi">Gelmedi</option>
          <option value="izinli">Izinli</option>
        </select>
      </label>
      <label><span>Aciklama</span><input name="aciklama"></label>
    </div>
    <button class="btn-primary" type="submit">Kaydet</button>
  </form>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📢</span> Duyuru Yayinla</h3></div>
  <form method="post" action="{{ url_for('admin_add_announcement') }}" class="admin-form">
    <div class="form-row"><label class="full"><span>Baslik</span><input name="baslik" required></label></div>
    <div class="form-row"><label class="full"><span>Icerik</span><textarea name="icerik" rows="3" required></textarea></label></div>
    <button class="btn-primary" type="submit">Yayinla</button>
  </form>
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">👥</span> Kayitli Ogrenciler</h3></div>
  {% if ogrenciler %}
  <div class="table-wrap"><table class="table">
    <thead><tr><th>Ad Soyad</th><th>T.C.</th><th>Sinif</th><th>No</th><th></th></tr></thead>
    <tbody>{% for o in ogrenciler %}<tr>
      <td><strong>{{ o.ad }}</strong></td><td>{{ o.tc_no }}</td><td>{{ o.sinif }}</td><td>{{ o.numara }}</td>
      <td><form method="post" action="{{ url_for('admin_delete', tip='ogrenci', oid=o.id) }}" onsubmit="return confirm('Silinsin mi?');"><button type="submit" class="link-btn" style="color:#dc2626">Sil</button></form></td>
    </tr>{% endfor %}</tbody>
  </table></div>
  {% else %}<p class="muted">Henuz ogrenci eklenmemis.</p>{% endif %}
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">👨‍🏫</span> Kayitli Ogretmenler</h3></div>
  {% if ogretmenler %}
  <div class="table-wrap"><table class="table">
    <thead><tr><th>Ad Soyad</th><th>T.C.</th><th></th></tr></thead>
    <tbody>{% for o in ogretmenler %}<tr>
      <td><strong>{{ o.name }}</strong></td><td>{{ o.tc_no }}</td>
      <td><form method="post" action="{{ url_for('admin_delete', tip='ogretmen', oid=o.id) }}" onsubmit="return confirm('Silinsin mi?');"><button type="submit" class="link-btn" style="color:#dc2626">Sil</button></form></td>
    </tr>{% endfor %}</tbody>
  </table></div>
  {% else %}<p class="muted">Henuz ogretmen eklenmemis.</p>{% endif %}
</div>

<div class="card">
  <div class="card-head"><h3><span class="ico">📘</span> Kayitli Dersler</h3></div>
  {% if dersler %}
  <div class="table-wrap"><table class="table">
    <thead><tr><th>Ders</th><th>Ogretmen</th><th></th></tr></thead>
    <tbody>{% for d in dersler %}<tr>
      <td><strong>{{ d.ad }}</strong></td><td>{{ d.ogretmen or '-' }}</td>
      <td><form method="post" action="{{ url_for('admin_delete', tip='ders', oid=d.id) }}" onsubmit="return confirm('Silinsin mi?');"><button type="submit" class="link-btn" style="color:#dc2626">Sil</button></form></td>
    </tr>{% endfor %}</tbody>
  </table></div>
  {% else %}<p class="muted">Henuz ders eklenmemis.</p>{% endif %}
</div>
{% endblock %}
""")


# ============================================================
# CSS
# ============================================================

print("\n[4/6] Stil dosyalari yaziliyor...")

# style.css
yaz("static/style.css", """:root {
  --navy:      #0b1437;
  --navy-2:    #131c47;
  --amber:     #f5a623;
  --amber-2:   #fbbf24;
  --coral:     #ef4444;
  --green:     #10b981;
  --cream:     #fdf9f3;
  --paper:     #ffffff;
  --line:      #ece3d3;
  --ink:       #1a1a2e;
  --muted:     #6b7280;
  --radius-lg: 22px;
  --shadow-sm: 0 1px 2px rgba(11,20,55,.05), 0 1px 3px rgba(11,20,55,.06);
  --shadow-md: 0 8px 24px rgba(11,20,55,.08), 0 2px 4px rgba(11,20,55,.04);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--ink);
  line-height: 1.55;
  background:
    radial-gradient(circle at 0% 0%,   rgba(245,166,35,.10), transparent 45%),
    radial-gradient(circle at 100% 100%, rgba(11,20,55,.06),   transparent 45%),
    var(--cream);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, .brand, .stat, .stat-card-deger, .panel-hero-greet {
  font-family: 'Fraunces', Georgia, serif;
  letter-spacing: -0.015em;
}
.container { max-width: 1140px; margin: 0 auto; padding: 0 20px; }
.muted { color: var(--muted); }
.small { font-size: .85rem; }

.btn-primary {
  display: inline-block; width: 100%;
  padding: 15px 22px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, var(--amber) 0%, var(--amber-2) 100%);
  color: var(--navy); font-size: 1rem; font-weight: 700;
  cursor: pointer; letter-spacing: .02em;
  box-shadow: 0 6px 20px rgba(245,166,35,.35);
  transition: all .18s ease; font-family: inherit;
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 10px 26px rgba(245,166,35,.45); }

.btn-ghost {
  padding: 8px 16px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,.22);
  background: rgba(255,255,255,.04);
  color: #fff; font-size: .88rem; font-weight: 500;
  cursor: pointer; text-decoration: none;
  font-family: inherit; transition: all .18s ease;
}
.btn-ghost:hover { background: var(--amber); border-color: var(--amber); color: var(--navy); }

.topbar {
  background: linear-gradient(180deg, var(--navy) 0%, var(--navy-2) 100%);
  color: #fff; position: sticky; top: 0; z-index: 50;
  box-shadow: 0 4px 20px rgba(11,20,55,.18);
}
.topbar::after {
  content: ""; display: block; height: 3px;
  background: linear-gradient(90deg, var(--amber), var(--amber-2) 40%, transparent);
}
.topbar-inner {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 20px;
}
.brand {
  color: #fff; text-decoration: none; font-weight: 700;
  font-size: 1.05rem; display: inline-flex; align-items: center; gap: 12px;
}
.brand::before {
  content: "C";
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, var(--amber), var(--amber-2));
  color: var(--navy); font-family: 'Fraunces', serif;
  font-weight: 700; font-size: 1.1rem;
}
.menu { display: flex; align-items: center; gap: 14px; }
.menu .user {
  font-size: .9rem; color: rgba(255,255,255,.85);
  padding-right: 14px; border-right: 1px solid rgba(255,255,255,.14);
}
.alert {
  padding: 14px 18px; border-radius: 12px;
  margin: 18px 0; font-size: .92rem; font-weight: 500;
  border-left: 4px solid;
}
.alert-error { background: #fff1f1; color: #991b1b; border-color: var(--coral); }
.alert-success { background: #ecfdf5; color: #065f46; border-color: var(--green); }
.alert-info { background: #eef2ff; color: #3730a3; border-color: #6366f1; }
""")

# hero.css
yaz("static/hero.css", """/* LOGIN HERO */

.login-page { overflow-x: hidden; }
.login-wrap { display: grid; grid-template-columns: 1.1fr 1fr; min-height: 100vh; }
.login-hero {
  position: relative; overflow: hidden;
  padding: 80px 70px; display: flex; align-items: center;
  background:
    radial-gradient(circle at 20% 25%, rgba(245,166,35,.22), transparent 45%),
    radial-gradient(circle at 85% 85%, rgba(99,102,241,.16), transparent 50%),
    linear-gradient(140deg, var(--navy) 0%, var(--navy-2) 55%, #241b58 100%);
  color: #fff;
}
.login-hero::before {
  content: ""; position: absolute;
  right: -18%; bottom: -22%; width: 95%; aspect-ratio: 1 / 1;
  background: url("logo.png") center/contain no-repeat;
  opacity: .07; filter: blur(1.5px) saturate(1.4);
  transform: rotate(-9deg); pointer-events: none; z-index: 0;
}
.hero-content { position: relative; z-index: 2; max-width: 520px; }
.hero-orb {
  position: absolute; right: -100px; bottom: -100px;
  width: 380px; height: 380px; border-radius: 50%;
  background: radial-gradient(circle, rgba(245,166,35,.35), transparent 70%);
  pointer-events: none;
}

.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  margin-bottom: 24px; padding: 8px 18px 8px 15px;
  border: 1px solid rgba(245,166,35,.35); border-radius: 999px;
  font-family: 'Inter', sans-serif;
  font-size: .72rem; font-weight: 600; letter-spacing: .14em;
  color: #f5a623; background: rgba(245,166,35,.07);
  position: relative; z-index: 2;
}
.hero-eyebrow-text { line-height: 1; padding-top: 1px; }
.hero-eyebrow-dot {
  position: relative; display: inline-block;
  width: 7px; height: 7px; border-radius: 50%;
  background: #f5a623; flex-shrink: 0;
  box-shadow: 0 0 8px rgba(245,166,35,.9);
}
.hero-eyebrow-dot::after {
  content: ""; position: absolute; inset: 0;
  border-radius: 50%; background: #f5a623;
  animation: eyebrowPulse 2s ease-out infinite;
}
@keyframes eyebrowPulse {
  0%   { transform: scale(1);   opacity: .9; }
  70%  { transform: scale(2.6); opacity: 0; }
  100% { transform: scale(2.6); opacity: 0; }
}

.hero-brand {
  position: relative; display: inline-flex; align-items: center;
  gap: 22px; margin: 0 0 46px; z-index: 2;
}
.hero-brand-mark { position: relative; flex-shrink: 0; }
.hero-brand-mark::before {
  content: ""; position: absolute; inset: -60px -70px;
  background: radial-gradient(ellipse at center,
    rgba(245,166,35,.34) 0%, rgba(245,166,35,.14) 38%, transparent 72%);
  filter: blur(20px); z-index: 0; pointer-events: none;
  animation: logoGlow 6s ease-in-out infinite alternate;
}
@keyframes logoGlow {
  0%   { opacity: .72; transform: scale(1); }
  100% { opacity: 1;   transform: scale(1.08); }
}
.hero-brand-mark img {
  position: relative; z-index: 1; display: block;
  height: clamp(96px, 11vw, 132px); width: auto;
  object-fit: contain; mix-blend-mode: screen;
  filter: brightness(1.10) contrast(1.06) saturate(1.12)
    drop-shadow(0 0 26px rgba(245,166,35,.50))
    drop-shadow(0 0 80px rgba(245,166,35,.24));
}
.hero-brand-text { display: flex; flex-direction: column; line-height: 1; }
.hero-brand-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(2rem, 3.2vw, 2.9rem);
  font-weight: 600; letter-spacing: -0.02em;
  color: #fff; line-height: 1;
}
.hero-brand-title::first-letter { color: #f5a623; }
.hero-brand-sub {
  margin-top: 6px; font-family: 'Inter', sans-serif;
  font-size: clamp(.7rem, 1vw, .85rem);
  font-weight: 600; letter-spacing: .44em;
  color: #f5a623; opacity: .92;
}

.login-hero h1 {
  font-size: clamp(1.8rem, 3vw, 2.8rem);
  font-weight: 600; line-height: 1.15;
  margin: 0 0 20px; color: #fff;
}
.hero-lead {
  font-size: 1.05rem; color: rgba(255,255,255,.78);
  margin: 0 0 30px; max-width: 460px;
}
.hero-list {
  list-style: none; padding: 0; margin: 0;
  display: flex; flex-direction: column; gap: 12px;
}
.hero-list li {
  position: relative; padding-left: 28px;
  color: rgba(255,255,255,.88); font-size: .98rem;
}
.hero-list li::before {
  content: "\\2605"; position: absolute; left: 0;
  color: #f5a623; font-size: .9rem;
}
.hero-stats {
  display: flex; gap: 40px;
  margin-top: 44px; padding-top: 30px;
  border-top: 1px solid rgba(255,255,255,.10);
  position: relative; z-index: 2;
}
.hero-stat { display: flex; flex-direction: column; gap: 4px; }
.hero-stat strong {
  font-family: 'Fraunces', serif;
  font-size: 1.9rem; font-weight: 600;
  color: #fff; letter-spacing: -0.02em; line-height: 1;
  display: inline-flex; align-items: baseline;
}
.hero-stat strong em {
  font-style: normal; color: #f5a623;
  font-size: .75em; margin-left: 2px;
}
.hero-stat span { font-size: .78rem; color: rgba(255,255,255,.62); }

.login-main {
  display: flex; align-items: center; justify-content: center;
  padding: 60px 40px;
}
.login-card { width: 100%; max-width: 400px; }
.login-card h2 {
  font-family: 'Fraunces', serif;
  font-size: 2rem; margin: 0 0 6px; color: var(--navy);
}
.login-card h2::after {
  content: ""; display: block; width: 42px; height: 3px;
  margin-top: 12px; background: var(--amber); border-radius: 3px;
}
.login-card .lead {
  margin: 14px 0 30px; color: var(--muted); font-size: .98rem;
}
.login-card label { display: block; margin-bottom: 18px; }
.login-card label span {
  display: block; font-size: .78rem; font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase;
  color: var(--navy-2); margin-bottom: 8px;
}
.login-card input {
  width: 100%; padding: 14px 16px;
  border: 1.5px solid var(--line); border-radius: 12px;
  font-size: 1rem; font-family: inherit;
  background: var(--paper); color: var(--ink);
  transition: all .16s ease;
}
.login-card input:focus {
  outline: none; border-color: var(--amber);
  box-shadow: 0 0 0 4px rgba(245,166,35,.15);
}

@media (max-width: 900px) {
  .login-wrap { grid-template-columns: 1fr; }
  .login-hero { padding: 50px 30px; min-height: auto; }
  .login-main { padding: 40px 24px; }
}
@media (max-width: 600px) {
  .login-hero h1 { font-size: 1.6rem; }
  .hero-brand-mark img { height: 72px; }
  .hero-stats { gap: 24px; margin-top: 32px; padding-top: 22px; }
  .hero-stat strong { font-size: 1.45rem; }
}
""")

# panel.css
yaz("static/panel.css", """/* PANEL */

.panel-hero {
  position: relative; display: flex; justify-content: space-between;
  align-items: center; gap: 24px;
  padding: 32px 36px; margin: 30px 0 26px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 85% 20%, rgba(245,166,35,.22), transparent 55%),
    linear-gradient(135deg, var(--navy) 0%, var(--navy-2) 60%, #221b52 100%);
  color: #fff; overflow: hidden;
  box-shadow: 0 18px 40px rgba(11,20,55,.22);
}
.panel-hero::after {
  content: ""; position: absolute;
  right: -60px; bottom: -60px;
  width: 220px; height: 220px; border-radius: 50%;
  background: radial-gradient(circle, rgba(245,166,35,.30), transparent 70%);
  pointer-events: none;
}
.panel-hero-text { position: relative; z-index: 2; }
.panel-hero-greet {
  font-size: 1.9rem; font-weight: 600;
  letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 6px;
}
.panel-hero-sub { font-size: .98rem; color: rgba(255,255,255,.78); }
.panel-hero-avatar {
  position: relative; z-index: 2;
  width: 68px; height: 68px; border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Fraunces', serif;
  font-size: 1.9rem; font-weight: 700;
  color: var(--navy);
  background: linear-gradient(135deg, var(--amber), var(--amber-2));
  box-shadow: 0 10px 26px rgba(245,166,35,.42);
  flex-shrink: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px; margin-bottom: 26px;
}
.stat-card {
  position: relative; background: var(--paper);
  border: 1px solid var(--line); border-radius: 20px;
  padding: 22px 24px; box-shadow: var(--shadow-sm);
  transition: transform .2s ease, box-shadow .2s ease;
  overflow: hidden;
}
.stat-card::before {
  content: ""; position: absolute; left: 0; top: 0;
  height: 3px; width: 100%;
  background: linear-gradient(90deg, var(--amber), var(--amber-2));
  opacity: .55;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.stat-card-head {
  display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
}
.stat-card-ico { font-size: 1.15rem; }
.stat-card-etiket {
  font-size: .76rem; font-weight: 700;
  letter-spacing: .12em; text-transform: uppercase;
  color: var(--muted);
}
.stat-card-deger {
  font-size: 2.4rem; font-weight: 600;
  color: var(--navy); line-height: 1;
  letter-spacing: -0.02em;
  display: flex; align-items: baseline; gap: 10px;
}
.stat-card-deger small {
  font-family: 'Inter', sans-serif;
  font-size: 1rem; font-weight: 500;
  color: var(--muted); letter-spacing: 0;
}
.stat-card-alt {
  margin-top: 12px; font-size: .85rem; color: var(--muted);
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.stat-card.durum-dikkat::before { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
.stat-card.durum-uyari::before  { background: linear-gradient(90deg, #fb923c, #ea580c); }
.stat-card.durum-kritik::before { background: linear-gradient(90deg, #f87171, #dc2626); }
.stat-card.durum-kritik .stat-card-deger { color: #dc2626; }
.stat-card.durum-uyari  .stat-card-deger { color: #ea580c; }

.progress {
  height: 6px; background: #f3ede0;
  border-radius: 999px; margin: 12px 0 4px; overflow: hidden;
}
.progress-bar {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, var(--green), #34d399);
  transition: width .5s ease;
}
.durum-dikkat .progress-bar { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
.durum-uyari  .progress-bar { background: linear-gradient(90deg, #fb923c, #ea580c); }
.durum-kritik .progress-bar { background: linear-gradient(90deg, #f87171, #dc2626); }

.dot {
  display: inline-block; width: 7px; height: 7px;
  border-radius: 50%; margin-right: 4px;
}
.dot.ozurlu  { background: var(--green); }
.dot.ozursuz { background: var(--coral); }

.card {
  background: var(--paper); border: 1px solid var(--line);
  border-radius: var(--radius-lg); padding: 26px;
  margin-bottom: 20px; box-shadow: var(--shadow-sm);
  transition: box-shadow .2s ease;
}
.card:hover { box-shadow: var(--shadow-md); }
.card h3 {
  margin: 0 0 16px; font-size: 1.02rem;
  font-family: 'Inter', sans-serif; font-weight: 700;
  color: var(--navy); display: flex; align-items: center; gap: 8px;
}
.card.bilgi {
  background: linear-gradient(135deg, #fff8e6 0%, #fdf3d8 100%);
  border-color: #f0e0b8;
}
.card-head {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 18px; gap: 12px;
}
.card-head h3 { margin: 0; }

.ders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}
.ders-card {
  background: #fdfaf3; border: 1px solid var(--line);
  border-radius: 16px; padding: 16px 18px;
  transition: background .18s ease, transform .18s ease;
}
.ders-card:hover {
  background: #fff; transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
.ders-head {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 12px; gap: 8px;
}
.ders-ad { font-weight: 700; color: var(--navy); font-size: .98rem; }
.ders-harf {
  font-size: .82rem; font-weight: 700;
  padding: 3px 10px; border-radius: 999px;
  background: #fff5e0; color: #9a6200; border: 1px solid #f4dca0;
}
.ders-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.sinav-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: #fff; border: 1px solid var(--line);
  padding: 4px 10px; border-radius: 999px;
  font-size: .82rem; font-weight: 600; color: var(--navy-2);
}
.sinav-chip em {
  font-style: normal; font-size: .7rem; font-weight: 700;
  letter-spacing: .06em; text-transform: uppercase; color: var(--muted);
}
.ders-bar {
  height: 4px; background: #efe7d4;
  border-radius: 999px; overflow: hidden;
}
.ders-bar-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, var(--amber), var(--amber-2));
  transition: width .6s ease;
}

.timeline { position: relative; padding-left: 26px; }
.timeline::before {
  content: ""; position: absolute;
  left: 6px; top: 6px; bottom: 6px; width: 2px;
  background: linear-gradient(180deg, var(--amber), transparent);
  opacity: .4; border-radius: 2px;
}
.timeline-item { position: relative; padding: 10px 0 18px; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-dot {
  position: absolute; left: -26px; top: 16px;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--paper); border: 3px solid var(--amber);
  box-shadow: 0 0 0 4px rgba(245,166,35,.15);
}
.timeline-head {
  display: flex; justify-content: space-between;
  align-items: baseline; gap: 12px; margin-bottom: 4px;
}
.timeline-head strong { color: var(--navy); font-size: .98rem; }
.timeline-tarih { font-size: .78rem; color: var(--muted); }
.timeline-body p { margin: 0; color: #4b5563; font-size: .92rem; line-height: 1.55; }

.chip {
  display: inline-block; background: #f3f4f6;
  color: var(--navy-2); padding: 3px 10px;
  border-radius: 999px; font-size: .82rem;
  font-weight: 600; border: 1px solid #e5e7eb;
}
.chip-buyuk {
  padding: 8px 16px; font-size: .92rem;
  background: #fff5e0; color: #9a6200; border-color: #f4dca0;
}
.chip-list { display: flex; flex-wrap: wrap; gap: 10px; }

.table { width: 100%; border-collapse: collapse; }
.table th, .table td {
  padding: 14px 10px; text-align: left;
  border-bottom: 1px solid var(--line); font-size: .95rem;
}
.table th {
  font-size: .74rem; text-transform: uppercase;
  letter-spacing: .08em; color: var(--muted);
  font-weight: 700; border-bottom: 2px solid var(--line);
}
.table tr:hover { background: #fdfaf3; }
.table tr:last-child td { border-bottom: none; }
.table-wrap { overflow-x: auto; margin: 0 -6px; padding: 0 6px; }

.link-btn {
  border: none; background: none; color: var(--navy-2);
  font-family: inherit; font-size: .88rem; font-weight: 600;
  cursor: pointer; padding: 4px 6px; border-radius: 6px;
}

@media (max-width: 720px) {
  .panel-hero {
    padding: 24px 22px; flex-direction: column;
    align-items: flex-start; gap: 18px;
    margin: 20px 0 22px;
  }
  .panel-hero-greet { font-size: 1.5rem; }
  .panel-hero-avatar {
    width: 56px; height: 56px; font-size: 1.5rem;
    align-self: flex-end;
  }
  .stat-card-deger { font-size: 2rem; }
  .stat-grid { gap: 14px; }
  .stat-card { padding: 18px 20px; }
  .ders-grid { grid-template-columns: 1fr; }
}
""")

# login.css (ek parçalar)
yaz("static/login.css", """/* LOGIN EXTRA */

.input-wrap { position: relative; display: block; }
.input-wrap input { padding-right: 48px !important; }
.input-eye {
  position: absolute; top: 50%; right: 8px;
  transform: translateY(-50%);
  width: 38px; height: 38px; border: none;
  background: transparent; color: #9ca3af;
  border-radius: 10px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s ease;
}
.input-eye:hover { color: #f5a623; background: rgba(245,166,35,.08); }
.input-eye .eye-closed { display: none; }
.input-eye.is-visible .eye-open { display: none; }
.input-eye.is-visible .eye-closed { display: block; }
""")

# admin.css
yaz("static/admin.css", """/* ADMIN FORM */

.admin-form .form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px; margin-bottom: 14px;
}
.admin-form .form-row .full { grid-column: 1 / -1; }
.admin-form label { display: block; font-size: .82rem; }
.admin-form label span {
  display: block; font-size: .72rem; font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase;
  color: var(--navy-2); margin-bottom: 6px;
}
.admin-form input, .admin-form select, .admin-form textarea {
  width: 100%; padding: 11px 13px;
  border: 1.5px solid var(--line); border-radius: 10px;
  font-size: .94rem; font-family: inherit;
  background: #fff; color: var(--ink);
  transition: all .15s ease;
}
.admin-form input:focus, .admin-form select:focus, .admin-form textarea:focus {
  outline: none; border-color: var(--amber);
  box-shadow: 0 0 0 3px rgba(245,166,35,.15);
}
.admin-form textarea { resize: vertical; min-height: 70px; }
.admin-form .btn-primary { margin-top: 6px; max-width: 240px; }
.admin-form select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 38px;
}
""")


# ============================================================
# LOGO KOPYALA
# ============================================================

print("\n[5/6] Logo kopyalaniyor...")

logo_kaynak = None
for aday in ["staff/logo.png", "staff/logo.jpg", "logo.png", "logo.jpg"]:
    if os.path.exists(os.path.join(KOK, aday)):
        logo_kaynak = aday
        break

if logo_kaynak:
    hedef = os.path.join(KOK, "static", "logo.png")
    try:
        shutil.copy2(os.path.join(KOK, logo_kaynak), hedef)
        print(f"  ✓ {logo_kaynak} -> static/logo.png")
    except Exception as e:
        print(f"  ! Kopyalanamadi: {e}")
else:
    print("  ! Logo bulunamadi (staff/logo.png yok)")
    print("    -> Login sayfasinda logo gorunmeyecek. staff/logo.png ekleyin.")


# ============================================================
# VERITABANI
# ============================================================

print("\n[6/6] Veritabani hazirlaniyor...")

try:
    from models import init_db, seed_admin
    init_db()
    seed_admin()
except Exception as e:
    print(f"  ! Veritabani hatasi: {e}")
    print("    Flask kurulu degilse once: py -m pip install -r requirements.txt")


# ============================================================
# BITTI
# ============================================================

print("\n" + "=" * 60)
print("  KURULUM TAMAMLANDI")
print("=" * 60)
print("\n  Simdi su komutu calistirin:\n")
print("      py run.py\n")
print("  Sonra tarayicida acin:")
print("      http://127.0.0.1:5000\n")
print("  Giris bilgileri:")
print("      T.C.  : 11111111111")
print("      Sifre : admin123\n")
print("=" * 60 + "\n")