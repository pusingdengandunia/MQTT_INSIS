# Proyek MQTT INSIS

Proyek ini mendemonstrasikan fitur-fitur MQTTv5 tingkat lanjut menggunakan Python (`paho-mqtt`) dan dilengkapi dengan dashboard pemantauan *real-time* berbasis React. Proyek ini dikembangkan untuk menyimulasikan dan memvisualisasikan data sensor, *event* sistem, dan *Remote Procedure Call* (RPC) menggunakan protokol MQTT.

## Fitur MQTTv5 yang Didemonstrasikan

Proyek ini mengimplementasikan fitur-fitur utama dari spesifikasi MQTTv5 berikut:
1. **QoS (Quality of Service) 1 & 2**: Memastikan pengiriman pesan untuk data penting seperti alarm.
2. **Topic Wildcards (`+` dan `#`)**: Pola *subscription* fleksibel untuk *data logging*.
3. **Topic Alias**: Mengoptimalkan *bandwidth* dengan mengganti string topik yang panjang dengan alias angka.
4. **User Properties**: Menyisipkan metadata kustom (misalnya, `severity`, `region`) pada pesan yang di-*publish*.
5. **Retain**: Menyimpan nilai terakhir yang valid (seperti suhu) di broker agar langsung diterima oleh *subscriber* baru.
6. **Message Expiry Interval**: Mengatur waktu kedaluwarsa (*time-to-live*) untuk pesan agar data yang sudah usang dibuang.
7. **Last Will and Testament (LWT)**: Memberikan notifikasi sistem ketika klien (seperti sistem alarm) terputus secara tidak terduga.
8. **Request-Response (RPC)**: Mengimplementasikan komunikasi dua arah via MQTT menggunakan properti `ResponseTopic` dan `CorrelationData`.
9. **Shared Subscriptions (`$share/group/topic`)**: Melakukan *load balancing* untuk pesan yang masuk ke beberapa *instance* pekerja (*worker*).
10. **Flow Control**: Mengelola batas pesan konkuren menggunakan properti `ReceiveMaximum` untuk mencegah *subscriber* menerima terlalu banyak pesan sekaligus.

## Struktur Proyek

- `pub.py`: Berisi beberapa skrip *Publisher* MQTT yang menyimulasikan berbagai skenario:
  - **Sensor Suhu**: Mem-*publish* data suhu (menggunakan Retain, Expiry, QoS 1).
  - **Sistem Alarm**: Mem-*publish* alarm kritis dan mengelola LWT (menggunakan User Properties, QoS 2, LWT).
  - **RPC Client**: Mengirimkan *request* dan menunggu *response* (menggunakan Topic Alias, Request-Response).
- `subs.py`: Berisi skrip *Subscriber* MQTT untuk menangani data yang masuk:
  - **Data Logger**: Mendengarkan berbagai topik menggunakan Wildcards dan Shared Subscriptions.
  - **RPC Server & Manager**: Menangani *request* RPC yang masuk, mengirimkan balasan, dan mengimplementasikan Flow Control.
- `mqtt-dashboard/`: Aplikasi web berbasis Vite + React yang memvisualisasikan data MQTT, termasuk grafik *gauge* untuk suhu dan log untuk *event* sistem.

## Prasyarat

- **Python 3.7+**
- **Node.js** (direkomendasikan v16+) dan **npm**
- Broker MQTT yang kompatibel dengan MQTTv5. Kode saat ini dikonfigurasi untuk menggunakan broker publik EMQX (`broker.emqx.io`).

## Instalasi & Persiapan

### 1. Lingkungan Python

Instal *library* Python yang dibutuhkan:
```bash
pip install paho-mqtt
```

### 2. Dashboard

Masuk ke direktori dashboard dan instal modul Node yang diperlukan:
```bash
cd mqtt-dashboard
npm install
```

## Menjalankan Aplikasi

Untuk melihat sistem berjalan secara penuh, Anda harus menjalankan setiap komponen di terminal yang terpisah.

### 1. Jalankan Dashboard
Pada terminal pertama, masuk ke direktori `mqtt-dashboard` dan jalankan *server* *development* Vite:
```bash
cd mqtt-dashboard
npm run dev
```
Buka *browser* Anda ke URL yang ditampilkan di terminal (biasanya `http://localhost:5173`) untuk melihat dashboard *real-time*.

### 2. Jalankan Subscriber
Pada terminal kedua, jalankan `subs.py` untuk mulai mendengarkan data yang masuk dan menangani permintaan RPC:
```bash
python subs.py
```

### 3. Jalankan Publisher
Pada terminal ketiga, jalankan `pub.py` untuk mulai mengirimkan simulasi data sensor, alarm, dan *request* RPC:
```bash
python pub.py
```
*Catatan: `pub.py` dirancang untuk menjalankan simulasinya lalu berhenti otomatis. Anda dapat menjalankannya kembali untuk mengirim *batch* data baru ke dashboard dan subscriber.*

## Referensi Topik

Sistem ini menggunakan struktur topik berikut (berada di bawah *namespace* `afrizan/insis/`):
- `afrizan/insis/sensor/suhu/ruang1`: Data sensor suhu *real-time*.
- `afrizan/insis/alarm/kebakaran`: Notifikasi alarm kritis.
- `afrizan/insis/status/lwt`: Notifikasi status *offline* (Last Will).
- `afrizan/insis/rpc/request`: Topik untuk menerima permintaan RPC.
- `afrizan/insis/rpc/response/client123`: Topik untuk balasan *server* RPC.
