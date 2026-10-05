# buton_detay.py
from pathlib import Path

LOGIN = Path("templates/login.html")
satirlar = LOGIN.read_text(encoding="utf-8").split("\n")

print("=" * 70)
print("login.html — satır 1-90 (back-home bloğu)")
print("=" * 70)
for i in range(0, min(90, len(satirlar))):
    print(f"{i:4d}| {satirlar[i]}")

print("\n" + "=" * 70)
print("login.html — satır 460-500 (ml11-back CSS)")
print("=" * 70)
for i in range(460, min(500, len(satirlar))):
    print(f"{i:4d}| {satirlar[i]}")

print("\n" + "=" * 70)
print("login.html — satır 660-700 (ml11-back JS)")
print("=" * 70)
for i in range(660, min(700, len(satirlar))):
    print(f"{i:4d}| {satirlar[i]}")