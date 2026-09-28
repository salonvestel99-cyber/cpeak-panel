# Site Raporu

Tarih: 2026-09-28 05:27

# 1. Proje Yapisi

- Python dosyalari: **6**
  - `app.py`
  - `guncelle.py`
  - `kur.py`
  - `migrator.py`
  - `models.py`
  - `run.py`
- Template dosyalari: **17**
  - `templates\admin.html`
  - `templates\base.html`
  - `templates\ders_programi.html`
  - `templates\ders_programi_yonetim.html`
  - `templates\devamsizlik.html`
  - `templates\devamsizlik_giris.html`
  - `templates\kvkk.html`
  - `templates\login.html`
  - `templates\not_giris.html`
  - `templates\odev_detay.html`
  - `templates\odevler.html`
  - `templates\ogrenci_duzenle.html`
  - `templates\ogretmen_odev_ver.html`
  - `templates\parent.html`
  - `templates\sifre_degistir.html`
  - `templates\student.html`
  - `templates\teacher.html`
- CSS dosyalari: **12**
  - `static\admin.css` (3303 byte)
  - `static\footer.css` (13391 byte)
  - `static\hero.css` (13242 byte)
  - `static\legal.css` (7442 byte)
  - `static\login.css` (20705 byte)
  - `static\panel.css` (52666 byte)
  - `static\responsive.css` (20220 byte)
  - `static\student.css` (8394 byte)
  - `static\style.css` (9179 byte)
  - `static\teacher.css` (8326 byte)
  - `static\theme.css` (32344 byte)
  - `static\whatsapp.css` (8416 byte)
- JS dosyalari: **6**
  - `static\auth.js`
  - `static\dashboard.js`
  - `static\dashboard_v2.js`
  - `static\data.js`
  - `static\login-extras.js`
  - `static\theme.js`

# 2. CSS Degiskenleri (`:root` ve tema bloklari)

Toplam **37** CSS degiskeni bulundu:

| Degisken | Deger |
|---|---|
| `--amber` | `var(--copper)` |
| `--amber-2` | `var(--copper-2)` |
| `--bg` | `#fafaf9` |
| `--border` | `#e4e4e7` |
| `--border-2` | `#d4d4d8` |
| `--copper` | `#b45309` |
| `--copper-2` | `#92400e` |
| `--copper-bg` | `#fef3e2` |
| `--coral` | `var(--copper)` |
| `--coral-2` | `var(--copper-2)` |
| `--coral-3` | `#f5a173` |
| `--cream` | `var(--bg)` |
| `--cream-2` | `var(--surface-2)` |
| `--forest` | `var(--ink)` |
| `--forest-2` | `var(--ink)` |
| `--forest-3` | `var(--ink-2)` |
| `--forest-4` | `var(--ink-2)` |
| `--green` | `#059669` |
| `--ink` | `#18181b` |
| `--ink-2` | `#27272a` |
| `--line` | `var(--border)` |
| `--muted` | `#71717a` |
| `--muted-2` | `#a1a1aa` |
| `--navy` | `var(--ink)` |
| `--navy-2` | `var(--ink-2)` |
| `--paper` | `var(--surface)` |
| `--radius` | `10px` |
| `--radius-lg` | `14px` |
| `--red` | `#dc2626` |
| `--sand` | `var(--border)` |
| `--sand-2` | `var(--border-2)` |
| `--shadow-lg` | `0 12px 32px rgba(24,24,27,.08)` |
| `--shadow-md` | `0 4px 12px rgba(24,24,27,.06)` |
| `--shadow-sm` | `0 1px 2px rgba(24,24,27,.04)` |
| `--surface` | `#ffffff` |
| `--surface-2` | `#f4f4f5` |
| `--theme-transition` | `background-color .28s ease, color .28s ease, border-color .28s ease` |

**Tema mekanizmasi:** `[data-theme="..."]`, `.dark` class'i, `prefers-color-scheme` media query

# 3. Template'lerde Kullanilan Onemli Class'lar

Toplam **358** class bulundu. Onemli kaliplar:

**Tema / layout:**
- `.container`
- `.modal-icon-wrapper`
- `.theme-toggle`
- `.theme-toggle-float`

**Header / nav:**
- `.legal-header`
- `.page-header`
- `.sinav-chip`
- `.user-dropdown-menu`

**Hero:**
- `.cookie-banner`
- `.cookie-banner-inner`
- `.hero-brand`
- `.hero-brand-anim`
- `.hero-brand-mark`
- `.hero-brand-sub`
- `.hero-brand-text`
- `.hero-brand-title`
- `.hero-clock`
- `.hero-content`
- `.hero-eyebrow`
- `.hero-eyebrow-dash`
- `.hero-eyebrow-icon`
- `.hero-eyebrow-tag`
- `.hero-eyebrow-text`
- `.hero-lead`
- `.hero-list`
- `.hero-orb`
- `.hero-stat`
- `.hero-stats`
- `.login-hero`
- `.panel-hero`
- `.panel-hero-avatar`
- `.panel-hero-eyebrow`
- `.panel-hero-greet`
- `.panel-hero-sub`
- `.panel-hero-text`
- `.st-hero`
- `.st-hero-eyebrow`
- `.st-hero-sub`
- `.st-hero-text`
- `.st-hero-title`
- `.tp-hero`
- `.tp-hero-avatar`
- `.tp-hero-eyebrow`
- `.tp-hero-sub`
- `.tp-hero-text`
- `.tp-hero-title`

**Kart / panel:**
- `.add-card`
- `.add-card-chev`
- `.add-card-plus`
- `.admin-panel`
- `.admin-panels`
- `.card`
- `.card-head`
- `.check-box`
- `.ders-card`
- `.login-card`
- `.mini-card`
- `.mini-card-head`
- `.mini-card-warn`
- `.modal-card`
- `.odev-card`
- `.panel-hero`
- `.panel-hero-avatar`
- `.panel-hero-eyebrow`
- `.panel-hero-greet`
- `.panel-hero-sub`
- `.panel-hero-text`
- `.premium-modal-card`
- `.st-quick-card`
- `.stat-card`
- `.stat-card-alt`
- `.stat-card-deger`
- `.stat-card-etiket`
- `.stat-card-head`
- `.stat-card-ico`
- `.stat-card-link`
- `.tp-quick-card`

**Buton:**
- `.btn-cancel`
- `.btn-confirm`
- `.btn-danger`
- `.btn-ghost`
- `.btn-mini`
- `.btn-mini-danger`
- `.btn-primary`
- `.cookie-btn`
- `.cookie-btn-primary`
- `.cookie-btn-secondary`
- `.filter-button`
- `.qa-btn`

**Form:**
- `.admin-form`
- `.check-label`
- `.compact-form`
- `.form-actions`
- `.form-row`
- `.form-row-sub`
- `.hucre-form`
- `.hucre-sil-form`
- `.inline-form`
- `.input-eye`
- `.input-icon`
- `.input-wrap`
- `.mini-input`
- `.not-filter-form`
- `.not-form`
- `.not-form-actions`
- `.puan-input`
- `.search-input`
- `.st-quick-label`
- `.st-stat-label`
- `.talep-form`
- `.tp-quick-label`
- `.tp-stat-label`
- `.whatsapp-float__label`
- `.yoklama-form`

**Modal / dialog:**
- `.modal`
- `.modal-actions`
- `.modal-card`
- `.modal-close`
- `.modal-icon-warn`
- `.modal-icon-wrapper`
- `.premium-modal-card`
- `.premium-modal-overlay`

**Cerez / cookie:**
- `.cookie-actions`
- `.cookie-banner`
- `.cookie-banner-inner`
- `.cookie-btn`
- `.cookie-btn-primary`
- `.cookie-btn-secondary`
- `.cookie-icon`
- `.cookie-text`

**WhatsApp:**
- `.social-whatsapp`
- `.whatsapp-float`
- `.whatsapp-float__icon`
- `.whatsapp-float__label`

**Avatar:**
- `.panel-hero-avatar`
- `.topbar-avatar`
- `.tp-hero-avatar`

**Footer:**
- `.footer-contact`
- `.footer-copy`
- `.footer-inner`
- `.footer-sep`
- `.footer-social`
- `.legal-footer`
- `.login-footer-bar`


# 4. Tema Degistirici Mekanizmasi

- localStorage anahtari: `cpeak_admin_tab`
- `data-theme` attribute kullaniliyor
- classList.toggle: `is-visible`
- classList.toggle: `is-active`
- classList.toggle: `is-active`
- classList.toggle: `open`
- classList.toggle: `is-active`
- classList.toggle: `is-active`
- classList.toggle: `is-visible`
- `matchMedia('(prefers-color-scheme: dark)')` kullaniliyor

# 5. Cerez Banner

**Bulunan class:** `cookie-banner`

**HTML (kirpilmis):**
```html
<div id="cookieBanner" class="cookie-banner" hidden>
  <div class="cookie-banner-inner">
    <div class="cookie-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5"/>
        <path d="M8.5 8.5v.01"/><path d="M16 15.5v.01"/><path d="M12 12v.01"/>
        <path d="M11 17v.01"/><path d="M7 14v.01"/>
      </svg>
```

# 6. WhatsApp Butonu

**Bulundu. HTML (kirpilmis):**
```html
<a href="https://wa.me/905421808402" target="_blank" rel="noopener" class="social-icon social-whatsapp" aria-label="WhatsApp" title="WhatsApp">
        <svg viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" clip-rule="evenodd" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669
```
**Gectigi template'ler:** templates\base.html, templates\login.html

# 7. Template'lerdeki Jinja Kosullari (endpoint/path)

_Endpoint/path iceren Jinja kosulu bulunamadi._

# 8. Flask Route'lari (URL kurallari)

| Dosya | URL | Fonksiyon | Ek |
|---|---|---|---|
| `app.py` | `/kvkk` | `kvkk` | `` |
| `app.py` | `/` | `index` | `` |
| `app.py` | `/giris` | `login` | ` methods=["GET", "POST"]` |
| `app.py` | `/sifremi-unuttum` | `sifremi_unuttum` | ` methods=["POST"]` |
| `app.py` | `/cikis` | `logout` | `` |
| `app.py` | `/panel` | `dashboard` | `` |
| `app.py` | `/sifre-degistir` | `sifre_degistir` | ` methods=["GET", "POST"]` |
| `app.py` | `/ogrenci` | `student_panel` | `` |
| `app.py` | `/veli` | `parent_panel` | `` |
| `app.py` | `/ogretmen` | `teacher_panel` | `` |
| `app.py` | `/devamsizlik/<int:sid>` | `devamsizlik_detay` | `` |
| `app.py` | `/admin` | `admin_panel` | `` |
| `app.py` | `/admin/ogrenci-ekle` | `admin_add_student` | ` methods=["POST"]` |
| `app.py` | `/admin/ogrenci-duzenle/<int:sid>` | `admin_edit_student` | ` methods=["GET", "POST"]` |
| `app.py` | `/admin/sifre-sifirla/<int:uid>` | `admin_sifre_sifirla` | ` methods=["POST"]` |
| `app.py` | `/admin/ogretmen-ekle` | `admin_add_teacher` | ` methods=["POST"]` |
| `app.py` | `/admin/ders-ekle` | `admin_add_course` | ` methods=["POST"]` |
| `app.py` | `/admin/not-ekle` | `admin_add_grade` | ` methods=["POST"]` |
| `app.py` | `/admin/devamsizlik-ekle` | `admin_add_attendance` | ` methods=["POST"]` |
| `app.py` | `/admin/duyuru-ekle` | `admin_add_announcement` | ` methods=["POST"]` |
| `app.py` | `/admin/talep-coz/<int:tid>` | `admin_talep_coz` | ` methods=["POST"]` |
| `app.py` | `/admin/talep-sil/<int:tid>` | `admin_talep_sil` | ` methods=["POST"]` |
| `app.py` | `/admin/sil/<tip>/<int:oid>` | `admin_delete` | ` methods=["POST"]` |
| `app.py` | `/not-giris` | `not_giris` | ` methods=["GET"]` |
| `app.py` | `/not-ekle-toplu` | `not_ekle_toplu` | ` methods=["POST"]` |
| `app.py` | `/devamsizlik-giris` | `devamsizlik_giris` | ` methods=["GET"]` |
| `app.py` | `/devamsizlik-kaydet` | `devamsizlik_kaydet` | ` methods=["POST"]` |
| `app.py` | `/ders-programi` | `ders_programi` | `` |
| `app.py` | `/odevler` | `odevler` | `` |
| `app.py` | `/odev/<int:hid>` | `odev_detay` | `` |
| `app.py` | `/odev/<int:hid>/teslim` | `odev_teslim` | ` methods=["POST"]` |
| `app.py` | `/ogretmen/odev-ver` | `ogretmen_odev_ver` | ` methods=["GET", "POST"]` |
| `app.py` | `/ders-programi/duzenle` | `ders_programi_duzenle` | ` methods=["GET", "POST"]` |
| `app.py` | `/ders-programi/sil/<int:sid>` | `ders_programi_sil` | ` methods=["POST"]` |
| `app.py` | `/admin/ders-programi` | `admin_ders_programi` | `` |
| `kur.py` | `/` | `index` | `` |
| `kur.py` | `/giris` | `login` | ` methods=["GET", "POST"]` |
| `kur.py` | `/cikis` | `logout` | `` |
| `kur.py` | `/panel` | `dashboard` | `` |
| `kur.py` | `/ogrenci` | `student_panel` | `` |
| `kur.py` | `/veli` | `parent_panel` | `` |
| `kur.py` | `/ogretmen` | `teacher_panel` | `` |
| `kur.py` | `/admin` | `admin_panel` | `` |
| `kur.py` | `/admin/ogrenci-ekle` | `admin_add_student` | ` methods=["POST"]` |
| `kur.py` | `/admin/ogretmen-ekle` | `admin_add_teacher` | ` methods=["POST"]` |
| `kur.py` | `/admin/ders-ekle` | `admin_add_course` | ` methods=["POST"]` |
| `kur.py` | `/admin/not-ekle` | `admin_add_grade` | ` methods=["POST"]` |
| `kur.py` | `/admin/devamsizlik-ekle` | `admin_add_attendance` | ` methods=["POST"]` |
| `kur.py` | `/admin/duyuru-ekle` | `admin_add_announcement` | ` methods=["POST"]` |
| `kur.py` | `/admin/sil/<tip>/<int:oid>` | `admin_delete` | ` methods=["POST"]` |

# 9. CSS'te Sabit (Hard-coded) Renkler

En sik kullanilan 20 renk:

| Renk | Kullanim |
|---|---|
| `fff` | 55 |
| `131316` | 15 |
| `e8765a` | 13 |
| `a1a1aa` | 13 |
| `d97706` | 12 |
| `f4f4f5` | 12 |
| `b45309` | 10 |
| `dc2626` | 10 |
| `3f3f46` | 8 |
| `e4e4e7` | 7 |
| `f59e0b` | 7 |
| `ef4444` | 7 |
| `ffffff` | 7 |
| `d4d4d8` | 7 |
| `rgba(255,255,255,.08)` | 7 |
| `rgba(180,83,9,.10)` | 7 |
| `rgba(255,255,255,.10)` | 6 |
| `rgba(180,83,9,.12)` | 6 |
| `25d366` | 5 |
| `fef2f2` | 5 |