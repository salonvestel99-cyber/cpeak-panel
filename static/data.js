// Demo veriler — istediğin zaman buradan güncellersin.
// Gerçek bir backend'e geçince bu dosya silinir, veriler API'den gelir.

const VERI = {
  kullanicilar: [
    // ÖĞRENCİLER
    { tc: "33333333333", sifre: "ogrenci123", ad: "Ali Demir",    rol: "student", ogrenciId: 1 },
    { tc: "33333333334", sifre: "ogrenci123", ad: "Zeynep Kaya",  rol: "student", ogrenciId: 2 },
    { tc: "33333333335", sifre: "ogrenci123", ad: "Mehmet Şahin", rol: "student", ogrenciId: 3 },

    // VELİLER (her biri bir öğrenciye bağlı)
    { tc: "44444444444", sifre: "veli123", ad: "Hasan Demir", rol: "parent", ogrenciId: 1 },
    { tc: "44444444445", sifre: "veli123", ad: "Fatma Kaya",  rol: "parent", ogrenciId: 2 },

    // ÖĞRETMEN
    { tc: "22222222222", sifre: "ogretmen123", ad: "Ayşe Yılmaz", rol: "teacher" },

  ],

  ogrenciler: {
    1: { id: 1, ad: "Ali Demir",    sinif: "9-A",  numara: 101 },
    2: { id: 2, ad: "Zeynep Kaya",  sinif: "9-A",  numara: 102 },
    3: { id: 3, ad: "Mehmet Şahin", sinif: "10-B", numara: 201 },
  },

  dersler: ["Matematik", "Türkçe", "İngilizce", "Fen Bilimleri", "Tarih"],

  notlar: {
    1: {
      "Matematik":     [{ sinav: "Vize", puan: 85 }, { sinav: "Final", puan: 92 }, { sinav: "Proje", puan: 78 }],
      "Türkçe":        [{ sinav: "Vize", puan: 88 }, { sinav: "Final", puan: 90 }, { sinav: "Proje", puan: 85 }],
      "İngilizce":     [{ sinav: "Vize", puan: 95 }, { sinav: "Final", puan: 97 }, { sinav: "Proje", puan: 92 }],
      "Fen Bilimleri": [{ sinav: "Vize", puan: 80 }, { sinav: "Final", puan: 84 }, { sinav: "Proje", puan: 88 }],
      "Tarih":         [{ sinav: "Vize", puan: 75 }, { sinav: "Final", puan: 82 }, { sinav: "Proje", puan: 79 }],
    },
    2: {
      "Matematik":     [{ sinav: "Vize", puan: 72 }, { sinav: "Final", puan: 78 }, { sinav: "Proje", puan: 85 }],
      "Türkçe":        [{ sinav: "Vize", puan: 90 }, { sinav: "Final", puan: 88 }, { sinav: "Proje", puan: 93 }],
      "İngilizce":     [{ sinav: "Vize", puan: 88 }, { sinav: "Final", puan: 91 }, { sinav: "Proje", puan: 89 }],
      "Fen Bilimleri": [{ sinav: "Vize", puan: 79 }, { sinav: "Final", puan: 83 }, { sinav: "Proje", puan: 81 }],
      "Tarih":         [{ sinav: "Vize", puan: 82 }, { sinav: "Final", puan: 86 }, { sinav: "Proje", puan: 84 }],
    },
    3: {
      "Matematik":     [{ sinav: "Vize", puan: 68 }, { sinav: "Final", puan: 74 }, { sinav: "Proje", puan: 80 }],
      "Türkçe":        [{ sinav: "Vize", puan: 76 }, { sinav: "Final", puan: 82 }, { sinav: "Proje", puan: 78 }],
      "İngilizce":     [{ sinav: "Vize", puan: 84 }, { sinav: "Final", puan: 88 }, { sinav: "Proje", puan: 86 }],
      "Fen Bilimleri": [{ sinav: "Vize", puan: 71 }, { sinav: "Final", puan: 77 }, { sinav: "Proje", puan: 75 }],
      "Tarih":         [{ sinav: "Vize", puan: 80 }, { sinav: "Final", puan: 84 }, { sinav: "Proje", puan: 82 }],
    },
  },

  devamsizlik: {
    1: { toplam: 5, ozurlu: 2, ozursuz: 3 },
    2: { toplam: 2, ozurlu: 1, ozursuz: 1 },
    3: { toplam: 8, ozurlu: 3, ozursuz: 5 },
  },

  duyurular: [
    { baslik: "Veli Toplantısı",         icerik: "Bu cumartesi saat 10:00'da veli toplantısı yapılacaktır.", tarih: "20 Eylül 2025" },
    { baslik: "Kütüphane Çalışma Saatleri", icerik: "Kütüphane hafta içi 08:00–18:00 arası açıktır.",       tarih: "18 Eylül 2025" },
    { baslik: "Vize Sınav Takvimi",       icerik: "Vize sınavları 15 Ekim'de başlıyor. Takvimi panelden takip edin.", tarih: "15 Eylül 2025" },
  ],
};
