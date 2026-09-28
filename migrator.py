# -*- coding: utf-8 -*-
"""
migrator.py — Idempotent Versioned File Patch System (v1)

Kullanım:
    python migrator.py

- migrations/ içindeki .py dosyalarını alfabetik sırayla işler.
- '_' ile başlayanları atlar (örn. _template.py).
- _applied.json içinde "id" varsa yamayı atlar → idempotent.
- Her dosya yazımından önce _backups/ altına zaman damgalı yedek alır.
- CRLF/LF duyarsız; orijinal satır sonu formatını korur.
- Kısmi başarıyı raporlar, başarılı kısımları yine de kaydeder.
"""

import os
import json
import shutil
import importlib.util
import datetime

# ---------- Sabitler ----------
MIGRATIONS_DIR = "migrations"
APPLIED_FILE = "_applied.json"
BACKUPS_DIR = "_backups"


# ---------- ANSI renkleri ----------
class C:
    R = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GRN = "\033[92m"; YLW = "\033[93m"
    CYN = "\033[96m"; GRY = "\033[90m"

if os.name == "nt":
    os.system("")  # Windows'ta ANSI'yi etkinleştir


# ---------- Yardımcılar ----------
def load_applied():
    if not os.path.exists(APPLIED_FILE):
        return {}
    try:
        with open(APPLIED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_applied(data):
    with open(APPLIED_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def backup_file(path):
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(path)
    dest = os.path.join(BACKUPS_DIR, f"{base}.{ts}.bak")
    shutil.copy2(path, dest)
    return dest


def detect_newline(text):
    return "\r\n" if "\r\n" in text else "\n"


def to_lf(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def load_patch(path):
    spec = importlib.util.spec_from_file_location("_patch_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "YAMA", None)


def write_new_file(ad, icerik):
    parent = os.path.dirname(ad)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(ad, "w", encoding="utf-8", newline="") as f:
        f.write(icerik.replace("\r\n", "\n"))  # yeni dosyalar LF ile


# ---------- Yama Uygulama ----------
def apply_patch(patch, applied):
    pid = patch.get("id")
    if not pid:
        return {"status": "error", "msg": "YAMA['id'] eksik"}

    if pid in applied:
        return {"status": "skipped", "when": applied[pid]}

    results = []
    target = patch.get("dosya")
    backup_path = None
    changed = False

    # --- Mevcut dosyada find & replace ---
    if target and patch.get("islemler"):
        if not os.path.exists(target):
            results.append(("fail", "file", f"Dosya yok: {target}"))
        else:
            with open(target, "r", encoding="utf-8", newline="") as f:
                original = f.read()

            nl = detect_newline(original)
            content = to_lf(original)

            for i, islem in enumerate(patch["islemler"], 1):
                bul = to_lf(islem.get("bul", ""))
                deg = to_lf(islem.get("degistir", ""))
                preview = bul[:60].replace("\n", " ")

                if bul and bul in content:
                    content = content.replace(bul, deg)
                    results.append(("ok", i, preview))
                    changed = True
                elif deg and deg in content:
                    results.append(("skip", i, preview))
                else:
                    results.append(("fail", i, preview))

            if changed:
                backup_path = backup_file(target)
                final = content.replace("\n", nl) if nl == "\r\n" else content
                with open(target, "w", encoding="utf-8", newline="") as f:
                    f.write(final)

    # --- Yeni dosya oluşturma ---
    for yeni in patch.get("yeni_dosyalar", []) or []:
        ad = yeni.get("ad")
        icerik = yeni.get("icerik", "")
        if not ad:
            continue
        if os.path.exists(ad):
            results.append(("skip", "new", ad))
        else:
            write_new_file(ad, icerik)
            results.append(("ok", "new", ad))

    applied[pid] = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_applied(applied)

    ok = sum(1 for r in results if r[0] == "ok")
    skip = sum(1 for r in results if r[0] == "skip")
    fail = sum(1 for r in results if r[0] == "fail")

    return {
        "status": "partial" if fail else "done",
        "results": results,
        "ok": ok, "skip": skip, "fail": fail,
        "backup": backup_path,
    }


# ---------- Ana Akış ----------
def main():
    line = "═" * 44
    print(f"{C.CYN}{line}{C.R}")
    print(f"{C.B}  MIGRATOR v1{C.R}")
    print(f"{C.CYN}{line}{C.R}\n")

    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"{C.RED}migrations/ klasörü bulunamadı.{C.R}")
        return

    files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR)
        if f.endswith(".py") and not f.startswith("_")
    )

    print(f"{C.GRY}{len(files)} yama bulundu.{C.R}\n")

    applied = load_applied()
    totals = {"applied": 0, "skipped": 0, "errors": 0, "partial": 0}

    for fname in files:
        path = os.path.join(MIGRATIONS_DIR, fname)
        try:
            patch = load_patch(path)
        except Exception as e:
            print(f"{C.RED}▸ {fname} — yüklenemedi: {e}{C.R}\n")
            totals["errors"] += 1
            continue

        if not patch:
            print(f"{C.RED}▸ {fname} — YAMA sözlüğü yok, atlandı{C.R}\n")
            totals["errors"] += 1
            continue

        pid = patch.get("id", "?")

        if pid in applied:
            print(f"{C.B}▸ {fname}{C.R}")
            print(f"  {C.YLW}• Uygulanmış ({applied[pid]}), atlandı{C.R}\n")
            totals["skipped"] += 1
            continue

        print(f"{C.B}▸ {fname}{C.R}")
        if patch.get("aciklama"):
            print(f"  {C.GRY}{patch['aciklama']}{C.R}")

        res = apply_patch(patch, applied)

        if res["status"] == "error":
            print(f"  {C.RED}✗ {res['msg']}{C.R}\n")
            totals["errors"] += 1
            continue

        for status, idx, preview in res["results"]:
            if status == "ok":
                print(f"  {C.GRN}✓ [{idx}] uygulandı{C.R}      → {preview}")
            elif status == "skip":
                print(f"  {C.YLW}• [{idx}] zaten vardı{C.R}     → {preview}")
            else:
                print(f"  {C.RED}✗ [{idx}] BULUNAMADI{C.R}      → {preview}")

        if res["fail"]:
            print(f"\n  {C.YLW}⚠ KISMİ — {res['ok']} uygulandı, "
                  f"{res['fail']} başarısız{C.R}")
            totals["partial"] += 1
        else:
            totals["applied"] += 1

        if res.get("backup"):
            print(f"  {C.GRY}Yedek: {res['backup']}{C.R}")
        print()

    print(f"{C.CYN}{line}{C.R}")
    print(f"  {C.B}Özet:{C.R} {totals['applied']} tam · "
          f"{totals['skipped']} atlandı · "
          f"{totals['partial'] + totals['errors']} sorun")
    print(f"{C.CYN}{line}{C.R}")

    temizle_migrations(applied)


def temizle_migrations(applied):
    """Uygulanmış .py yamalarını _backups/migrations_archive/ altına taşır.
    migrations/ klasöründe sadece _template.py ve başarısız yamalar kalır."""
    if not os.path.isdir(MIGRATIONS_DIR):
        return

    arsiv = os.path.join(BACKUPS_DIR, "migrations_archive")
    os.makedirs(arsiv, exist_ok=True)

    tasindi = []
    for fname in os.listdir(MIGRATIONS_DIR):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        path = os.path.join(MIGRATIONS_DIR, fname)
        try:
            patch = load_patch(path)
        except Exception:
            continue
        if not patch or patch.get("id") not in applied:
            continue
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        hedef = os.path.join(arsiv, f"{fname}.{ts}.bak")
        try:
            shutil.move(path, hedef)
            tasindi.append(fname)
        except Exception as e:
            print(f"{C.YLW}⚠ {fname} taşınamadı: {e}{C.R}")

    if tasindi:
        print(f"\n{C.GRY}🧹 {len(tasindi)} yama arşive taşındı → {arsiv}/{C.R}")


if __name__ == "__main__":
    main()