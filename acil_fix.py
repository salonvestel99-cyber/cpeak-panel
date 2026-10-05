#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
acil_fix.py — security.py'deki bozuk satırı düzelt.
Render deploy hatası: content_security_policy=None  # comment,
Doğrusu: content_security_policy=None,  # comment
"""

import re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
SEC = KOK / "security.py"
YED_DIR = KOK / "backups"


def main():
    if not SEC.exists():
        print("[HATA] security.py yok"); sys.exit(1)

    ic = SEC.read_text(encoding="utf-8")

    # Bozuk satırı bul: content_security_policy=None ... # ... , (virgül commentte)
    # Yenisi: content_security_policy=None,  # comment
    pat = re.compile(
        r'([ \t]*content_security_policy\s*=\s*None)[ \t]*'
        r'(#[^\n]*?)(?:,)?[ \t]*$',
        re.MULTILINE,
    )

    def fix(m):
        # Comment içindeki virgülü temizle
        comment = m.group(2).rstrip().rstrip(",")
        return f"{m.group(1)},  {comment}"

    yeni, n = pat.subn(fix, ic, count=1)

    if n == 0:
        # Zaten düzgün mü?
        if re.search(r'content_security_policy\s*=\s*None\s*,', ic):
            print("[ATLA] Satır zaten düzgün görünüyor.")
            return
        print("[HATA] Bozuk satır bulunamadı.")
        # Ne olduğunu göster
        for i, s in enumerate(ic.split("\n")):
            if "content_security_policy" in s:
                print(f"  {i+1}| {s}")
        sys.exit(1)

    # Yedek
    YED_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    yed = YED_DIR / f"security.py.broken.{stamp}.bak"
    shutil.copy2(SEC, yed)
    print(f"[YEDEK] backups/{yed.name}")

    SEC.write_text(yeni, encoding="utf-8")
    print(f"[OK] security.py düzeltildi")

    # Syntax kontrolü
    import ast
    try:
        ast.parse(yeni)
        print("[✓] Python syntax doğrulandı")
    except SyntaxError as e:
        print(f"[HATA] Syntax hâlâ bozuk: {e}")
        sys.exit(1)

    # Doğru satırı göster
    for i, s in enumerate(yeni.split("\n")):
        if "content_security_policy" in s:
            print(f"  → {i+1}: {s.strip()}")

    # Git commit + push
    print("\n[GIT] Commit + push...")
    try:
        subprocess.run(["git", "add", str(SEC.relative_to(KOK))],
                       cwd=str(KOK), check=True)
        r = subprocess.run(
            ["git", "commit", "-m",
             "fix(acil): security.py syntax hatası düzeltildi\n\n"
             "content_security_policy=None satırındaki virgül comment\n"
             "içinde kalmıştı, Render deploy başarısız oluyordu."],
            cwd=str(KOK), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        print(r.stdout.strip())
        if r.stderr.strip():
            print(r.stderr.strip())

        r2 = subprocess.run(["git", "push"], cwd=str(KOK),
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        print(r2.stdout.strip())
        if r2.stderr.strip():
            print(r2.stderr.strip())
        if r2.returncode == 0:
            print("[GIT] ✓ push tamam — Render otomatik deploy edecek")
    except subprocess.CalledProcessError as e:
        print(f"[GIT] hata: {e}")
        print("Manuel: git add security.py && git commit -m 'fix' && git push")


if __name__ == "__main__":
    main()