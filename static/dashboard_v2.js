// Panel v2 — öğrenci / veli / öğretmen rolleri için zengin render.
// Admin rolü kaldırıldı; öğretmen paneli yönetici işlevlerini de kapsar.

/* ---------- Yardımcılar ---------- */

function notOrtalamasi(sinavlar) {
  if (!sinavlar || !sinavlar.length) return 0;
  const toplam = sinavlar.reduce((t, s) => t + s.puan, 0);
  return Math.round((toplam / sinavlar.length) * 10) / 10;
}

function genelOrtalama(notlar) {
  const dersOrt = Object.values(notlar || {}).map(notOrtalamasi);
  if (!dersOrt.length) return 0;
  const t = dersOrt.reduce((a, b) => a + b, 0);
  return Math.round((t / dersOrt.length) * 10) / 10;
}

function harfNotu(puan) {
  if (puan >= 90) return "AA";
  if (puan >= 85) return "BA";
  if (puan >= 80) return "BB";
  if (puan >= 75) return "CB";
  if (puan >= 70) return "CC";
  if (puan >= 65) return "DC";
  if (puan >= 60) return "DD";
  if (puan >= 50) return "FD";
  return "FF";
}

function harfSinifi(puan) {
  if (puan >= 85) return "harf-a";
  if (puan >= 70) return "harf-b";
  if (puan >= 50) return "harf-c";
  return "harf-f";
}

function devamsizlikDurumu(toplam) {
  if (toplam <= 5)  return { sinif: "durum-iyi",    etiket: "İyi" };
  if (toplam <= 10) return { sinif: "durum-dikkat", etiket: "Dikkat" };
  if (toplam <= 15) return { sinif: "durum-uyari",  etiket: "Uyarı" };
  return { sinif: "durum-kritik", etiket: "Kritik" };
}

/* ---------- HTML parçaları ---------- */

function heroHTML(k, alt) {
  const bas = k.ad.split(" ")[0];
  const harf = k.ad.trim().charAt(0).toUpperCase();
  return `
    <div class="panel-hero">
      <div class="panel-hero-text">
        <div class="panel-hero-greet">Merhaba, ${bas} 👋</div>
        <div class="panel-hero-sub">${alt}</div>
      </div>
      <div class="panel-hero-avatar">${harf}</div>
    </div>`;
}

function statKartHTML(ikon, etiket, deger, alt) {
  return `
    <div class="stat-card">
      <div class="stat-card-head">
        <span class="stat-card-ico">${ikon}</span>
        <span class="stat-card-etiket">${etiket}</span>
      </div>
      <div class="stat-card-deger">${deger}</div>
      <div class="stat-card-alt">${alt}</div>
    </div>`;
}

function devamsizlikKartHTML(dev) {
  const durum = devamsizlikDurumu(dev.toplam);
  const oran = Math.min(100, (dev.toplam / 20) * 100);
  return `
    <div class="stat-card devamsizlik ${durum.sinif}">
      <div class="stat-card-head">
        <span class="stat-card-ico">📅</span>
        <span class="stat-card-etiket">Devamsızlık</span>
      </div>
      <div class="stat-card-deger">${dev.toplam} <small>gün</small></div>
      <div class="progress"><div class="progress-bar" style="width:${oran}%"></div></div>
      <div class="stat-card-alt">
        <span><span class="dot ozurlu"></span>Özürlü: ${dev.ozurlu}</span>
        <span><span class="dot ozursuz"></span>Özürsüz: ${dev.ozursuz}</span>
      </div>
    </div>`;
}

function ortalamaKartHTML(notlar) {
  const ort = genelOrtalama(notlar);
  const harf = harfNotu(ort);
  const hSinif = harfSinifi(ort);
  return `
    <div class="stat-card">
      <div class="stat-card-head">
        <span class="stat-card-ico">📊</span>
        <span class="stat-card-etiket">Ortalama</span>
      </div>
      <div class="stat-card-deger">${ort} <small class="harf ${hSinif}">${harf}</small></div>
      <div class="stat-card-alt">${Object.keys(notlar || {}).length} ders</div>
    </div>`;
}

function dersKartHTML(ders, sinavlar) {
  const ort = notOrtalamasi(sinavlar);
  const harf = harfNotu(ort);
  const hSinif = harfSinifi(ort);
  const bar = Math.min(100, ort);
  const chips = sinavlar
    .map(s => `<span class="sinav-chip"><em>${s.sinav}</em>${s.puan}</span>`)
    .join("");
  return `
    <div class="ders-card">
      <div class="ders-head">
        <span class="ders-ad">${ders}</span>
        <span class="ders-harf ${hSinif}">${harf} · ${ort}</span>
      </div>
      <div class="ders-chips">${chips}</div>
      <div class="ders-bar"><div class="ders-bar-fill" style="width:${bar}%"></div></div>
    </div>`;
}

function notlarHTML(notlar) {
  if (!notlar || !Object.keys(notlar).length) {
    return '<p class="muted">Henüz not kaydı yok.</p>';
  }
  return `<div class="ders-grid">${
    Object.entries(notlar).map(([d, s]) => dersKartHTML(d, s)).join("")
  }</div>`;
}

function duyurularHTML() {
  if (!VERI.duyurular || !VERI.duyurular.length) {
    return '<p class="muted">Duyuru yok.</p>';
  }
  return `<div class="timeline">${
    VERI.duyurular.map(d => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-body">
          <div class="timeline-head">
            <strong>${d.baslik}</strong>
            <span class="timeline-tarih">${d.tarih}</span>
          </div>
          <p>${d.icerik}</p>
        </div>
      </div>`).join("")
  }</div>`;
}

/* ---------- Paneller ---------- */

function ogrenciPaneli(ogrenciId, k) {
  const ogr = VERI.ogrenciler[ogrenciId];
  const dev = VERI.devamsizlik[ogrenciId] || { toplam: 0, ozurlu: 0, ozursuz: 0 };
  const notlar = VERI.notlar[ogrenciId] || {};

  return `
    ${heroHTML(k, `${ogr.sinif} · ${ogr.numara} numaralı öğrenci`)}

    <div class="stat-grid">
      ${devamsizlikKartHTML(dev)}
      ${ortalamaKartHTML(notlar)}
      ${statKartHTML("📚", "Ders Sayısı", Object.keys(notlar).length, "Bu dönem")}
      ${statKartHTML("📢", "Duyuru", VERI.duyurular.length, "Güncel")}
    </div>

    <div class="card">
      <div class="card-head">
        <h3><span class="ico">📚</span> Notlarım</h3>
        <span class="muted small">Sınav bazlı puanlar</span>
      </div>
      ${notlarHTML(notlar)}
    </div>

    <div class="card">
      <div class="card-head">
        <h3><span class="ico">📢</span> Duyurular</h3>
      </div>
      ${duyurularHTML()}
    </div>`;
}

function veliPaneli(ogrenciId, k) {
  const ogr = VERI.ogrenciler[ogrenciId];
  const dev = VERI.devamsizlik[ogrenciId] || { toplam: 0, ozurlu: 0, ozursuz: 0 };
  const notlar = VERI.notlar[ogrenciId] || {};

  return `
    ${heroHTML(k, `Öğrenciniz: ${ogr.ad} · ${ogr.sinif} / ${ogr.numara}`)}

    <div class="stat-grid">
      ${devamsizlikKartHTML(dev)}
      ${ortalamaKartHTML(notlar)}
      ${statKartHTML("👤", "Öğrenci", ogr.ad.split(" ")[0], ogr.sinif)}
      ${statKartHTML("📢", "Duyuru", VERI.duyurular.length, "Güncel")}
    </div>

    <div class="card">
      <div class="card-head">
        <h3><span class="ico">📚</span> Notlar</h3>
        <span class="muted small">Görüntüleme modu</span>
      </div>
      ${notlarHTML(notlar)}
    </div>

    <div class="card">
      <div class="card-head">
        <h3><span class="ico">📢</span> Duyurular</h3>
      </div>
      ${duyurularHTML()}
    </div>`;
}

function ogretmenPaneli(k) {
  const ogrenciListesi = Object.values(VERI.ogrenciler);
  const siniflar = [...new Set(ogrenciListesi.map(o => o.sinif))].sort();

  const tumNotlar = Object.values(VERI.notlar);
  const tumOrt = tumNotlar.length
    ? Math.round((tumNotlar.reduce((t, n) => t + genelOrtalama(n), 0) / tumNotlar.length) * 10) / 10
    : 0;

  const satirlar = ogrenciListesi.map(o => {
    const dev = VERI.devamsizlik[o.id] || { toplam: 0 };
    const ort = genelOrtalama(VERI.notlar[o.id] || {});
    const harf = harfNotu(ort);
    const hSinif = harfSinifi(ort);
    const dSinif = devamsizlikDurumu(dev.toplam).sinif;
    return `
      <tr>
        <td><strong>${o.ad}</strong></td>
        <td><span class="chip">${o.sinif}</span></td>
        <td>${o.numara}</td>
        <td><span class="harf ${hSinif}">${harf}</span> ${ort}</td>
        <td><span class="durum-badge ${dSinif}">${dev.toplam} gün</span></td>
      </tr>`;
  }).join("");

  return `
    ${heroHTML(k, "Öğretmen Paneli · Tüm sınıflar ve öğrenciler")}

    <div class="stat-grid">
      ${statKartHTML("👥", "Öğrenci", ogrenciListesi.length, "Toplam kayıtlı")}
      ${statKartHTML("📘", "Ders", VERI.dersler.length, "Müfredatta")}
      ${statKartHTML("🏫", "Sınıf", siniflar.length, "Aktif")}
      ${statKartHTML("📊", "Genel Ort.", tumOrt, "Tüm öğrenciler")}
    </div>

    <div class="card">
      <div class="card-head">
        <h3><span class="ico">📘</span> Verdiğim Dersler</h3>
      </div>
      <div class="chip-list">
        ${VERI.dersler.map(d => `<span class="chip chip-buyuk">${d}</span>`).join("")}
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h3><span class="ico">👥</span> Öğrenci Listesi</h3>
        <span class="muted small">${ogrenciListesi.length} öğrenci</span>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Ad Soyad</th><th>Sınıf</th><th>No</th>
              <th>Ortalama</th><th>Devamsızlık</th>
            </tr>
          </thead>
          <tbody>${satirlar}</tbody>
        </table>
      </div>
    </div>`;
}

/* ---------- Ana akış ---------- */

document.addEventListener("DOMContentLoaded", () => {
  const icerik = document.getElementById("panelIcerik");
  if (!icerik) return;

  const k = korumaliSayfa();
  if (!k) return;

  document.getElementById("kullaniciAdi").textContent = k.ad;
  document.getElementById("cikisBtn").addEventListener("click", cikisYap);

  // Başlık artık hero içinde; eski .page-head'i gizle
  const bh = document.querySelector(".page-head");
  if (bh) bh.style.display = "none";

  if (k.rol === "student") {
    icerik.innerHTML = ogrenciPaneli(k.ogrenciId, k);
  } else if (k.rol === "parent") {
    icerik.innerHTML = veliPaneli(k.ogrenciId, k);
  } else if (k.rol === "teacher") {
    icerik.innerHTML = ogretmenPaneli(k);
  } else {
    cikisYap();
  }
});
