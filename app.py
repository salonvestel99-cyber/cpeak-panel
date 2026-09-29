# -*- coding: utf-8 -*-
"""Ana Flask uygulaması."""

import os
from datetime import date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

from models import get_db
from mail_service import (send_email, sablon_sifre_talebi, sablon_test, sablon_kayit, sablon_sifre_degisti, sablon_sifre_sifirlandi, sablon_devamsizlik, sablon_not_girildi, sablon_ozel, HAZIR_SABLONLAR)

load_dotenv()

app = Flask(__name__)



# ============================================================
# --- Guvenlik katmanlari ---
from security import init_security
init_security(app)


# ============================================================
# Veritabani baslatma - GUNICORN ile de calisir
# ============================================================
# Absolute path kullan (Render'da /tmp yazilabilir)
import os as _os
_DB_YOL = _os.environ.get("DB_PATH", "")
if _DB_YOL and not _os.path.isabs(_DB_YOL):
    # Relative ise proje kokune sabitle
    _DB_YOL = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), _DB_YOL)
    _os.environ["DB_PATH"] = _DB_YOL
print(f"[boot] DB_PATH={_os.environ.get('DB_PATH', 'egitim.db')}", flush=True)

try:
    with app.app_context():
        from models import init_db, seed_admin
        try:
            init_db()
            print("[boot] init_db OK", flush=True)
        except Exception as e:
            import traceback
            print(f"[boot] init_db HATA: {e}", flush=True)
            traceback.print_exc()
        try:
            seed_admin()
            print("[boot] seed_admin OK", flush=True)
        except Exception as e:
            import traceback
            print(f"[boot] seed_admin HATA: {e}", flush=True)
            traceback.print_exc()
except Exception as e:
    import traceback
    print(f"[boot] DIS HATA: {e}", flush=True)
    traceback.print_exc()
# ============================================================

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.permanent_session_lifetime = timedelta(days=30)

@app.context_processor
def inject_now():
    """Şablonlarda dinamik selamlama için saat bilgisi."""
    from datetime import datetime
    return {"now_hour": datetime.now().hour}

def login_required(*roles):
    """Çoklu rol destekli login kontrolü.

    Kullanım:
        @login_required()                     # herhangi bir giriş
        @login_required("admin")              # sadece admin
        @login_required("admin", "teacher")   # admin veya teacher
    """
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if roles and session.get("role") not in roles:
                flash("Bu sayfaya erişim yetkiniz yok.", "error")
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

@app.route("/kvkk")
def kvkk():
    return render_template("kvkk.html")

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))

@app.route("/giris", methods=["GET", "POST"])
@app.limiter.limit("10 per minute", methods=["POST"])
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
            session.permanent = bool(request.form.get("beni_hatirla"))
            return redirect(url_for("dashboard"))
        flash("T.C. kimlik no veya şifre hatalı.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

# ============================================================
# ŞİFREMİ UNUTTUM — talep kaydı
# ============================================================

@app.route("/sifremi-unuttum", methods=["POST"])
@app.limiter.limit("3 per minute")
def sifremi_unuttum():
    tc = request.form.get("tc", "").strip()
    email = request.form.get("email", "").strip()
    if not tc:
        flash("T.C. kimlik no gerekli.", "error")
        return redirect(url_for("login"))
    conn = get_db()
    u = conn.execute("SELECT id, name, role FROM users WHERE tc_no = ?", (tc,)).fetchone()
    if u:
        conn.execute(
            "INSERT INTO reset_requests (tc_no, user_name, role, email, mesaj, tarih) VALUES (?,?,?,?,?,?)",
            (tc, u["name"], u["role"], email or None,
             "Kullanıcı şifre sıfırlama talep etti.",
             date.today().strftime("%d.%m.%Y %H:%M"))
        )
        conn.commit()
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
    return redirect(url_for("login"))

@app.route("/cikis", methods=["POST"])
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

# ============================================================
# ŞİFRE DEĞİŞTİRME (her kullanıcı)
# ============================================================

@app.route("/sifre-degistir", methods=["GET", "POST"])
@login_required()
def sifre_degistir():
    if request.method == "POST":
        eski = request.form.get("eski", "")
        yeni = request.form.get("yeni", "")
        yeni2 = request.form.get("yeni2", "")
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        if not u or not check_password_hash(u["password_hash"], eski):
            conn.close()
            flash("Mevcut şifre hatalı.", "error")
            return redirect(url_for("sifre_degistir"))
        if len(yeni) < 5:
            conn.close()
            flash("Yeni şifre en az 5 karakter olmalı.", "error")
            return redirect(url_for("sifre_degistir"))
        if yeni != yeni2:
            conn.close()
            flash("Yeni şifreler eşleşmiyor.", "error")
            return redirect(url_for("sifre_degistir"))
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                     (generate_password_hash(yeni), session["user_id"]))
        conn.commit()
        try:
            _k = conn.execute("SELECT email, name, tc_no FROM users WHERE id = ?",
                              (session["user_id"],)).fetchone()
            if _k and _k["email"]:
                send_email("Sifreniz Degistirildi", _k["email"],
                           sablon_sifre_degisti(_k["name"], _k["tc_no"]))
        except Exception as _e:
            print(f"[sifre_degistir] mail hata: {_e}", flush=True)
        conn.close()
        flash("Şifreniz güncellendi.", "success")
        return redirect(url_for("dashboard"))
    return render_template("sifre_degistir.html")

# ============================================================
# ÖĞRENCİ
# ============================================================

@app.route("/ogrenci")
@login_required("student")
def student_panel():
    conn = get_db()
    s = conn.execute("SELECT * FROM students WHERE user_id = ?", (session["user_id"],)).fetchone()
    conn.close()
    if not s:
        flash("Öğrenci kaydınız bulunamadı.", "error")
        return redirect(url_for("logout"))
    data = _ogrenci_verisi(s["id"])
    return render_template("student.html", ogrenci=dict(s), **data)

# ============================================================
# VELİ
# ============================================================

@app.route("/veli")
@login_required("parent")
def parent_panel():
    sid = session.get("student_id")
    if not sid:
        flash("Veliye bağlı öğrenci bulunamadı.", "error")
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

# ============================================================
# ÖĞRETMEN
# ============================================================

@app.route("/ogretmen")
@login_required("teacher")
def teacher_panel():
    conn = get_db()

    # Kendi dersleri
    dersler = conn.execute(
        "SELECT id, ad FROM courses WHERE ogretmen_id = ? ORDER BY ad",
        (session["user_id"],)
    ).fetchall()

    # Tüm öğrenciler
    ogrenciler = conn.execute("""
        SELECT s.id, u.name AS ad, s.sinif, s.numara
        FROM students s JOIN users u ON u.id = s.user_id
        ORDER BY s.sinif, s.numara
    """).fetchall()

    # Sınıflar (filtre için)
    siniflar = [r["sinif"] for r in conn.execute(
        "SELECT DISTINCT sinif FROM students ORDER BY sinif"
    ).fetchall()]

    # Son ödevler (tablo varsa)
    try:
        odevler = conn.execute("""
            SELECT h.id, h.baslik, h.teslim,
                (SELECT COUNT(*) FROM homework_submission
                 WHERE homework_id = h.id) AS teslim_sayisi
            FROM homework h
            WHERE h.ogretmen_id = ?
            ORDER BY h.id DESC LIMIT 5
        """, (session["user_id"],)).fetchall()
    except Exception:
        odevler = []

    # Bugünkü yoklama
    try:
        bugun = date.today().isoformat()
        bugun_yoklama = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE tarih = ?",
            (bugun,)
        ).fetchone()[0]
    except Exception:
        bugun_yoklama = 0

    conn.close()

    # Bugünün tarihi (Türkçe)
    d = date.today()
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
             "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    bugun_gun = f"{gunler[d.weekday()]}, {d.day} {aylar[d.month-1]}"

    if bugun_yoklama == 0:
        yoklama_metni = "Henüz alınmadı"
    else:
        yoklama_metni = "öğrenci işaretli"

    return render_template("teacher.html",
                           dersler=[dict(x) for x in dersler],
                           ogrenciler=[dict(x) for x in ogrenciler],
                           siniflar=siniflar,
                           odevler=[dict(x) for x in odevler],
                           ogrenci_sayisi=len(ogrenciler),
                           bugun_yoklama=bugun_yoklama,
                           yoklama_metni=yoklama_metni,
                           bugun_gun=bugun_gun)

# ============================================================
# DEVAMSIZLIK DETAY (ortak — rol kontrolü içinde)
# ============================================================

@app.route("/devamsizlik/<int:sid>")
@login_required()
def devamsizlik_detay(sid):
    role = session["role"]

    # Yetki: öğrenci sadece kendini, veli sadece çocuğunu
    if role == "student":
        conn = get_db()
        own = conn.execute("SELECT id FROM students WHERE user_id = ?",
                           (session["user_id"],)).fetchone()
        conn.close()
        if not own or own["id"] != sid:
            flash("Bu sayfaya erişim yetkiniz yok.", "error")
            return redirect(url_for("dashboard"))
    elif role == "parent":
        if session.get("student_id") != sid:
            flash("Bu sayfaya erişim yetkiniz yok.", "error")
            return redirect(url_for("dashboard"))

    conn = get_db()
    s = conn.execute("""
        SELECT s.id, s.sinif, s.numara, u.name AS ad
        FROM students s JOIN users u ON u.id = s.user_id
        WHERE s.id = ?
    """, (sid,)).fetchone()
    if not s:
        conn.close()
        flash("Öğrenci bulunamadı.", "error")
        return redirect(url_for("dashboard"))

    kayitlar = conn.execute("""
        SELECT tarih, durum, aciklama FROM attendance
        WHERE student_id = ? ORDER BY tarih DESC, id DESC
    """, (sid,)).fetchall()
    conn.close()

    sayilar = {"toplam": len(kayitlar), "geldi": 0, "gelmedi": 0, "izinli": 0}
    for k in kayitlar:
        sayilar[k["durum"]] = sayilar.get(k["durum"], 0) + 1

    return render_template("devamsizlik.html",
                           ogrenci=dict(s),
                           kayitlar=[dict(k) for k in kayitlar],
                           sayilar=sayilar)

# ============================================================
# ADMIN
# ============================================================

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
        SELECT s.id, u.id AS uid, u.name AS ad, u.tc_no, s.sinif, s.numara
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
    talepler = conn.execute("""
        SELECT id, tc_no, user_name, role, email, tarih
        FROM reset_requests WHERE durum = 'bekliyor'
        ORDER BY id DESC
    """).fetchall()
    duyurular = conn.execute("""
        SELECT id, baslik, icerik, tarih FROM announcements
        ORDER BY id DESC LIMIT 30
    """).fetchall()
    conn.close()
    return render_template("admin.html", sayilar=sayilar,
                           ogrenciler=[dict(o) for o in ogrenciler],
                           ogretmenler=[dict(o) for o in ogretmenler],
                           dersler=[dict(d) for d in dersler],
                           talepler=[dict(t) for t in talepler],
                           duyurular=[dict(d) for d in duyurular])

@app.route("/admin/ogrenci-ekle", methods=["POST"])
@login_required("admin")
def admin_add_student():
    ad = request.form.get("ad", "").strip()
    tc = request.form.get("tc", "").strip()
    sifre = request.form.get("sifre", "").strip()
    sinif = request.form.get("sinif", "").strip()
    numara = request.form.get("numara", "").strip()
    if not (ad and tc and sifre and sinif and numara):
        flash("Tüm alanlar zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        mevcut = conn.execute("SELECT role FROM users WHERE tc_no = ?", (tc,)).fetchone()
        if mevcut:
            conn.close()
            rol_tr = {"student": "öğrenci", "parent": "veli", "teacher": "öğretmen", "admin": "yönetici"}.get(mevcut["role"], mevcut["role"])
            flash(f"Bu T.C. ({tc}) zaten {rol_tr} olarak kayıtlı.", "error")
            return redirect(url_for("admin_panel"))

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
        try:
            _giris = request.url_root.rstrip("/") + url_for("login")
            _email_ogr = request.form.get("email", "").strip()
            if _email_ogr:
                send_email("C-Peak Panel Kaydiniz", _email_ogr,
                           sablon_kayit(ad, tc, sifre, _giris))
            _email_veli = request.form.get("veli_email", "").strip()
            if _email_veli and v_ad and v_sifre and v_tc:
                send_email("C-Peak Panel Veli Kaydiniz", _email_veli,
                           sablon_kayit(v_ad, v_tc, v_sifre, _giris))
        except Exception as _e:
            print(f"[admin_add_student] mail hata: {_e}", flush=True)
        flash(f"Öğrenci eklendi: {ad}", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
            flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/admin/ogrenci-duzenle/<int:sid>", methods=["GET", "POST"])
@login_required("admin")
def admin_edit_student(sid):
    conn = get_db()
    s = conn.execute("""
        SELECT s.id, s.sinif, s.numara, u.id AS uid, u.name AS ad, u.tc_no
        FROM students s JOIN users u ON u.id = s.user_id
        WHERE s.id = ?
    """, (sid,)).fetchone()
    if not s:
        conn.close()
        flash("Öğrenci bulunamadı.", "error")
        return redirect(url_for("admin_panel"))

    veli = conn.execute(
        "SELECT id, name, tc_no FROM users WHERE role='parent' AND student_id = ?",
        (sid,)
    ).fetchone()

    if request.method == "POST":
        ad = request.form.get("ad", "").strip()
        tc = request.form.get("tc", "").strip()
        sinif = request.form.get("sinif", "").strip()
        numara = request.form.get("numara", "").strip()
        yeni_sifre = request.form.get("yeni_sifre", "").strip()
        v_ad = request.form.get("veli_ad", "").strip()
        v_tc = request.form.get("veli_tc", "").strip()
        v_sifre = request.form.get("veli_sifre", "").strip()

        try:
            conn.execute("UPDATE users SET name = ?, tc_no = ? WHERE id = ?",
                         (ad, tc, s["uid"]))
            conn.execute("UPDATE students SET sinif = ?, numara = ? WHERE id = ?",
                         (sinif, int(numara), sid))
            if yeni_sifre:
                conn.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                             (generate_password_hash(yeni_sifre), s["uid"]))
            if veli:
                if v_ad or v_tc:
                    conn.execute("UPDATE users SET name = ?, tc_no = ? WHERE id = ?",
                                 (v_ad or veli["name"], v_tc or veli["tc_no"], veli["id"]))
                if v_sifre:
                    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                                 (generate_password_hash(v_sifre), veli["id"]))
            elif v_ad and v_tc and v_sifre:
                conn.execute("INSERT INTO users (tc_no, password_hash, name, role, student_id) VALUES (?,?,?,?,?)",
                             (v_tc, generate_password_hash(v_sifre), v_ad, "parent", sid))
            conn.commit()
            flash("Öğrenci bilgileri güncellendi.", "success")
            conn.close()
            return redirect(url_for("admin_panel"))
        except Exception as e:
            conn.rollback()
            flash(f"Hata: {e}", "error")
            conn.close()
            return redirect(url_for("admin_edit_student", sid=sid))

    conn.close()
    return render_template("ogrenci_duzenle.html",
                           ogrenci=dict(s),
                           veli=dict(veli) if veli else None)

@app.route("/admin/sifre-sifirla/<int:uid>", methods=["POST"])
@login_required("admin")
def admin_sifre_sifirla(uid):
    yeni = request.form.get("yeni_sifre", "").strip()
    if len(yeni) < 5:
        flash("Yeni şifre en az 5 karakter olmalı.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                     (generate_password_hash(yeni), uid))
        conn.commit()
        try:
            _k = conn.execute("SELECT email, name FROM users WHERE id = ?", (uid,)).fetchone()
            if _k and _k["email"]:
                send_email("Sifreniz Yenilendi", _k["email"],
                           sablon_sifre_sifirlandi(_k["name"], yeni))
        except Exception as _e:
            print(f"[admin_sifre_sifirla] mail hata: {_e}", flush=True)
        flash("Şifre başarıyla değiştirildi.", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
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
        flash("Tüm alanlar zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        mevcut = conn.execute("SELECT role FROM users WHERE tc_no = ?", (tc,)).fetchone()
        if mevcut:
            conn.close()
            rol_tr = {"student": "öğrenci", "parent": "veli", "teacher": "öğretmen", "admin": "yönetici"}.get(mevcut["role"], mevcut["role"])
            flash(f"Bu T.C. ({tc}) zaten {rol_tr} olarak kayıtlı. Aynı numara iki kez kullanılamaz.", "error")
            return redirect(url_for("admin_panel"))

        conn.execute("INSERT INTO users (tc_no, password_hash, name, role) VALUES (?,?,?,?)",
                     (tc, generate_password_hash(sifre), ad, "teacher"))
        conn.commit()
        try:
            _giris = request.url_root.rstrip("/") + url_for("login")
            _email = request.form.get("email", "").strip()
            if _email:
                send_email("C-Peak Panel Kaydiniz", _email,
                           sablon_kayit(ad, tc, sifre, _giris))
        except Exception as _e:
            print(f"[admin_add_teacher] mail hata: {_e}", flush=True)
        flash(f"Öğretmen eklendi: {ad}", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash(f"Bu T.C. ({tc}) zaten sistemde kayıtlı.", "error")
        else:
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
        flash("Ders adı zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO courses (ad, ogretmen_id) VALUES (?,?)",
                     (ad, int(ogr_id) if ogr_id else None))
        conn.commit()
        flash(f"Ders eklendi: {ad}", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
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
        flash("Tüm alanlar zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO grades (student_id, course_id, sinav, puan, tarih) VALUES (?,?,?,?,?)",
                     (int(sid), int(cid), sinav, float(puan), date.today().isoformat()))
        conn.commit()
        try:
            _ogr = conn.execute("""
                SELECT u.name AS ad, u.email AS ogr_mail, s.id AS sid
                FROM students s JOIN users u ON u.id = s.user_id
                WHERE s.id = ?
            """, (int(sid),)).fetchone()
            _ders = conn.execute("SELECT ad FROM courses WHERE id = ?", (int(cid),)).fetchone()
            if _ogr and _ders:
                if _ogr["ogr_mail"]:
                    send_email("Yeni Notunuz: " + _ders["ad"], _ogr["ogr_mail"],
                               sablon_not_girildi(_ogr["ad"], _ders["ad"], sinav, puan))
                _veli = conn.execute(
                    "SELECT email FROM users WHERE role='parent' AND student_id = ? LIMIT 1",
                    (_ogr["sid"],)
                ).fetchone()
                if _veli and _veli["email"]:
                    send_email("Yeni Not: " + _ders["ad"], _veli["email"],
                               sablon_not_girildi(_ogr["ad"], _ders["ad"], sinav, puan))
        except Exception as _e:
            print(f"[admin_add_grade] mail hata: {_e}", flush=True)
        flash(f"Not eklendi: {sinav} = {puan}", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
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
        flash("Öğrenci, tarih ve durum zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO attendance (student_id, tarih, durum, aciklama) VALUES (?,?,?,?)",
                     (int(sid), tarih, durum, aciklama or None))
        conn.commit()
        flash("Devamsızlık kaydı eklendi.", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
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
        flash("Başlık ve içerik zorunlu.", "error")
        return redirect(url_for("admin_panel"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO announcements (baslik, icerik, tarih, yazar_id) VALUES (?,?,?,?)",
                     (baslik, icerik, date.today().strftime("%d.%m.%Y"), session["user_id"]))
        conn.commit()
        flash("Duyuru yayınlandı.", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
            flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/admin/talep-coz/<int:tid>", methods=["POST"])
@login_required("admin")
def admin_talep_coz(tid):
    yeni_sifre = request.form.get("yeni_sifre", "").strip()
    if len(yeni_sifre) < 5:
        flash("Yeni sifre en az 5 karakter olmali.", "error")
        return redirect(url_for("admin_panel"))

    conn = get_db()
    try:
        talep = conn.execute(
            "SELECT tc_no, user_name FROM reset_requests WHERE id = ?",
            (tid,)
        ).fetchone()

        if not talep:
            flash("Talep bulunamadi.", "error")
            return redirect(url_for("admin_panel"))

        u = conn.execute(
            "SELECT id, name FROM users WHERE tc_no = ?",
            (talep["tc_no"],)
        ).fetchone()

        if not u:
            flash(f"Bu T.C. sistemde kayitli degil.", "error")
            return redirect(url_for("admin_panel"))

        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(yeni_sifre), u["id"])
        )
        conn.execute("DELETE FROM reset_requests WHERE id = ?", (tid,))
        conn.commit()
        flash(f"{u['name']} icin yeni sifre atandi ve talep kapatildi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/admin/talep-sil/<int:tid>", methods=["POST"])
@login_required("admin")
def admin_talep_sil(tid):
    conn = get_db()
    try:
        conn.execute("DELETE FROM reset_requests WHERE id = ?", (tid,))
        conn.commit()
        flash("Talep kaldırıldı.", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
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
        flash("Kayıt silindi.", "success")
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            flash("Bu T.C. numarası zaten sistemde kayıtlı.", "error")
        else:
            flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))

# ============================================================
# TOPLU NOT GİRİŞİ (admin + öğretmen)
# ============================================================

@app.route("/not-giris", methods=["GET"])
@login_required()
def not_giris():
    role = session.get("role")
    if role not in ("admin", "teacher"):
        flash("Bu sayfaya erişim yetkiniz yok.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()

    # Öğretmen sadece kendi derslerini görsün
    if role == "teacher":
        courses = conn.execute(
            "SELECT id, ad FROM courses WHERE ogretmen_id = ? ORDER BY ad",
            (session["user_id"],)
        ).fetchall()
    else:
        courses = conn.execute("SELECT id, ad FROM courses ORDER BY ad").fetchall()

    # Tüm öğrenciler
    students = conn.execute("""
        SELECT s.id, s.sinif, s.numara, u.name AS ad
        FROM students s JOIN users u ON u.id = s.user_id
        ORDER BY s.sinif, s.numara
    """).fetchall()

    # Filtre (opsiyonel)
    course_id = request.args.get("course_id", type=int)
    sinav = request.args.get("sinav", "").strip()

    mevcut_notlar = {}
    if course_id and sinav:
        rows = conn.execute(
            "SELECT student_id, puan FROM grades WHERE course_id = ? AND sinav = ?",
            (course_id, sinav)
        ).fetchall()
        for r in rows:
            mevcut_notlar[r["student_id"]] = r["puan"]

    conn.close()

    return render_template("not_giris.html",
                           courses=[dict(c) for c in courses],
                           students=[dict(s) for s in students],
                           mevcut_notlar=mevcut_notlar,
                           secili_course=course_id,
                           secili_sinav=sinav)

@app.route("/not-ekle-toplu", methods=["POST"])
@login_required()
def not_ekle_toplu():
    role = session.get("role")
    if role not in ("admin", "teacher"):
        return redirect(url_for("dashboard"))

    course_id = request.form.get("course_id", type=int)
    sinav = request.form.get("sinav", "").strip()

    if not course_id or not sinav:
        flash("Ders ve sınav türü seçiniz.", "error")
        return redirect(url_for("not_giris"))

    conn = get_db()
    kaydedilen = 0
    try:
        for key, val in request.form.items():
            if not key.startswith("puan_"):
                continue
            sid_str = key[5:]
            try:
                sid = int(sid_str)
            except ValueError:
                continue
            val = (val or "").strip()
            if not val:
                continue
            try:
                puan = float(val.replace(",", "."))
            except ValueError:
                continue
            if puan < 0 or puan > 100:
                continue

            # Aynı kaydı sil (varsa), yenisini ekle
            conn.execute(
                "DELETE FROM grades WHERE student_id = ? AND course_id = ? AND sinav = ?",
                (sid, course_id, sinav)
            )
            conn.execute(
                "INSERT INTO grades (student_id, course_id, sinav, puan, tarih) VALUES (?,?,?,?,?)",
                (sid, course_id, sinav, puan, date.today().isoformat())
            )
            kaydedilen += 1

        conn.commit()
        if kaydedilen:
            flash(f"{kaydedilen} not kaydedildi.", "success")
        else:
            flash("Hiçbir puan girilmedi.", "error")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for("not_giris", course_id=course_id, sinav=sinav))

# ============================================================
# TOPLU YOKLAMA (devamsızlık)
# ============================================================

@app.route("/devamsizlik-giris", methods=["GET"])
@login_required()
def devamsizlik_giris():
    role = session.get("role")
    if role not in ("admin", "teacher"):
        flash("Bu sayfaya erişim yetkiniz yok.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()

    # Sınıflar (filtre için)
    siniflar = [r["sinif"] for r in conn.execute(
        "SELECT DISTINCT sinif FROM students ORDER BY sinif"
    ).fetchall()]

    # Seçili tarih ve sınıf
    tarih = request.args.get("tarih", date.today().isoformat())
    sinif = request.args.get("sinif", "").strip()

    # Öğrenciler (filtreye göre)
    if sinif:
        students = conn.execute("""
            SELECT s.id, s.sinif, s.numara, u.name AS ad
            FROM students s JOIN users u ON u.id = s.user_id
            WHERE s.sinif = ?
            ORDER BY s.numara
        """, (sinif,)).fetchall()
    else:
        students = conn.execute("""
            SELECT s.id, s.sinif, s.numara, u.name AS ad
            FROM students s JOIN users u ON u.id = s.user_id
            ORDER BY s.sinif, s.numara
        """).fetchall()

    # O gün için mevcut kayıtlar
    mevcut = {}
    if tarih:
        rows = conn.execute(
            "SELECT student_id, durum, aciklama FROM attendance WHERE tarih = ?",
            (tarih,)
        ).fetchall()
        for r in rows:
            mevcut[r["student_id"]] = {"durum": r["durum"], "aciklama": r["aciklama"]}

    conn.close()

    return render_template("devamsizlik_giris.html",
                           siniflar=siniflar,
                           students=[dict(s) for s in students],
                           mevcut=mevcut,
                           tarih=tarih,
                           secili_sinif=sinif)

@app.route("/devamsizlik-kaydet", methods=["POST"])
@login_required()
def devamsizlik_kaydet():
    role = session.get("role")
    if role not in ("admin", "teacher"):
        return redirect(url_for("dashboard"))

    tarih = request.form.get("tarih", "").strip()
    sinif = request.form.get("sinif", "").strip()

    if not tarih:
        flash("Tarih seçiniz.", "error")
        return redirect(url_for("devamsizlik_giris"))

    conn = get_db()
    kaydedilen = 0
    try:
        for key, val in request.form.items():
            if not key.startswith("durum_"):
                continue
            sid_str = key[6:]
            try:
                sid = int(sid_str)
            except ValueError:
                continue
            val = (val or "").strip()
            if val not in ("geldi", "gelmedi", "izinli"):
                continue

            aciklama = request.form.get(f"aciklama_{sid}", "").strip() or None

            # Aynı gün + öğrenci için varsa güncelle
            conn.execute(
                "DELETE FROM attendance WHERE student_id = ? AND tarih = ?",
                (sid, tarih)
            )
            conn.execute(
                "INSERT INTO attendance (student_id, tarih, durum, aciklama) VALUES (?,?,?,?)",
                (sid, tarih, val, aciklama)
            )
            kaydedilen += 1
            if val == "gelmedi":
                try:
                    _ogr = conn.execute("""
                        SELECT u.name AS ad, s.sinif FROM students s
                        JOIN users u ON u.id = s.user_id WHERE s.id = ?
                    """, (sid,)).fetchone()
                    _veli = conn.execute(
                        "SELECT email FROM users WHERE role='parent' AND student_id = ? LIMIT 1",
                        (sid,)
                    ).fetchone()
                    if _ogr and _veli and _veli["email"]:
                        send_email("Devamsizlik Bildirimi", _veli["email"],
                                   sablon_devamsizlik(_ogr["ad"], _ogr["sinif"], tarih))
                except Exception as _e:
                    print(f"[devamsizlik] mail hata: {_e}", flush=True)

        conn.commit()
        if kaydedilen:
            flash(f"{kaydedilen} devamsızlık kaydı yapıldı.", "success")
        else:
            flash("Hiçbir öğrenci işaretlenmedi.", "error")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for("devamsizlik_giris", tarih=tarih, sinif=sinif))

# ============================================================
# HAFTALIK DERS PROGRAMI
# ============================================================

GUN_ADI = {1: "Pazartesi", 2: "Salı", 3: "Çarşamba", 4: "Perşembe", 5: "Cuma", 6: "Cumartesi", 7: "Pazar"}

@app.route("/ders-programi")
@login_required()
def ders_programi():
    role = session["role"]
    conn = get_db()

    sinif = None
    if role == "student":
        s = conn.execute("SELECT sinif FROM students WHERE user_id = ?",
                         (session["user_id"],)).fetchone()
        if s:
            sinif = s["sinif"]
    elif role == "parent":
        sid = session.get("student_id")
        if sid:
            s = conn.execute("SELECT sinif FROM students WHERE id = ?", (sid,)).fetchone()
            if s:
                sinif = s["sinif"]

    # Admin/öğretmen sınıf seçebilir
    if role in ("admin", "teacher"):
        sinif = request.args.get("sinif", "").strip() or None

    siniflar = [r["sinif"] for r in conn.execute(
        "SELECT DISTINCT sinif FROM students ORDER BY sinif"
    ).fetchall()]

    program = {}
    if sinif:
        rows = conn.execute("""
            SELECT sc.gun, sc.saat, c.ad AS ders
            FROM schedule sc JOIN courses c ON c.id = sc.ders_id
            WHERE sc.sinif = ?
            ORDER BY sc.gun, sc.saat
        """, (sinif,)).fetchall()
        for r in rows:
            program[(r["gun"], r["saat"])] = r["ders"]

    conn.close()
    return render_template("ders_programi.html",
                           sinif=sinif, siniflar=siniflar,
                           program=program, gunler=GUN_ADI,
                           saatler=range(1, 9))

@app.route("/odevler")
@login_required()
def odevler():
    role = session["role"]
    conn = get_db()

    if role == "student":
        # Öğrencinin sınıfı + dersler
        s = conn.execute("""
            SELECT id, sinif FROM students WHERE user_id = ?
        """, (session["user_id"],)).fetchone()
        if not s:
            conn.close()
            return redirect(url_for("dashboard"))
        rows = conn.execute("""
            SELECT h.id, h.baslik, h.verilis, h.teslim,
                   c.ad AS ders, u.name AS ogretmen,
                   (SELECT durum FROM homework_submission
                    WHERE homework_id = h.id AND student_id = ?) AS durum
            FROM homework h
            JOIN courses c ON c.id = h.ders_id
            JOIN users u ON u.id = h.ogretmen_id
            WHERE h.sinif IS NULL OR h.sinif = ?
            ORDER BY h.teslim DESC, h.id DESC
        """, (s["id"], s["sinif"])).fetchall()
    elif role == "teacher":
        rows = conn.execute("""
            SELECT h.id, h.baslik, h.verilis, h.teslim, h.sinif,
                   c.ad AS ders,
                   (SELECT COUNT(*) FROM homework_submission
                    WHERE homework_id = h.id) AS teslim_sayisi
            FROM homework h
            JOIN courses c ON c.id = h.ders_id
            WHERE h.ogretmen_id = ?
            ORDER BY h.id DESC
        """, (session["user_id"],)).fetchall()
    else:
        # admin hepsini görsün
        rows = conn.execute("""
            SELECT h.id, h.baslik, h.verilis, h.teslim, h.sinif,
                   c.ad AS ders, u.name AS ogretmen
            FROM homework h
            JOIN courses c ON c.id = h.ders_id
            JOIN users u ON u.id = h.ogretmen_id
            ORDER BY h.id DESC
        """).fetchall()

    conn.close()
    return render_template("odevler.html", odevler=[dict(r) for r in rows], role=role)

@app.route("/odev/<int:hid>")
@login_required()
def odev_detay(hid):
    role = session["role"]
    conn = get_db()

    h = conn.execute("""
        SELECT h.*, c.ad AS ders, u.name AS ogretmen
        FROM homework h
        JOIN courses c ON c.id = h.ders_id
        JOIN users u ON u.id = h.ogretmen_id
        WHERE h.id = ?
    """, (hid,)).fetchone()

    if not h:
        conn.close()
        flash("Ödev bulunamadı.", "error")
        return redirect(url_for("odevler"))

    teslim_listesi = []
    kendi_durum = None
    if role == "student":
        s = conn.execute("SELECT id FROM students WHERE user_id = ?",
                         (session["user_id"],)).fetchone()
        if s:
            kendi = conn.execute(
                "SELECT durum, tarih FROM homework_submission WHERE homework_id = ? AND student_id = ?",
                (hid, s["id"])
            ).fetchone()
            if kendi:
                kendi_durum = dict(kendi)
    elif role in ("teacher", "admin"):
        teslim_listesi = conn.execute("""
            SELECT u.name AS ad, s.sinif, s.numara, hs.durum, hs.tarih
            FROM homework_submission hs
            JOIN students s ON s.id = hs.student_id
            JOIN users u ON u.id = s.user_id
            WHERE hs.homework_id = ?
            ORDER BY s.sinif, s.numara
        """, (hid,)).fetchall()

    conn.close()
    return render_template("odev_detay.html",
                           odev=dict(h),
                           teslim_listesi=[dict(t) for t in teslim_listesi],
                           kendi_durum=kendi_durum)

@app.route("/odev/<int:hid>/teslim", methods=["POST"])
@login_required("student")
def odev_teslim(hid):
    conn = get_db()
    s = conn.execute("SELECT id FROM students WHERE user_id = ?",
                     (session["user_id"],)).fetchone()
    if not s:
        conn.close()
        return redirect(url_for("dashboard"))

    try:
        conn.execute("DELETE FROM homework_submission WHERE homework_id = ? AND student_id = ?",
                     (hid, s["id"]))
        conn.execute("""
            INSERT INTO homework_submission (homework_id, student_id, durum, tarih)
            VALUES (?, ?, 'yapildi', ?)
        """, (hid, s["id"], date.today().isoformat()))
        conn.commit()
        flash("Ödev yapıldı olarak işaretlendi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("odev_detay", hid=hid))

@app.route("/ogretmen/odev-ver", methods=["GET", "POST"])
@login_required("teacher")
def ogretmen_odev_ver():
    conn = get_db()

    if request.method == "POST":
        ders_id = request.form.get("ders_id", type=int)
        sinif = request.form.get("sinif", "").strip()
        baslik = request.form.get("baslik", "").strip()
        icerik = request.form.get("icerik", "").strip()
        teslim = request.form.get("teslim", "").strip()

        if not (ders_id and baslik and teslim):
            flash("Ders, başlık ve teslim tarihi zorunlu.", "error")
            return redirect(url_for("ogretmen_odev_ver"))

        try:
            conn.execute("""
                INSERT INTO homework (ders_id, ogretmen_id, sinif, baslik, icerik, verilis, teslim)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ders_id, session["user_id"], sinif or None,
                  baslik, icerik or None,
                  date.today().isoformat(), teslim))
            conn.commit()
            flash("Ödev yayınlandı.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Hata: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for("ogretmen_odev_ver"))

    dersler = conn.execute(
        "SELECT id, ad FROM courses WHERE ogretmen_id = ? ORDER BY ad",
        (session["user_id"],)
    ).fetchall()
    siniflar = [r["sinif"] for r in conn.execute(
        "SELECT DISTINCT sinif FROM students ORDER BY sinif"
    ).fetchall()]
    conn.close()
    return render_template("ogretmen_odev_ver.html",
                           dersler=[dict(d) for d in dersler],
                           siniflar=siniflar)

# ============================================================
# DERS PROGRAMI DÜZENLEME (admin + öğretmen)
# ============================================================

@app.route("/ders-programi/duzenle", methods=["GET", "POST"])
@login_required("admin", "teacher")
def ders_programi_duzenle():
    role = session.get("role")
    conn = get_db()

    if request.method == "POST":
        sinif = request.form.get("sinif", "").strip()
        gun = request.form.get("gun", type=int)
        saat = request.form.get("saat", type=int)
        ders_id = request.form.get("ders_id", type=int)

        if not (sinif and gun and saat and ders_id):
            flash("Tüm alanlar zorunlu.", "error")
            return redirect(url_for("ders_programi_duzenle", sinif=sinif))

        if role == "teacher":
            ders = conn.execute(
                "SELECT 1 FROM courses WHERE id = ? AND ogretmen_id = ?",
                (ders_id, session["user_id"])
            ).fetchone()
            if not ders:
                conn.close()
                flash("Bu ders size atanmamış.", "error")
                return redirect(url_for("ders_programi_duzenle", sinif=sinif))

        try:
            conn.execute("DELETE FROM schedule WHERE sinif = ? AND gun = ? AND saat = ?",
                         (sinif, gun, saat))
            conn.execute("INSERT INTO schedule (sinif, gun, saat, ders_id) VALUES (?,?,?,?)",
                         (sinif, gun, saat, ders_id))
            conn.commit()
            flash("Ders programa kaydedildi.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Hata: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for("ders_programi_duzenle", sinif=sinif))

    siniflar = [r["sinif"] for r in conn.execute(
        "SELECT DISTINCT sinif FROM students ORDER BY sinif"
    ).fetchall()]

    if role == "teacher":
        dersler = conn.execute(
            "SELECT id, ad FROM courses WHERE ogretmen_id = ? ORDER BY ad",
            (session["user_id"],)
        ).fetchall()
    else:
        dersler = conn.execute("SELECT id, ad FROM courses ORDER BY ad").fetchall()

    sinif = request.args.get("sinif", "").strip() or (siniflar[0] if siniflar else None)

    program = {}
    if sinif:
        rows = conn.execute("""
            SELECT sc.id, sc.gun, sc.saat, c.ad AS ders, c.ogretmen_id
            FROM schedule sc JOIN courses c ON c.id = sc.ders_id
            WHERE sc.sinif = ?
            ORDER BY sc.gun, sc.saat
        """, (sinif,)).fetchall()
        for r in rows:
            program[(r["gun"], r["saat"])] = dict(r)

    conn.close()

    return render_template("ders_programi_yonetim.html",
                           sinif=sinif,
                           siniflar=siniflar,
                           dersler=[dict(d) for d in dersler],
                           program=program,
                           gunler=GUN_ADI,
                           saatler=range(1, 9),
                           role=role)


@app.route("/ders-programi/sil/<int:sid>", methods=["POST"])
@login_required("admin", "teacher")
def ders_programi_sil(sid):
    role = session.get("role")
    sinif = request.form.get("sinif", "").strip()
    conn = get_db()
    try:
        if role == "teacher":
            row = conn.execute("""
                SELECT c.ogretmen_id FROM schedule sc
                JOIN courses c ON c.id = sc.ders_id
                WHERE sc.id = ?
            """, (sid,)).fetchone()
            if not row or row["ogretmen_id"] != session["user_id"]:
                conn.close()
                flash("Bu kaydı silme yetkiniz yok.", "error")
                return redirect(url_for("ders_programi_duzenle", sinif=sinif))

        conn.execute("DELETE FROM schedule WHERE id = ?", (sid,))
        conn.commit()
        flash("Kayıt silindi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Hata: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("ders_programi_duzenle", sinif=sinif))


# ============================================================
# ESKİ URL YÖNLENDİRMELERİ
# ============================================================

@app.route("/admin/ders-programi")
@login_required("admin")
def admin_ders_programi():
    sinif = request.args.get("sinif", "")
    if sinif:
        return redirect(url_for("ders_programi_duzenle", sinif=sinif))
    return redirect(url_for("ders_programi_duzenle"))


# ============================================================
# Gelistirme sunucusunu baslat
# ============================================================


# === BILDIRIM ROUTES ===
from flask import jsonify as _jsonify, request as _req, abort as _abort
from models import get_db as _get_db


@app.route("/bildirim-gonder", methods=["POST"])
@app.limiter.limit("5 per minute")
def bildirim_gonder():
    """Kullanicidan bildirim al. CSRF Flask-WTF tarafindan korunur."""
    if not session.get("name"):
        return _jsonify(ok=False, hata="Giris yapmalisiniz"), 401

    tur = (_req.form.get("tur") or "diger").strip().lower()
    baslik = (_req.form.get("baslik") or "").strip()[:120]
    mesaj = (_req.form.get("mesaj") or "").strip()[:2000]
    sayfa_url = (_req.form.get("sayfa") or "")[:500]
    tarayici = (_req.headers.get("User-Agent") or "")[:500]

    if tur not in ("hata", "oneri", "diger"):
        tur = "diger"
    if len(baslik) < 3 or len(mesaj) < 5:
        return _jsonify(ok=False, hata="Baslik ve mesaj en az 3-5 karakter olmali"), 400

    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO feedback (user_id, user_name, user_tc, role, tur, baslik, mesaj, sayfa_url, tarayici) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                session.get("user_id") or session.get("uid") or session.get("id"),
                session.get("name"),
                session.get("tc_no"),
                session.get("role"),
                tur, baslik, mesaj, sayfa_url, tarayici,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return _jsonify(ok=True, mesaj="Bildiriminiz alindi, tesekkurler.")


@app.route("/admin/bildirimler")
def admin_bildirimler():
    if session.get("role") != "admin":
        _abort(403)
    filtre = (_req.args.get("durum") or "tumu").strip().lower()

    conn = _get_db()
    try:
        if filtre in ("yeni", "okundu", "cozuldu"):
            rows = conn.execute(
                "SELECT * FROM feedback WHERE durum = ? ORDER BY tarih DESC",
                (filtre,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM feedback ORDER BY "
                "CASE durum WHEN 'yeni' THEN 0 WHEN 'okundu' THEN 1 ELSE 2 END, "
                "tarih DESC"
            ).fetchall()
        # Sayilar
        sayilar = dict(conn.execute(
            "SELECT durum, COUNT(*) FROM feedback GROUP BY durum"
        ).fetchall())
    finally:
        conn.close()

    return render_template(
        "bildirimler.html",
        bildirimler=[dict(r) for r in rows],
        filtre=filtre,
        yeni_sayi=sayilar.get("yeni", 0),
        okundu_sayi=sayilar.get("okundu", 0),
        cozuldu_sayi=sayilar.get("cozuldu", 0),
        toplam=sum(sayilar.values()),
    )


@app.route("/admin/bildirim-coz/<int:bid>", methods=["POST"])
def admin_bildirim_coz(bid):
    if session.get("role") != "admin":
        _abort(403)
    conn = _get_db()
    try:
        conn.execute("UPDATE feedback SET durum = 'cozuldu' WHERE id = ?", (bid,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("admin_bildirimler"))


@app.route("/admin/bildirim-sil/<int:bid>", methods=["POST"])
def admin_bildirim_sil(bid):
    if session.get("role") != "admin":
        _abort(403)
    conn = _get_db()
    try:
        conn.execute("DELETE FROM feedback WHERE id = ?", (bid,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("admin_bildirimler"))


@app.route("/admin/bildirim-oku/<int:bid>", methods=["POST"])
def admin_bildirim_oku(bid):
    """Yeni durumundan okundu'ya gecir."""
    if session.get("role") != "admin":
        _abort(403)
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE feedback SET durum = 'okundu' WHERE id = ? AND durum = 'yeni'",
            (bid,),
        )
        conn.commit()
    finally:
        conn.close()
    return _jsonify(ok=True)



@app.route("/api/yeni-bildirim-sayi")
def api_yeni_bildirim_sayi():
    """Sadece admin icin: yeni durumdaki bildirim sayisi."""
    if session.get("role") != "admin":
        return _jsonify(ok=False, sayi=0), 403
    conn = _get_db()
    try:
        r = conn.execute(
            "SELECT COUNT(*) AS n FROM feedback WHERE durum = 'yeni'"
        ).fetchone()
        n = r["n"] if r else 0
    except Exception:
        n = 0
    finally:
        conn.close()
    return _jsonify(ok=True, sayi=n)



@app.route("/admin/bildirim-cevapla/<int:bid>", methods=["POST"])
def admin_bildirim_cevapla(bid):
    """Admin bir bildirime cevap yazar."""
    if session.get("role") != "admin":
        _abort(403)
    cevap = (_req.form.get("cevap") or "").strip()[:2000]
    if not cevap:
        return redirect(url_for("admin_bildirimler"))
    from datetime import datetime as _dt
    tarih = _dt.now().strftime("%d.%m.%Y %H:%M")
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE feedback SET cevap = ?, cevap_tarih = ?, durum = 'cozuldu' WHERE id = ?",
            (cevap, tarih, bid),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("admin_bildirimler"))



@app.route("/bildirimlerim")
def bildirimlerim():
    """Kullanici kendi gonderdigi bildirimleri ve admin cevaplarini gorur."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    uid = session.get("user_id")
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM feedback WHERE user_id = ? ORDER BY id DESC",
            (uid,),
        ).fetchall()
    finally:
        conn.close()
    return render_template("bildirimlerim.html", bildirimler=[dict(r) for r in rows])


@app.route("/api/bildirim-cevap-sayi")
def api_bildirim_cevap_sayi():
    """Kullanicinin cevaplanmis ama gormedigi bildirim sayisi."""
    if not session.get("user_id"):
        return _jsonify(ok=False, sayi=0), 401
    uid = session.get("user_id")
    conn = _get_db()
    try:
        r = conn.execute(
            "SELECT COUNT(*) AS n FROM feedback "
            "WHERE user_id = ? AND cevap IS NOT NULL AND cevap != ''",
            (uid,),
        ).fetchone()
        n = r["n"] if r else 0
    except Exception:
        n = 0
    finally:
        conn.close()
    return _jsonify(ok=True, sayi=n)

# === /BILDIRIM ROUTES ===




# ============================================================
# KURULUM ENDPOINT - veritabani + admin olusturur
# Tarayicidan: https://cpeak-panel.onrender.com/kur
# ============================================================
@app.route("/kur")
def kur_endpoint():
    import os as _os_kur
    if _os_kur.environ.get("KUR_AKTIF") != "1":
        return "Bu sayfa devre disi.", 403
    """Veritabani ve admin olustur. Ilk kurulum icin."""
    import traceback as _tb
    sonuc = []

    # DB path bilgisi
    import os as _os
    db_yolu = _os.environ.get("DB_PATH", "egitim.db")
    sonuc.append(f"DB_PATH: {db_yolu}")
    sonuc.append(f"DB var mi: {_os.path.exists(db_yolu)}")

    try:
        from models import init_db, seed_admin, DB_PATH as _DBP
        sonuc.append(f"models.DB_PATH: {_DBP}")

        try:
            init_db()
            sonuc.append("[OK] init_db calisti")
        except Exception as e:
            sonuc.append(f"[HATA] init_db: {e}")
            sonuc.append(_tb.format_exc())

        try:
            seed_admin()
            sonuc.append("[OK] seed_admin calisti")
        except Exception as e:
            sonuc.append(f"[HATA] seed_admin: {e}")
            sonuc.append(_tb.format_exc())

        # Kontrol - kac kullanici var?
        try:
            conn = get_db()
            kullanicilar = conn.execute(
                "SELECT id, tc_no, name, role FROM users"
            ).fetchall()
            sonuc.append(f"Toplam kullanici: {len(kullanicilar)}")
            for k in kullanicilar:
                sonuc.append(f"  - {dict(k)}")
            conn.close()
        except Exception as e:
            sonuc.append(f"[HATA] Kullanici listesi: {e}")

    except Exception as e:
        sonuc.append(f"[HATA] Import: {e}")
        sonuc.append(_tb.format_exc())

    from flask import Response as _R
    return _R(
        "<pre style='font:13px/1.5 monospace;padding:20px;"
        "background:#18181b;color:#e4e4e7;'>"
        + "\n".join(sonuc)
        + "</pre>",
        mimetype="text/html"
    )
# ============================================================



# ============================================================
# ADMIN TEST E-POSTA
# ============================================================
@app.route("/admin/test-email", methods=["GET", "POST"])
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



# ============================================================
# ADMIN - MAIL GONDER
# ============================================================
@app.route("/admin/mail-gonder", methods=["GET", "POST"])
@login_required("admin")
def admin_mail_gonder():
    from mail_service import HAZIR_SABLONLAR, sablon_ozel
    conn = get_db()
    try:
        kullanicilar = conn.execute(
            "SELECT id, name, tc_no, role, email FROM users ORDER BY role, name"
        ).fetchall()
    finally:
        conn.close()

    onizleme = None
    if request.method == "POST":
        aksiyon = request.form.get("aksiyon", "gonder")
        alici_tipi = request.form.get("alici_tipi", "tek")
        konu = (request.form.get("konu") or "").strip()
        icerik = request.form.get("icerik") or ""
        renk = request.form.get("renk") or "#f59e0b"

        # Alici listesi
        alicilar = []
        if alici_tipi == "tek":
            uid = request.form.get("kullanici_id", "").strip()
            if uid:
                conn = get_db()
                try:
                    r = conn.execute("SELECT email FROM users WHERE id = ?", (int(uid),)).fetchone()
                    if r and r["email"]:
                        alicilar = [r["email"]]
                finally:
                    conn.close()
        elif alici_tipi == "rol":
            rol = request.form.get("rol", "").strip()
            if rol in ("student", "parent", "teacher", "admin"):
                conn = get_db()
                try:
                    rows = conn.execute(
                        "SELECT email FROM users WHERE role = ? AND email IS NOT NULL AND email != ''",
                        (rol,)
                    ).fetchall()
                    alicilar = [r["email"] for r in rows if r["email"]]
                finally:
                    conn.close()
        elif alici_tipi == "manuel":
            m = request.form.get("manuel_email", "")
            alicilar = [e.strip() for e in m.split(",") if "@" in e and e.strip()]

        # HTML olustur
        html = sablon_ozel(konu or "Bilgilendirme", icerik, renk)

        if aksiyon == "onizle":
            onizleme = html
            flash("Onizleme asagida gosteriliyor. Kontrol edip 'Mail Gonder' butonuna basin.", "success")
        else:
            if not alicilar:
                flash("Alici secilmedi veya gecerli mail adresi yok.", "error")
            elif not konu:
                flash("Konu bos olamaz.", "error")
            else:
                try:
                    send_email(konu, alicilar, html)
                    flash("Mail " + str(len(alicilar)) + " kisiye kuyruga alindi.", "success")
                except Exception as e:
                    flash("Hata: " + str(e), "error")
                return redirect(url_for("admin_mail_gonder"))

    return render_template(
        "admin_mail.html",
        kullanicilar=[dict(u) for u in kullanicilar],
        sablonlar=HAZIR_SABLONLAR,
        onizleme=onizleme,
    )
# ============================================================

if __name__ == "__main__":
    import os as _os
    _debug = _os.environ.get("FLASK_DEBUG", "1").lower() in ("1","true","yes","on")
    _host  = _os.environ.get("FLASK_HOST", "127.0.0.1")
    _port  = int(_os.environ.get("FLASK_PORT", "5000"))
    app.run(debug=_debug, host=_host, port=_port)
