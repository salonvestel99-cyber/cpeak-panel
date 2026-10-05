# -*- coding: utf-8 -*-
"""PostgreSQL (Supabase) veritabani katmani.

sqlite3 API'sini taklit eden ince bir adaptor kullanir; bu sayede
app.py'de hicbir degisiklik gerekmez. Sadece DATABASE_URL ortam
degiskenini tanimlamaniz yeterlidir.
"""

import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL", "")
# app.py /kur endpoint'i DB_PATH import ediyor -> geriye donuk uyumluluk
DB_PATH = DATABASE_URL


# ============================================================
# sqlite3.Row benzeri satir nesnesi
# ============================================================
class PgRow:
    __slots__ = ("_cols", "_vals", "_map")

    def __init__(self, cols, vals):
        self._cols = list(cols)
        self._vals = list(vals)
        self._map = dict(zip(self._cols, self._vals))

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._vals[key]
        return self._map[key]

    def __contains__(self, key):
        return key in self._map

    def __iter__(self):
        return iter(self._vals)

    def __len__(self):
        return len(self._vals)

    def keys(self):
        return list(self._cols)

    def get(self, key, default=None):
        return self._map.get(key, default)

    def __repr__(self):
        return f"PgRow({self._map})"


def _wrap(cursor, raw):
    if raw is None:
        return None
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return PgRow(cols, raw)


# ============================================================
# sqlite3.Cursor benzeri sarmalayici
# ============================================================
class PgCursor:
    def __init__(self, conn):
        self._conn = conn
        self._cur = conn._pg.cursor()
        self._lastrowid = None

    def execute(self, sql, params=None):
        sql = sql.replace("?", "%s").strip().rstrip(";")
        upper = sql.upper()
        if upper.startswith("INSERT") and "RETURNING" not in upper:
            self._cur.execute(sql + " RETURNING id", params or ())
            r = self._cur.fetchone()
            self._lastrowid = r[0] if r else None
        else:
            self._cur.execute(sql, params or ())
        return self

    def executescript(self, sql):
        # PRAGMA satirlarini at, kalanini oldugu gibi calistir
        temiz = "\n".join(
            s for s in sql.splitlines()
            if not s.strip().upper().startswith("PRAGMA")
        )
        self._cur.execute(temiz)

    def fetchone(self):
        return _wrap(self._cur, self._cur.fetchone())

    def fetchall(self):
        rows = self._cur.fetchall()
        return [_wrap(self._cur, r) for r in rows] if rows else []

    def close(self):
        try:
            self._cur.close()
        except Exception:
            pass

    @property
    def lastrowid(self):
        return self._lastrowid

    @property
    def rowcount(self):
        return self._cur.rowcount


# ============================================================
# sqlite3.Connection benzeri sarmalayici
# ============================================================
class PgConn:
    def __init__(self, url):
        # URL'i manuel ayristir: postgresql://user:pass@host:port/db
        from urllib.parse import urlparse, unquote
        p = urlparse(url)
        self._pg = psycopg2.connect(
            dbname=p.path.lstrip("/") or "postgres",
            user=unquote(p.username or "postgres"),
            password=unquote(p.password or ""),
            host=p.hostname,
            port=p.port or 5432,
        )
        self._pg.autocommit = False

    def execute(self, sql, params=None):
        c = PgCursor(self)
        c.execute(sql, params)
        return c

    def cursor(self):
        return PgCursor(self)

    def executescript(self, sql):
        c = PgCursor(self)
        c.executescript(sql)
        return c

    def commit(self):
        self._pg.commit()

    def rollback(self):
        try:
            self._pg.rollback()
        except Exception:
            pass

    def close(self):
        try:
            self._pg.close()
        except Exception:
            pass

    @property
    def row_factory(self):
        return PgRow

    @row_factory.setter
    def row_factory(self, _v):
        pass


# ============================================================
# Sema (SQLite -> PostgreSQL cevirisi)
# ============================================================
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tc_no TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student','parent','teacher','admin')),
    student_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email TEXT
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    sinif TEXT NOT NULL,
    numara INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    ad TEXT NOT NULL,
    ogretmen_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS grades (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    sinav TEXT NOT NULL,
    puan REAL NOT NULL,
    tarih TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    tarih TEXT NOT NULL,
    durum TEXT NOT NULL CHECK(durum IN ('geldi','gelmedi','izinli')),
    aciklama TEXT
);

CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    baslik TEXT NOT NULL,
    icerik TEXT NOT NULL,
    tarih TEXT NOT NULL,
    yazar_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    sinif TEXT NOT NULL,
    gun INTEGER NOT NULL,
    saat INTEGER NOT NULL,
    ders_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS homework (
    id SERIAL PRIMARY KEY,
    ders_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    ogretmen_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sinif TEXT,
    baslik TEXT NOT NULL,
    icerik TEXT,
    verilis TEXT NOT NULL,
    teslim TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS homework_submission (
    id SERIAL PRIMARY KEY,
    homework_id INTEGER NOT NULL REFERENCES homework(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    durum TEXT NOT NULL CHECK(durum IN ('yapildi','yapilmadi')),
    tarih TEXT NOT NULL,
    UNIQUE(homework_id, student_id)
);

CREATE TABLE IF NOT EXISTS reset_requests (
    id SERIAL PRIMARY KEY,
    tc_no TEXT NOT NULL,
    user_name TEXT,
    role TEXT,
    email TEXT,
    mesaj TEXT,
    tarih TEXT NOT NULL,
    durum TEXT DEFAULT 'bekliyor'
);

CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    user_name TEXT,
    user_tc TEXT,
    role TEXT,
    tur TEXT NOT NULL CHECK(tur IN ('hata','oneri','diger')),
    baslik TEXT NOT NULL,
    mesaj TEXT NOT NULL,
    sayfa_url TEXT,
    tarayici TEXT,
    durum TEXT NOT NULL DEFAULT 'yeni' CHECK(durum IN ('yeni','okundu','cozuldu')),
    tarih TEXT NOT NULL DEFAULT to_char(now(), 'DD.MM.YYYY HH24:MI'),
    cevap TEXT,
    cevap_tarih TEXT
);

CREATE INDEX IF NOT EXISTS idx_feedback_durum ON feedback(durum);
CREATE INDEX IF NOT EXISTS idx_feedback_tarih ON feedback(tarih DESC);

ALTER TABLE feedback ADD COLUMN IF NOT EXISTS cevap TEXT;
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS cevap_tarih TEXT;
"""


def get_db():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL ortam degiskeni tanimli degil! "
            "Render > Environment > DATABASE_URL ekleyin."
        )
    return PgConn(DATABASE_URL)


def init_db():
    conn = get_db()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def seed_admin():
    tc = os.environ.get("ADMIN_TC", "11111111111")
    sifre = os.environ.get("ADMIN_PASSWORD", "admin123")
    ad = os.environ.get("ADMIN_NAME", "Sistem Yoneticisi")
    conn = get_db()
    try:
        var = conn.execute("SELECT 1 FROM users WHERE tc_no = ?", (tc,)).fetchone()
        if var:
            return
        conn.execute(
            "INSERT INTO users (tc_no, password_hash, name, role, student_id) VALUES (?,?,?,?,?)",
            (tc, generate_password_hash(sifre), ad, "admin", None)
        )
        conn.commit()
        print(f"  [seed] Admin olusturuldu -> T.C.: {tc}  |  Sifre: {sifre}")
    finally:
        conn.close()


# === CPK_SEVIYE_TESTI ===
def _seviye_testi_tablo(conn):
    """Tablo yoksa oluştur."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seviye_testleri (
            id SERIAL PRIMARY KEY,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            sinif TEXT,
            puan INTEGER NOT NULL,
            seviye TEXT NOT NULL,
            cevaplar TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def seviye_testi_kaydet(isim, telefon, sinif, puan, seviye, cevaplar):
    """Seviye testi sonucunu kaydeder."""
    conn = get_db()
    try:
        _seviye_testi_tablo(conn)
        conn.execute(
            "INSERT INTO seviye_testleri "
            "(isim, telefon, sinif, puan, seviye, cevaplar) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (isim, telefon, sinif, puan, seviye, cevaplar),
        )
        conn.commit()
    finally:
        conn.close()
# === /CPK_SEVIYE_TESTI ===

