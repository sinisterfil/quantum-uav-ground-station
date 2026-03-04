# Quantum UAV Yer İstasyonu Arayüzü

PySide6 tabanlı İHA yer kontrol istasyonu arayüzü. Yarışma sırasında telemetri izleme, canlı harita, kamera akışı ve sistem konfigürasyonu sağlar.

## Gereksinimler

- Python 3.9+
- PySide6
- PySide6-WebEngine (harita için)
- folium (harita oluşturma)
- opencv-python (kamera akışı)
- numpy

## Kurulum

```bash
pip install PySide6 PySide6-WebEngine folium opencv-python numpy
```

## Çalıştırma

```bash
python3 arayuz3.py
```

## Sekmeler

| Sekme | Açıklama |
|-------|----------|
| **Ana Ekran** | Canlı harita (Folium), kamera akışı (OpenCV), durum paneli, komut butonları |
| **Detay** | Telemetri verileri, uçuş modu, kilitlenme durumu, batarya |
| **Debug** | Ham veri tablosu, sunucu logları, Redis monitör |
| **Ayarlar** | Bağlantı ayarları, HSS koordinat girişi, kalibrasyon ofsetleri |

## Üst Telemetri Çubuğu

Enlem · Boylam · İrtifa · Dikilme · Yönelme · Yatış · Hız · Batarya · Saat

## Notlar

- **Kamera:** Varsayılan olarak bilgisayar webcam'ini kullanır (`source=0`). RTSP stream için `VideoThread(source="rtsp://...")` şeklinde değiştirilebilir. Kamera bulunamazsa test pattern gösterir.
- **Harita:** OpenStreetMap katmanı üzerinde geofence, HSS bölgeleri, İHA ikonları görüntülenir. Koordinatlar şu an örnek veridir.

