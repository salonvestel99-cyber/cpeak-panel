# Yama Sistemi (Migrator v1)

Küçük-orta değişiklikleri tekrar edilebilir şekilde uygulamak için.

## Kurulum
```bash
python migrator.py
```

## Yamaları Ekleme
1. `migrations/_template.py` dosyasını kopyala.
2. `migrations/00N_isim.py` olarak kaydet.
3. `YAMA` sözlüğünü düzenle.
4. `python migrator.py`

## Klasör Yapısı
- `migrator.py`     → Motor
- `migrations/`     → Yamalar
- `_applied.json`   → Uygulananlar
- `_backups/`       → Otomatik yedekler

## Geri Dönme
`_backups/` klasöründen ilgili `.bak` dosyasını hedef konuma kopyala.