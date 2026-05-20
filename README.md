# 🔍 Conan – Cyberoutcast OSINT Toolkit

Toolkit investigasi digital berbasis Python untuk Linux.  
Dibuat untuk kegiatan sosial oleh **Cyberoutcast Detective Organization**.

---

## 📦 Instalasi

```bash
# Clone atau download repo
git clone https://github.com/USERNAME/conan.git
cd conan

# Install dependensi
pip3 install -r requirements.txt --break-system-packages
```

---

## 🚀 Cara Pakai

### Menu interaktif
```bash
python3 conan.py
```

### Langsung via argumen
```bash
python3 conan.py --phone 6281234567890     # Phone OSINT
python3 conan.py --social username_target  # Social Media OSINT
python3 conan.py --wa 6281234567890        # WhatsApp Info
python3 conan.py --image foto_bukti.jpg    # Metadata Gambar
python3 conan.py --rekening 1234567890     # Cek Rekening
python3 conan.py --report                  # Buat Laporan
```

---

## 📋 Modul

| # | Modul | Fungsi |
|---|-------|--------|
| 1 | Phone OSINT | Info operator, wilayah, validasi nomor |
| 2 | Social Media OSINT | Lacak username di 16+ platform |
| 3 | WhatsApp Info | Cek status pendaftaran WA |
| 4 | Image Metadata | Ekstrak GPS & EXIF dari foto bukti |
| 5 | Rekening OSINT | Cek database penipuan cekrekening.id |
| 6 | Report Generator | Buat laporan forensik .txt & .json |

---

## 📁 Struktur

```
conan/
├── conan.py          ← Entry point utama
├── requirements.txt
├── README.md
├── modules/
│   ├── phone_osint.py
│   ├── social_osint.py
│   ├── whatsapp_info.py
│   ├── image_metadata.py
│   ├── rekening_osint.py
│   ├── report_gen.py
│   └── session.py    ← Manajemen sesi lintas modul
└── reports/          ← Output laporan tersimpan di sini
```

---

## 🔧 Pengembangan Lanjutan

Untuk menambah modul baru, kirim pesan berikut ke Claude:

```
#CyberoutcastToolkit
Repo: github.com/USERNAME/conan
Minta tambah modul: [nama modul yang diinginkan]
```

---

## ⚖️ Disclaimer

Tool ini hanya mengakses data yang tersedia secara **publik dan legal**.  
Digunakan untuk keperluan investigasi sosial dan diserahkan ke pihak berwenang.  
Penggunaan di luar itu adalah tanggung jawab pengguna sepenuhnya.

---

*Conan v1.0 – Cyberoutcast · Linux · Python 3.10+*
