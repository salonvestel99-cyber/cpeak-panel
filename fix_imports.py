import re, shutil, subprocess
from datetime import datetime

f = "app.py"
c = open(f, encoding="utf-8").read()
orig = c

# 1) Yedek al
bak = f + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(f, bak)
print(f"Yedek: {bak}")

# 2) from flask import ... satirini bul, Response ekle
m = re.search(r"^from flask import (.+)$", c, re.MULTILINE)
if m:
    names = [n.strip() for n in m.group(1).split(",")]
    if "Response" not in names:
        names.append("Response")
        yeni = "from flask import " + ", ".join(names)
        c = c[:m.start()] + yeni + c[m.end():]
        print(f"+ Response eklendi: {yeni}")
    else:
        print("Response zaten var")
else:
    c = "from flask import Response\n" + c
    print("+ from flask import Response (en basa)")

# 3) from datetime import datetime kontrolu
if "from datetime import datetime" not in c:
    c = re.sub(
        r"(from flask import [^\n]+)",
        r"\1\nfrom datetime import datetime",
        c, count=1
    )
    print("+ from datetime import datetime eklendi")
else:
    print("datetime zaten var")

# 4) Yaz
if c != orig:
    open(f, "w", encoding="utf-8").write(c)
    print(f"Yazildi: {f}")
else:
    print("Degisiklik yok")
    raise SystemExit(0)

# 5) Commit + push
subprocess.run(["git", "add", f])
subprocess.run(["git", "commit", "-m", "fix: Response ve datetime importlari eklendi"])
r = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
print("Push:", "OK" if r.returncode == 0 else r.stderr[:300])