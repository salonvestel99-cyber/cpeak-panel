// Panel sayfasını role göre render eder.

function ortalamaHesapla(notlar) {
  const ortalamalar = Object.values(notlar).map(sinavlar => {
    const toplam = sinavlar.reduce((t, s) => t + s.puan, 0);
    return toplam / sinavlar.length;
  });
  if (!ortalamalar.length) return 0;
  const genel = ortalamalar.reduce((t, o) => t + o, 0) / ortalamalar.length;
  return Math.round(genel * 100) / 100;
}

function notlarHTML(notlar) {
  if (!notlar || !Object.keys(notlar).length) {
    return '<p class="muted">Henüz not kaydı yok.</p>';
  }
  const satirlar = Object.entries(notlar).map(([ders, sinavlar]) => {
    const etiketler = sinavlar
      .map(s => `<span class="badge">${s.sinav}: ${s.puan}</span>`)
      .join("");
    return `<tr><td><strong>${ders}</strong></td><td>${etiketler}</td></tr>`;
  }).join("");
  return `
    <table class="table">
      <thead><tr><th>Ders</th><th>Sınavlar</th></tr></thead>
      <tbody>${satirlar}</tbody>
    </table>`;
}

function duyurularHTML() {
  const d = VERI.duyurular.map(x => `
    <div class="duyuru">
      <strong>${x.baslik}</strong>
      <span class="muted small"> · ${x.tarih}</span>
      <p>${x.icerik}</p>
    </div>`).join("");
  return d || '<p class="muted">Duyuru yok.</p>';
}

function ogrenciOzetKartlari(ogrenciId) {
  const dev = VERI.devamsizlik[ogrenciId] || { toplam: 0, ozurlu: 0, ozursuz: 0 };
  const ort = ortalamaHesapla(VERI.notlar[ogrenciId] || {});
  return `
    <div class="grid grid-2">
      <div class="card devamsizlik">
        <h3><span class="ico">📅</span> Devamsızlık</h3>
        <div class="stat">${dev.toplam} gün</div>
        <p class="muted">Özürlü: ${dev.ozurlu} · Özürsüz: ${dev.ozursuz}</p>
      </div>
      <div class="card ortalama">
        <h3><span class="ico">📊</span> Ortalama</h3>
        <div class="stat">${ort}</div>
        <p class="muted">Tüm derslerin ortalaması</p>
      </div>
    </div>`;
}

function ogrenciPaneli(ogrenciId) {
  const ogr = VERI.ogrenciler[ogrenciId];
  const notlar = VERI.notlar[ogrenciId];
  return `
    ${ogrenciOzetKartlari(ogrenciId)}
    <div class="card">
      <h3><span class="ico">📚</span> Notlar</h3>
      ${notlarHTML(notlar)}
    </div>
    <div class="card">
      <h3><span class="ico">📢</span> Duyurular</h3>
      ${duyurularHTML()}
    </div>`;
}

function veliPaneli(ogrenciId) {
  const ogr = VERI.ogrenciler[ogrenciId];
  return `
    <div class="alert alert-info">
      <strong>${ogr.ad}</strong> adlı öğrencinin bilgilerini görüntülüyorsunuz.
    </div>
    ${ogrenciOzetKartlari(ogrenciId)}
    <div class="card">
      <h3><span class="ico">📚</span> Notlar (görüntüleme)</h3>
      ${notlarHTML(VERI.notlar[ogrenciId])}
    </div>
    <div class="card">
      <h3><span class="ico">📢</span> Duyurular</h3>
      ${duyurularHTML()}
    </div>`;
}

function ogretmenPaneli() {
  const ogrenciSatirlari = Object.values(VERI.ogrenciler).map(o =>
    `<tr><td>${o.ad}</td><td>${o.sinif}</td><td>${o.numara}</td></tr>`
  ).join("");
  const dersler = VERI.dersler.map(d => `<li>${d}</li>`).join("");
  return `
    <div class="card">
      <h3><span class="ico">📘</span> Verdiğim Dersler</h3>
      <ul class="liste">${dersler}</ul>
    </div>
    <div class="card">
      <h3><span class="ico">👥</span> Öğrenciler</h3>
      <table class="table">
        <thead><tr><th>Ad Soyad</th><th>Sınıf</th><th>No</th></tr></thead>
        <tbody>${ogrenciSatirlari}</tbody>
      </table>
    </div>
    <div class="card">
      <p class="muted">Not girişi ve devamsızlık işleme özellikleri sonraki sürümde eklenecek.</p>
    </div>`;
}

function adminPaneli() {
  const sayi = {
    ogrenci: Object.keys(VERI.ogrenciler).length,
    ogretmen: VERI.kullanicilar.filter(u => u.rol === "teacher").length,
    veli: VERI.kullanicilar.filter(u => u.rol === "parent").length,
    ders: VERI.dersler.length,
  };
  return `
    <div class="grid grid-4">
      <div class="card"><h3>Öğrenci</h3><div class="stat">${sayi.ogrenci}</div></div>
      <div class="card"><h3>Öğretmen</h3><div class="stat">${sayi.ogretmen}</div></div>
      <div class="card"><h3>Veli</h3><div class="stat">${sayi.veli}</div></div>
      <div class="card"><h3>Ders</h3><div class="stat">${sayi.ders}</div></div>
    </div>`;
}

// ---- Ana akış ----
document.addEventListener("DOMContentLoaded", () => {
  const icerik = document.getElementById("panelIcerik");
  if (!icerik) return;

  const k = korumaliSayfa();
  if (!k) return;

  document.getElementById("kullaniciAdi").textContent = k.ad;
  document.getElementById("cikisBtn").addEventListener("click", cikisYap);

  const baslik = document.getElementById("panelBaslik");
  const alt = document.getElementById("panelAlt");

  if (k.rol === "student") {
    const ogr = VERI.ogrenciler[k.ogrenciId];
    baslik.textContent = `Merhaba, ${k.ad} 👋`;
    alt.textContent = `${ogr.sinif} · ${ogr.numara} numaralı öğrenci`;
    icerik.innerHTML = ogrenciPaneli(k.ogrenciId);
  } else if (k.rol === "parent") {
    baslik.textContent = `Hoş geldiniz, ${k.ad}`;
    alt.textContent = "Öğrencinizin güncel durumu";
    icerik.innerHTML = veliPaneli(k.ogrenciId);
  } else if (k.rol === "teacher") {
    baslik.textContent = `Merhaba, ${k.ad} 👋`;
    alt.textContent = "Öğretmen Paneli";
    icerik.innerHTML = ogretmenPaneli();
  } else if (k.rol === "admin") {
    baslik.textContent = "Yönetici Paneli";
    alt.textContent = "Sistem genel bakış";
    icerik.innerHTML = adminPaneli();
  }
});
