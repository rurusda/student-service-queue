# Student Service Queue

**Student Service Queue** merupakan aplikasi berbasis web yang dikembangkan untuk mendukung pengelolaan antrean layanan mahasiswa. Proyek ini menggunakan arsitektur frontend dan backend yang dijalankan menggunakan Docker serta menerapkan otomatisasi proses **Continuous Integration dan Continuous Deployment (CI/CD)** menggunakan Jenkins.

## 1. Fitur dan Komponen

Proyek ini terdiri dari beberapa komponen utama:

- **Frontend:** Antarmuka aplikasi berbasis HTML, CSS, dan JavaScript.
- **Backend:** REST API menggunakan Python.
- **Database/Penyimpanan:** Menggunakan Docker Named Volume untuk menjaga persistensi data.
- **Web Server:** Nginx sebagai server frontend.
- **Containerization:** Docker dan Docker Compose.
- **CI/CD:** Jenkins untuk otomatisasi validasi, build, dan deployment aplikasi.

## 2. Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python | Pengembangan backend |
| HTML, CSS, JavaScript | Pengembangan frontend |
| Docker | Menjalankan aplikasi dalam container |
| Docker Compose | Mengelola beberapa container |
| Nginx | Web server frontend |
| Jenkins | Otomatisasi CI/CD |
| GitHub | Penyimpanan source code dan version control |

## 3. Struktur Direktori

```text
student-service-queue/
│
├── backend/
│   ├── app.py
│   └── Dockerfile
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── docker-compose.yml
├── Jenkinsfile
└── README.md
```

## 4. Persyaratan Sistem

Pastikan perangkat telah memiliki:

- Docker Desktop
- Docker Compose
- Git
- Jenkins (untuk menjalankan pipeline CI/CD)

## 5. Cara Menjalankan Aplikasi

### A. Clone Repository

```bash
git clone https://github.com/rurusda/student-service-queue.git
```

Masuk ke direktori proyek:

```bash
cd student-service-queue
```

### B. Menjalankan Aplikasi dengan Docker Compose

Jalankan perintah berikut:

```bash
docker compose up -d --build
```

Perintah tersebut digunakan untuk membangun image dan menjalankan container backend serta frontend.

### C. Memeriksa Container

```bash
docker compose ps
```

Pastikan container backend dan frontend berada dalam status `Up`.

### D. Mengakses Aplikasi

Setelah container berhasil dijalankan, aplikasi dapat diakses melalui:

- **Frontend:** http://localhost:8081
- **Backend Health Check:** http://localhost:5001/health

### E. Menghentikan Aplikasi

```bash
docker compose down
```

## 6. Konfigurasi Docker

Aplikasi dijalankan menggunakan dua service utama:

1. **Backend**
   - Container: `student-service-backend`
   - Port: `5001`
   - Penyimpanan data: `queue-db-data`

2. **Frontend**
   - Container: `student-service-frontend`
   - Image: `nginx:alpine`
   - Port: `8081`

Docker Named Volume `queue-db-data` digunakan untuk menjaga data agar tetap tersedia meskipun container dihentikan atau dibuat ulang.

## 7. Implementasi CI/CD dengan Jenkins

Proyek ini menerapkan pipeline CI/CD menggunakan Jenkins dengan agent berlabel `docker-agent`.

Pipeline terdiri dari beberapa tahapan:

1. **Checkout Source Code:** Mengambil source code terbaru dari repository GitHub.
2. **Code Validation:** Memeriksa sintaks Python dan validasi konfigurasi Docker Compose.
3. **Build and Deploy:** Membangun Docker image dan menjalankan aplikasi menggunakan Docker Compose.
4. **Health Check:** Memastikan backend API dan frontend dapat memberikan respons.

Pipeline dijalankan menggunakan file `Jenkinsfile` yang tersimpan di repository.

## 8. Hasil Pengujian

Berdasarkan pengujian deployment, diperoleh hasil sebagai berikut:

- Source code berhasil diambil dari GitHub.
- Validasi sintaks Python berhasil dilakukan.
- Konfigurasi Docker Compose berhasil divalidasi.
- Docker image backend berhasil dibangun.
- Container backend dan frontend berhasil dijalankan.
- Backend memberikan respons health check dengan status `active`.
- Frontend berhasil diakses melalui browser dengan HTTP Status Code `200 OK`.
- Jenkins Stage View menunjukkan seluruh tahapan pipeline berhasil dijalankan pada build yang sukses.

## 9. Author (Anggota Kelompok(E))

**Rusda Ulva_101012300162**
**Eirene Kezia_101012300168**
**Muhamad Malik Hasbiya_101012300387**

Repository: [student-service-queue](https://github.com/rurusda/student-service-queue)

## Webhook Testing
Pengujian GitHub Webhook berhasil dilakukan.
Perubahan ini digunakan untuk menguji otomatisasi CI/CD melalui Jenkins.