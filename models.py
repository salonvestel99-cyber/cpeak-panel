# -*- coding: utf-8 -*-
"""SQLite veritabanı katmanı."""

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


CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sinif TEXT NOT NULL,
    gun INTEGER NOT NULL,
    saat INTEGER NOT NULL,
    ders_id INTEGER NOT NULL,
    FOREIGN KEY(ders_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ders_id INTEGER NOT NULL,
    ogretmen_id INTEGER NOT NULL,
    sinif TEXT,
    baslik TEXT NOT NULL,
    icerik TEXT,
    verilis TEXT NOT NULL,
    teslim TEXT NOT NULL,
    FOREIGN KEY(ders_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY(ogretmen_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS homework_submission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    homework_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    durum TEXT NOT NULL CHECK(durum IN ('yapildi','yapilmadi')),
    tarih TEXT NOT NULL,
    UNIQUE(homework_id, student_id),
    FOREIGN KEY(homework_id) REFERENCES homework(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reset_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tc_no TEXT NOT NULL,
    user_name TEXT,
    role TEXT,
    email TEXT,
    mesaj TEXT,
    tarih TEXT NOT NULL,
    durum TEXT DEFAULT 'bekliyor'
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    tarih TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_feedback_durum ON feedback(durum);
CREATE INDEX IF NOT EXISTS idx_feedback_tarih ON feedback(tarih DESC);
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    # Eski veritabanına eksik sütun varsa ekle
    try:
        conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def seed_admin():
    from werkzeug.security import generate_password_hash
    tc = os.environ.get("ADMIN_TC", "11111111111")
    sifre = os.environ.get("ADMIN_PASSWORD", "admin123")
    ad = os.environ.get("ADMIN_NAME", "Sistem Yöneticisi")
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
