# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arayuz_serbestg.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QThread, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox,
    QFrame, QGroupBox, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpinBox, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextBrowser, QWidget)
from PySide6.QtWebEngineWidgets import QWebEngineView
import folium, io, os, cv2

# macOS kamera izin sorununu önle
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"


class VideoThread(QThread):
    """OpenCV kamera/RTSP akışını ayrı thread'de okur, frame sinyali yayar."""
    frame_ready = Signal(QImage)

    def __init__(self, source=0, parent=None):
        super().__init__(parent)
        self.source = source      # 0 = webcam, "rtsp://..." = RTSP
        self._running = True
        self.bbox = None           # (x, y, w, h) — kilitlenme kutusu

    def run(self):
        import numpy as np
        cap = cv2.VideoCapture(self.source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Kamera açılamazsa test pattern üret
        if not cap.isOpened():
            self._send_test_pattern(np)
            return

        while self._running:
            ret, frame = cap.read()
            if not ret:
                self.msleep(30)
                continue

            # Bounding box overlay (kırmızı kilitlenme kutusu)
            if self.bbox:
                bx, by, bw, bh = self.bbox
                cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
                cv2.putText(frame, "HEDEF", (bx, by - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # BGR → RGB → QImage
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.frame_ready.emit(qimg.copy())
        cap.release()

    def _send_test_pattern(self, np):
        """Kamera yokken renk çubuklu test pattern üret"""
        import time
        w, h = 640, 480
        colors = [
            (255, 255, 255), (255, 255, 0), (0, 255, 255), (0, 255, 0),
            (255, 0, 255), (255, 0, 0), (0, 0, 255), (0, 0, 0),
        ]
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        bar_w = w // len(colors)
        for i, c in enumerate(colors):
            frame[:, i * bar_w:(i + 1) * bar_w] = c

        frame_count = 0
        while self._running:
            display = frame.copy()
            # Üst bilgi şeridi
            cv2.rectangle(display, (0, 0), (w, 36), (0, 0, 0), -1)
            cv2.putText(display, "KAMERA BULUNAMADI - TEST PATTERN",
                        (10, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            cv2.putText(display, f"Frame: {frame_count}  |  Kaynak: {self.source}",
                        (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

            # Hareket eden çizgi (canlılık göstergesi)
            y_line = 40 + (frame_count * 3) % (h - 44)
            cv2.line(display, (0, y_line), (w, y_line), (0, 255, 0), 1)

            # Bounding box overlay test
            if self.bbox:
                bx, by, bw, bh = self.bbox
                cv2.rectangle(display, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
                cv2.putText(display, "HEDEF", (bx, by - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            qimg = QImage(display.data, w, h, 3 * w, QImage.Format.Format_RGB888)
            self.frame_ready.emit(qimg.copy())
            frame_count += 1
            time.sleep(1 / 30)  # ~30 FPS

    def stop(self):
        self._running = False
        self.wait()

class Ui_QuanrumUAVArayz(object):
    def setupUi(self, QuanrumUAVArayz):
        if not QuanrumUAVArayz.objectName():
            QuanrumUAVArayz.setObjectName(u"QuanrumUAVArayz")
        QuanrumUAVArayz.resize(1025, 628)
        self.centralwidget = QWidget(QuanrumUAVArayz)
        self.centralwidget.setObjectName(u"centralwidget")

        # === TAB WIDGET ===
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 0, 1025, 628))
        self.tabWidget.setStyleSheet(
            "QTabWidget::pane { border: none; background-color: #2b2b2b; }\n"
            "QTabBar::tab { background-color: #3a3a3a; color: white; padding: 8px 20px; "
            "margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }\n"
            "QTabBar::tab:selected { background-color: #555555; font-weight: bold; }\n"
            "QTabBar::tab:hover { background-color: #4a4a4a; }\n")

        # --- Tab 1: Ana Ekran (Dashboard) ---
        self.tab_dashboard = QWidget()
        self.tab_dashboard.setObjectName(u"tab_dashboard")
        self.tab_dashboard.setStyleSheet("background-color: #2b2b2b;")
        self._setupDashboard()
        self.tabWidget.addTab(self.tab_dashboard, u"Ana Ekran")

        # --- Tab 2: Debug / Mühendislik ---
        self.tab_debug = QWidget()
        self.tab_debug.setObjectName(u"tab_debug")
        self.tab_debug.setStyleSheet("background-color: #2b2b2b;")
        self._setupDebug()
        self.tabWidget.addTab(self.tab_debug, u"Debug")

        # --- Tab 3: Ayarlar / Konfigürasyon ---
        self.tab_settings = QWidget()
        self.tab_settings.setObjectName(u"tab_settings")
        self.tab_settings.setStyleSheet("background-color: #2b2b2b;")
        self._setupSettings()
        self.tabWidget.addTab(self.tab_settings, u"Ayarlar")

        # (Detay sekmesi kaldırıldı)

        QuanrumUAVArayz.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(QuanrumUAVArayz)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1025, 19))
        QuanrumUAVArayz.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(QuanrumUAVArayz)
        self.statusbar.setObjectName(u"statusbar")
        QuanrumUAVArayz.setStatusBar(self.statusbar)

        self.retranslateUi(QuanrumUAVArayz)

        QMetaObject.connectSlotsByName(QuanrumUAVArayz)
    # setupUi

    def _setupSettings(self):
        """Ayarlar / Konfigürasyon Sekmesi"""
        dark = "#3a3a3a"
        panel_ss = f"background-color: {dark}; border: 1px solid #555; border-radius: 4px;"
        hdr_ss = "color: #ff8800; font-size: 12px; font-weight: bold; background: transparent;"
        lbl_ss = "color: #cccccc; font-size: 11px; background: transparent;"
        input_ss = (
            "QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { "
            "background-color: #1a1a1a; color: #00ff00; border: 1px solid #555; "
            "border-radius: 3px; padding: 3px 6px; "
            "font-family: 'Courier New', monospace; font-size: 11px; }\n"
            "QComboBox::drop-down { border: none; }\n"
            "QComboBox QAbstractItemView { background-color: #1a1a1a; color: #00ff00; "
            "selection-background-color: #333; }")
        btn_ss = (
            "QPushButton { background-color: #444; color: white; "
            "border: 1px solid #666; border-radius: 4px; padding: 5px 14px; font-size: 11px; }\n"
            "QPushButton:hover { background-color: #555; }\n"
            "QPushButton:pressed { background-color: #333; }")
        save_btn_ss = (
            "QPushButton { background-color: #006633; color: white; "
            "border: 1px solid #009944; border-radius: 4px; padding: 5px 14px; "
            "font-size: 11px; font-weight: bold; }\n"
            "QPushButton:hover { background-color: #008844; }\n"
            "QPushButton:pressed { background-color: #004422; }")

        # Başlık
        self.cfg_title = QLabel(self.tab_settings)
        self.cfg_title.setGeometry(QRect(10, 4, 400, 20))
        self.cfg_title.setText("AYARLAR / KONFİGÜRASYON")
        self.cfg_title.setStyleSheet("color: #ff8800; font-size: 13px; font-weight: bold; background: transparent;")

        # ── 1) BAĞLANTI AYARLARI ─────────────────────────────
        self.cfg_conn_frame = QFrame(self.tab_settings)
        self.cfg_conn_frame.setGeometry(QRect(3, 28, 335, 230))
        self.cfg_conn_frame.setStyleSheet(panel_ss)

        lbl_conn = QLabel(self.cfg_conn_frame)
        lbl_conn.setGeometry(QRect(8, 4, 200, 18))
        lbl_conn.setText("BAĞLANTI AYARLARI")
        lbl_conn.setStyleSheet(hdr_ss)

        # Serial Port
        lbl_serial = QLabel(self.cfg_conn_frame)
        lbl_serial.setGeometry(QRect(10, 30, 120, 16))
        lbl_serial.setText("Serial Port:")
        lbl_serial.setStyleSheet(lbl_ss)

        self.cfg_serial_combo = QComboBox(self.cfg_conn_frame)
        self.cfg_serial_combo.setGeometry(QRect(10, 48, 200, 26))
        self.cfg_serial_combo.setStyleSheet(input_ss)
        self.cfg_serial_combo.addItems(["/dev/ttyUSB0", "/dev/ttyACM0", "COM3", "COM4"])
        self.cfg_serial_combo.setEditable(True)

        self.cfg_serial_refresh = QPushButton(self.cfg_conn_frame)
        self.cfg_serial_refresh.setGeometry(QRect(215, 48, 60, 26))
        self.cfg_serial_refresh.setText("Tara")
        self.cfg_serial_refresh.setStyleSheet(btn_ss)

        self.cfg_baud_combo = QComboBox(self.cfg_conn_frame)
        self.cfg_baud_combo.setGeometry(QRect(280, 48, 45, 26))
        self.cfg_baud_combo.setStyleSheet(input_ss + "\nQComboBox { font-size: 9px; }")
        self.cfg_baud_combo.addItems(["57600", "115200", "921600"])
        self.cfg_baud_combo.setCurrentIndex(1)

        # Sunucu IP / Port
        lbl_server = QLabel(self.cfg_conn_frame)
        lbl_server.setGeometry(QRect(10, 82, 120, 16))
        lbl_server.setText("Sunucu IP:")
        lbl_server.setStyleSheet(lbl_ss)

        self.cfg_server_ip = QLineEdit(self.cfg_conn_frame)
        self.cfg_server_ip.setGeometry(QRect(10, 100, 200, 26))
        self.cfg_server_ip.setStyleSheet(input_ss)
        self.cfg_server_ip.setPlaceholderText("192.168.1.100")

        lbl_port = QLabel(self.cfg_conn_frame)
        lbl_port.setGeometry(QRect(220, 82, 60, 16))
        lbl_port.setText("Port:")
        lbl_port.setStyleSheet(lbl_ss)

        self.cfg_server_port = QSpinBox(self.cfg_conn_frame)
        self.cfg_server_port.setGeometry(QRect(220, 100, 100, 26))
        self.cfg_server_port.setStyleSheet(input_ss)
        self.cfg_server_port.setRange(1, 65535)
        self.cfg_server_port.setValue(8000)

        # Takım ID / Şifre
        lbl_team = QLabel(self.cfg_conn_frame)
        lbl_team.setGeometry(QRect(10, 134, 120, 16))
        lbl_team.setText("Takım ID:")
        lbl_team.setStyleSheet(lbl_ss)

        self.cfg_team_id = QLineEdit(self.cfg_conn_frame)
        self.cfg_team_id.setGeometry(QRect(10, 152, 140, 26))
        self.cfg_team_id.setStyleSheet(input_ss)
        self.cfg_team_id.setPlaceholderText("T001")

        lbl_pass = QLabel(self.cfg_conn_frame)
        lbl_pass.setGeometry(QRect(160, 134, 120, 16))
        lbl_pass.setText("Şifre:")
        lbl_pass.setStyleSheet(lbl_ss)

        self.cfg_team_pass = QLineEdit(self.cfg_conn_frame)
        self.cfg_team_pass.setGeometry(QRect(160, 152, 160, 26))
        self.cfg_team_pass.setStyleSheet(input_ss)
        self.cfg_team_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.cfg_team_pass.setPlaceholderText("••••••")

        # Bağlantı kaydet butonu
        self.cfg_conn_save = QPushButton(self.cfg_conn_frame)
        self.cfg_conn_save.setGeometry(QRect(10, 190, 140, 30))
        self.cfg_conn_save.setText("Kaydet & Uygula")
        self.cfg_conn_save.setStyleSheet(save_btn_ss)

        self.cfg_conn_status = QLabel(self.cfg_conn_frame)
        self.cfg_conn_status.setGeometry(QRect(160, 195, 160, 20))
        self.cfg_conn_status.setText("")
        self.cfg_conn_status.setStyleSheet("color: #888; font-size: 10px; background: transparent;")

        # ── 2) HSS MANUEL GİRİŞ ──────────────────────────────
        self.cfg_hss_frame = QFrame(self.tab_settings)
        self.cfg_hss_frame.setGeometry(QRect(3, 262, 335, 226))
        self.cfg_hss_frame.setStyleSheet(panel_ss)

        lbl_hss = QLabel(self.cfg_hss_frame)
        lbl_hss.setGeometry(QRect(8, 4, 280, 18))
        lbl_hss.setText("HSS MANUEL GİRİŞ (Hakem Koordinatları)")
        lbl_hss.setStyleSheet(hdr_ss)

        # HSS giriş alanları (3 adet HSS bölgesi)
        self.cfg_hss_entries = []
        for i in range(3):
            y = 28 + i * 54

            lbl = QLabel(self.cfg_hss_frame)
            lbl.setGeometry(QRect(10, y, 80, 16))
            lbl.setText(f"HSS {i+1}:")
            lbl.setStyleSheet(lbl_ss)

            lbl_lat = QLabel(self.cfg_hss_frame)
            lbl_lat.setGeometry(QRect(70, y, 30, 16))
            lbl_lat.setText("Lat:")
            lbl_lat.setStyleSheet(lbl_ss)

            lat = QLineEdit(self.cfg_hss_frame)
            lat.setGeometry(QRect(10, y + 18, 100, 24))
            lat.setStyleSheet(input_ss)
            lat.setPlaceholderText("38.xxxx")

            lbl_lon = QLabel(self.cfg_hss_frame)
            lbl_lon.setGeometry(QRect(120, y, 30, 16))
            lbl_lon.setText("Lon:")
            lbl_lon.setStyleSheet(lbl_ss)

            lon = QLineEdit(self.cfg_hss_frame)
            lon.setGeometry(QRect(115, y + 18, 100, 24))
            lon.setStyleSheet(input_ss)
            lon.setPlaceholderText("35.xxxx")

            lbl_r = QLabel(self.cfg_hss_frame)
            lbl_r.setGeometry(QRect(225, y, 50, 16))
            lbl_r.setText("R (m):")
            lbl_r.setStyleSheet(lbl_ss)

            radius = QSpinBox(self.cfg_hss_frame)
            radius.setGeometry(QRect(220, y + 18, 70, 24))
            radius.setStyleSheet(input_ss)
            radius.setRange(1, 500)
            radius.setValue(50)

            self.cfg_hss_entries.append({"lat": lat, "lon": lon, "radius": radius})

        self.cfg_hss_apply = QPushButton(self.cfg_hss_frame)
        self.cfg_hss_apply.setGeometry(QRect(10, 192, 140, 28))
        self.cfg_hss_apply.setText("Haritaya Uygula")
        self.cfg_hss_apply.setStyleSheet(save_btn_ss)

        self.cfg_hss_clear = QPushButton(self.cfg_hss_frame)
        self.cfg_hss_clear.setGeometry(QRect(160, 192, 100, 28))
        self.cfg_hss_clear.setText("Temizle")
        self.cfg_hss_clear.setStyleSheet(btn_ss)

        # ── 3) KALİBRASYON ───────────────────────────────────
        self.cfg_calib_frame = QFrame(self.tab_settings)
        self.cfg_calib_frame.setGeometry(QRect(342, 28, 340, 460))
        self.cfg_calib_frame.setStyleSheet(panel_ss)

        lbl_calib = QLabel(self.cfg_calib_frame)
        lbl_calib.setGeometry(QRect(8, 4, 260, 18))
        lbl_calib.setText("KALİBRASYON (Kamera & Sensör)")
        lbl_calib.setStyleSheet(hdr_ss)

        # Kamera ofsetleri
        lbl_cam = QLabel(self.cfg_calib_frame)
        lbl_cam.setGeometry(QRect(10, 28, 200, 16))
        lbl_cam.setText("Kamera Ofset:")
        lbl_cam.setStyleSheet("color: white; font-size: 11px; font-weight: bold; background: transparent;")

        cam_offsets = [
            ("X (px):",  "cfg_cam_x",   -500, 500, 0),
            ("Y (px):",  "cfg_cam_y",   -500, 500, 0),
            ("Açı (°):", "cfg_cam_ang", -180, 180, 0),
        ]
        for j, (label_text, attr, mn, mx, default) in enumerate(cam_offsets):
            y = 48 + j * 40

            lbl = QLabel(self.cfg_calib_frame)
            lbl.setGeometry(QRect(10, y, 70, 16))
            lbl.setText(label_text)
            lbl.setStyleSheet(lbl_ss)

            spin = QSpinBox(self.cfg_calib_frame)
            spin.setGeometry(QRect(80, y, 100, 24))
            spin.setStyleSheet(input_ss)
            spin.setRange(mn, mx)
            spin.setValue(default)
            setattr(self, attr, spin)

        # Sensör ofsetleri
        lbl_sens = QLabel(self.cfg_calib_frame)
        lbl_sens.setGeometry(QRect(10, 176, 200, 16))
        lbl_sens.setText("Sensör Ofset:")
        lbl_sens.setStyleSheet("color: white; font-size: 11px; font-weight: bold; background: transparent;")

        sensor_offsets = [
            ("GPS N (m):",   "cfg_gps_n",   -10.0, 10.0, 0.0),
            ("GPS E (m):",   "cfg_gps_e",   -10.0, 10.0, 0.0),
            ("GPS D (m):",   "cfg_gps_d",   -10.0, 10.0, 0.0),
            ("Baro Ofs (m):", "cfg_baro",   -50.0, 50.0, 0.0),
            ("IMU Roll (°):", "cfg_imu_r",  -10.0, 10.0, 0.0),
            ("IMU Pitch (°):","cfg_imu_p",  -10.0, 10.0, 0.0),
            ("IMU Yaw (°):", "cfg_imu_y",   -10.0, 10.0, 0.0),
        ]
        for k, (label_text, attr, mn, mx, default) in enumerate(sensor_offsets):
            y = 196 + k * 32

            lbl = QLabel(self.cfg_calib_frame)
            lbl.setGeometry(QRect(10, y, 100, 16))
            lbl.setText(label_text)
            lbl.setStyleSheet(lbl_ss)

            spin = QDoubleSpinBox(self.cfg_calib_frame)
            spin.setGeometry(QRect(115, y, 100, 24))
            spin.setStyleSheet(input_ss)
            spin.setRange(mn, mx)
            spin.setSingleStep(0.01)
            spin.setDecimals(2)
            spin.setValue(default)
            setattr(self, attr, spin)

        # Kalibrasyon butonları
        self.cfg_calib_save = QPushButton(self.cfg_calib_frame)
        self.cfg_calib_save.setGeometry(QRect(10, 424, 140, 28))
        self.cfg_calib_save.setText("Kaydet & Uygula")
        self.cfg_calib_save.setStyleSheet(save_btn_ss)

        self.cfg_calib_reset = QPushButton(self.cfg_calib_frame)
        self.cfg_calib_reset.setGeometry(QRect(160, 424, 100, 28))
        self.cfg_calib_reset.setText("Sıfırla")
        self.cfg_calib_reset.setStyleSheet(btn_ss)

    def _setupDebug(self):
        """Debug / Mühendislik Sekmesi"""
        W = 1020
        dark = "#3a3a3a"
        panel_ss = f"background-color: {dark}; border: 1px solid #555; border-radius: 4px;"
        hdr_ss = "color: white; font-size: 12px; font-weight: bold; background: transparent;"
        table_ss = (
            "QTableWidget { background-color: #1a1a1a; color: #00ff00; gridline-color: #333; "
            "font-family: 'Courier New', monospace; font-size: 11px; border: none; }\n"
            "QTableWidget::item { padding: 2px; }\n"
            "QHeaderView::section { background-color: #3a3a3a; color: #cccccc; "
            "font-weight: bold; font-size: 10px; border: 1px solid #555; padding: 3px; }")
        log_ss = (
            "QTextBrowser { background-color: #0a0a0a; color: #00ff00; "
            "font-family: 'Courier New', monospace; font-size: 11px; "
            "border: 1px solid #444; border-radius: 3px; }")

        # ── BAŞLIK ────────────────────────────────────────────
        self.dbg_title = QLabel(self.tab_debug)
        self.dbg_title.setGeometry(QRect(10, 4, 300, 20))
        self.dbg_title.setText("DEBUG / MÜHENDİSLİK")
        self.dbg_title.setStyleSheet("color: #ff8800; font-size: 13px; font-weight: bold; background: transparent;")

        # ── 1) HAM VERİ TABLOSU (Telemetry Table) ───────────
        self.dbg_telem_frame = QFrame(self.tab_debug)
        self.dbg_telem_frame.setGeometry(QRect(3, 28, 505, 460))
        self.dbg_telem_frame.setStyleSheet(panel_ss)

        lbl_telem = QLabel(self.dbg_telem_frame)
        lbl_telem.setGeometry(QRect(8, 4, 200, 18))
        lbl_telem.setText("HAM VERİ TABLOSU (MAVLink)")
        lbl_telem.setStyleSheet(hdr_ss)

        self.dbg_telem_table = QTableWidget(self.dbg_telem_frame)
        self.dbg_telem_table.setGeometry(QRect(4, 26, 497, 428))
        self.dbg_telem_table.setStyleSheet(table_ss)
        self.dbg_telem_table.setColumnCount(3)
        self.dbg_telem_table.setHorizontalHeaderLabels(["Parametre", "Değer", "Birim"])
        self.dbg_telem_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.dbg_telem_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.dbg_telem_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.dbg_telem_table.setColumnWidth(1, 120)
        self.dbg_telem_table.setColumnWidth(2, 60)
        self.dbg_telem_table.verticalHeader().setVisible(False)
        self.dbg_telem_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.dbg_telem_table.setAlternatingRowColors(True)
        self.dbg_telem_table.setStyleSheet(
            table_ss + "\nQTableWidget { alternate-background-color: #111; }")

        # Placeholder satırları
        telem_rows = [
            # IMU
            ("IMU / acc_x",  "—", "m/s²"),
            ("IMU / acc_y",  "—", "m/s²"),
            ("IMU / acc_z",  "—", "m/s²"),
            ("IMU / gyro_x", "—", "rad/s"),
            ("IMU / gyro_y", "—", "rad/s"),
            ("IMU / gyro_z", "—", "rad/s"),
            # GPS
            ("GPS / lat",    "—", "°"),
            ("GPS / lon",    "—", "°"),
            ("GPS / alt",    "—", "m"),
            ("GPS / fix",    "—", ""),
            ("GPS / sat",    "—", ""),
            ("GPS / hdop",   "—", ""),
            # Attitude
            ("ATT / roll",   "—", "°"),
            ("ATT / pitch",  "—", "°"),
            ("ATT / yaw",    "—", "°"),
            # Servo
            ("SERVO / ch1",  "—", "µs"),
            ("SERVO / ch2",  "—", "µs"),
            ("SERVO / ch3",  "—", "µs"),
            ("SERVO / ch4",  "—", "µs"),
            # System
            ("SYS / bat_v",  "—", "V"),
            ("SYS / bat_%",  "—", "%"),
            ("SYS / mode",   "—", ""),
            ("SYS / armed",  "—", ""),
            ("SYS / uptime", "—", "s"),
        ]
        self.dbg_telem_table.setRowCount(len(telem_rows))
        for row, (param, val, unit) in enumerate(telem_rows):
            self.dbg_telem_table.setItem(row, 0, QTableWidgetItem(param))
            self.dbg_telem_table.setItem(row, 1, QTableWidgetItem(val))
            self.dbg_telem_table.setItem(row, 2, QTableWidgetItem(unit))

        # ── 2) SUNUCU LOGLARI ────────────────────────────────
        self.dbg_log_frame = QFrame(self.tab_debug)
        self.dbg_log_frame.setGeometry(QRect(512, 28, 508, 280))
        self.dbg_log_frame.setStyleSheet(panel_ss)

        lbl_log = QLabel(self.dbg_log_frame)
        lbl_log.setGeometry(QRect(8, 4, 200, 18))
        lbl_log.setText("SUNUCU LOGLARI")
        lbl_log.setStyleSheet(hdr_ss)

        self.dbg_log_browser = QTextBrowser(self.dbg_log_frame)
        self.dbg_log_browser.setGeometry(QRect(4, 26, 500, 248))
        self.dbg_log_browser.setStyleSheet(log_ss)
        self.dbg_log_browser.setOpenExternalLinks(False)
        self.dbg_log_browser.append('<span style="color:#888">[--:--:--]</span> Sunucu logları bekleniyor...')

        # Log durum çubuğu
        self.dbg_log_status = QLabel(self.dbg_log_frame)
        self.dbg_log_status.setGeometry(QRect(340, 4, 160, 18))
        self.dbg_log_status.setAlignment(Qt.AlignRight)
        self.dbg_log_status.setText("Bağlantı: —")
        self.dbg_log_status.setStyleSheet("color: #ff4444; font-size: 10px; background: transparent;")

        # ── 3) REDIS MONİTÖR ─────────────────────────────────
        self.dbg_redis_frame = QFrame(self.tab_debug)
        self.dbg_redis_frame.setGeometry(QRect(512, 312, 508, 176))
        self.dbg_redis_frame.setStyleSheet(panel_ss)

        lbl_redis = QLabel(self.dbg_redis_frame)
        lbl_redis.setGeometry(QRect(8, 4, 200, 18))
        lbl_redis.setText("REDIS MONİTÖR")
        lbl_redis.setStyleSheet(hdr_ss)

        # Paket hızı göstergeleri
        rate_items = [
            ("Gelen",  "dbg_redis_in"),
            ("Giden",  "dbg_redis_out"),
            ("Toplam", "dbg_redis_total"),
        ]
        for i, (label_text, attr) in enumerate(rate_items):
            lbl = QLabel(self.dbg_redis_frame)
            lbl.setGeometry(QRect(8 + i * 100, 26, 90, 14))
            lbl.setText(label_text)
            lbl.setStyleSheet("color: #aaa; font-size: 10px; background: transparent;")
            val = QLabel(self.dbg_redis_frame)
            val.setGeometry(QRect(8 + i * 100, 42, 90, 22))
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet(
                "QLabel { background-color: black; color: #00ff00; "
                "font-family: 'Courier New', monospace; font-size: 12px; "
                "font-weight: bold; border: 1px solid #333; border-radius: 3px; }")
            val.setText("0 pkt/s")
            setattr(self, attr + "_val", val)

        # Redis durum
        self.dbg_redis_status = QLabel(self.dbg_redis_frame)
        self.dbg_redis_status.setGeometry(QRect(320, 26, 180, 18))
        self.dbg_redis_status.setAlignment(Qt.AlignRight)
        self.dbg_redis_status.setText("Redis: BAĞLI DEĞİL")
        self.dbg_redis_status.setStyleSheet("color: #ff4444; font-size: 10px; font-weight: bold; background: transparent;")

        # Grafik alanı (placeholder — ileride pyqtgraph/matplotlib ile doldurulacak)
        self.dbg_redis_graph = QLabel(self.dbg_redis_frame)
        self.dbg_redis_graph.setGeometry(QRect(4, 68, 500, 102))
        self.dbg_redis_graph.setAlignment(Qt.AlignCenter)
        self.dbg_redis_graph.setStyleSheet(
            "background-color: #0a0a0a; color: #444; font-size: 12px; "
            "border: 1px solid #333; border-radius: 3px;")
        self.dbg_redis_graph.setText("PAKET/SN GRAFİĞİ\n(pyqtgraph ile doldurulacak)")

    def _loadMap(self):
        """Folium haritasını oluştur ve QWebEngineView'e yükle"""
        # Örnek merkez koordinat (yarışma alanı)
        center_lat, center_lon = 39.7833, 30.5167

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=15,
            tiles="OpenStreetMap",
        )

        # Geofence sınırı (örnek dikdörtgen alan)
        geofence_coords = [
            [center_lat + 0.008, center_lon - 0.012],
            [center_lat + 0.008, center_lon + 0.012],
            [center_lat - 0.008, center_lon + 0.012],
            [center_lat - 0.008, center_lon - 0.012],
        ]
        folium.Polygon(
            locations=geofence_coords,
            color="#44ff44", weight=2, fill=True,
            fill_color="#44ff44", fill_opacity=0.05,
            tooltip="Geofence Sınırı",
        ).add_to(m)

        # HSS bölgeleri (örnek kırmızı daireler)
        hss_zones = [
            (center_lat + 0.003, center_lon - 0.005, 80),
            (center_lat - 0.002, center_lon + 0.004, 60),
        ]
        for lat, lon, radius in hss_zones:
            folium.Circle(
                location=[lat, lon], radius=radius,
                color="#ff3333", weight=2, fill=True,
                fill_color="#ff3333", fill_opacity=0.25,
                tooltip=f"HSS (r={radius}m)",
            ).add_to(m)

        # Kendi İHA (mavi ikon)
        folium.Marker(
            location=[center_lat, center_lon],
            icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
            tooltip="Kendi İHA",
        ).add_to(m)

        # Rakip İHA'lar (kırmızı ikonlar)
        rivals = [
            (center_lat + 0.002, center_lon + 0.003),
            (center_lat - 0.003, center_lon - 0.002),
        ]
        for rlat, rlon in rivals:
            folium.Marker(
                location=[rlat, rlon],
                icon=folium.Icon(color="red", icon="plane", prefix="fa"),
                tooltip="Rakip İHA",
            ).add_to(m)

        # Kamikaze hedef (QR ikonu)
        folium.Marker(
            location=[center_lat - 0.001, center_lon + 0.006],
            icon=folium.Icon(color="orange", icon="qrcode", prefix="fa"),
            tooltip="Kamikaze Hedefi (QR)",
        ).add_to(m)

        # HTML'e dönüştür ve yükle
        html = m.get_root().render()
        self.dash_map_view.setHtml(html)

    def _setupDashboard(self):
        """Ana Ekran - Yarışma Dashboard"""
        W = 1020
        dark = "#3a3a3a"
        panel_ss = f"background-color: {dark}; border: 1px solid #555; border-radius: 4px;"
        val_ss = ("QLabel { background-color: black; color: #00ff00; "
                  "font-family: 'Courier New', monospace; font-size: 11px; "
                  "font-weight: bold; border: 1px solid #333; padding: 1px; }")
        hdr_ss = "color: white; font-size: 10px; background-color: transparent;"
        btn_ss = ("QPushButton { background-color: #800000; color: white; "
                  "border: 2px solid #5a0000; border-radius: 8px; padding: 6px; }\n"
                  "QPushButton:hover { background-color: #a00000; }\n"
                  "QPushButton:pressed { background-color: #5a0000; }")

        # ── TELEMETRY STRIP ──────────────────────────────────
        self.dash_telem = QFrame(self.tab_dashboard)
        self.dash_telem.setGeometry(QRect(0, 0, W, 46))
        self.dash_telem.setStyleSheet(f"background-color: {dark};")

        telem_items = [
            ("Enlem",   "dash_enlem"),   ("Boylam",  "dash_boylam"),
            ("İrtifa",  "dash_irtifa"),  ("Dikilme", "dash_dikilme"),
            ("Yönelme", "dash_yonelme"), ("Yatış",   "dash_yatis"),
            ("Hız",     "dash_hiz"),     ("Batarya", "dash_bat"),
            ("Saat",    "dash_saat"),
        ]
        spacing = W // len(telem_items)
        for i, (title, attr) in enumerate(telem_items):
            x = i * spacing + 8
            lbl = QLabel(self.dash_telem)
            lbl.setGeometry(QRect(x, 4, spacing - 12, 14))
            lbl.setText(title)
            lbl.setStyleSheet(hdr_ss)
            val = QLabel(self.dash_telem)
            val.setGeometry(QRect(x, 22, spacing - 12, 18))
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet(val_ss)
            val.setText("—")
            setattr(self, attr + "_val", val)

        # ── CANLI HARİTA (Folium + QWebEngineView) ───────────
        self.dash_map_frame = QFrame(self.tab_dashboard)
        self.dash_map_frame.setGeometry(QRect(3, 50, 585, 375))
        self.dash_map_frame.setStyleSheet(panel_ss)

        self.dash_map_view = QWebEngineView(self.dash_map_frame)
        self.dash_map_view.setGeometry(QRect(2, 2, 581, 371))
        self._loadMap()

        # ── HUD VIDEO ─────────────────────────────────────────
        self.dash_hud_frame = QFrame(self.tab_dashboard)
        self.dash_hud_frame.setGeometry(QRect(592, 50, 428, 255))
        self.dash_hud_frame.setStyleSheet(panel_ss)

        self.dash_hud_label = QLabel(self.dash_hud_frame)
        self.dash_hud_label.setGeometry(QRect(2, 2, 424, 251))
        self.dash_hud_label.setAlignment(Qt.AlignCenter)
        self.dash_hud_label.setStyleSheet(
            "background-color: #1a1a1a; color: #666; font-size: 16px; border: none;")
        self.dash_hud_label.setText("KAMERA AKIŞI")
        self.dash_hud_label.setScaledContents(True)

        # Bounding box overlay indicator
        self.dash_bbox_status = QLabel(self.dash_hud_frame)
        self.dash_bbox_status.setGeometry(QRect(4, 230, 100, 18))
        self.dash_bbox_status.setAlignment(Qt.AlignCenter)
        self.dash_bbox_status.setStyleSheet(
            "background-color: rgba(200,0,0,180); color: white; font-size: 10px; "
            "font-weight: bold; border-radius: 3px; border: none;")
        self.dash_bbox_status.setText("BBOX: YOK")

        # ── DURUM PANELİ ─────────────────────────────────────
        self.dash_status_frame = QFrame(self.tab_dashboard)
        self.dash_status_frame.setGeometry(QRect(592, 309, 428, 116))
        self.dash_status_frame.setStyleSheet(panel_ss)

        status_items = [
            ("Mod",       "dash_st_mod",   0),
            ("Batarya",   "dash_st_bat",   108),
            ("Kilitlenme","dash_st_lock",  216),
            ("Hız",       "dash_st_spd",   324),
        ]
        for label_text, attr, sx in status_items:
            lbl = QLabel(self.dash_status_frame)
            lbl.setGeometry(QRect(sx + 6, 6, 96, 14))
            lbl.setText(label_text)
            lbl.setStyleSheet("color: #aaa; font-size: 10px; background: transparent; border: none;")
            val = QLabel(self.dash_status_frame)
            val.setGeometry(QRect(sx + 6, 24, 96, 24))
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet(val_ss)
            val.setText("—")
            setattr(self, attr + "_val", val)

        # Mod değerini öne çıkar
        self.dash_st_mod_val.setStyleSheet(
            "QLabel { background-color: #00cc44; color: white; font-size: 13px; "
            "font-weight: bold; border-radius: 5px; border: none; }")
        self.dash_st_mod_val.setText("OTONOM")

        # Kilitlenme durumu + süre
        self.dash_lock_indicator = QLabel(self.dash_status_frame)
        self.dash_lock_indicator.setGeometry(QRect(6, 56, 200, 22))
        self.dash_lock_indicator.setAlignment(Qt.AlignCenter)
        self.dash_lock_indicator.setStyleSheet(
            "background-color: #ccaa00; color: black; font-size: 11px; "
            "font-weight: bold; border-radius: 4px; border: none;")
        self.dash_lock_indicator.setText("ARANIYOR")

        self.dash_lock_timer = QLabel(self.dash_status_frame)
        self.dash_lock_timer.setGeometry(QRect(210, 56, 90, 22))
        self.dash_lock_timer.setAlignment(Qt.AlignCenter)
        self.dash_lock_timer.setStyleSheet(
            "QLabel { background-color: black; color: #ff4444; "
            "font-family: 'Courier New', monospace; font-size: 11px; "
            "font-weight: bold; border-radius: 4px; border: 1px solid #555; }")
        self.dash_lock_timer.setText("0.0s / 4.0s")

        self.dash_lock_coord = QLabel(self.dash_status_frame)
        self.dash_lock_coord.setGeometry(QRect(6, 82, 300, 16))
        self.dash_lock_coord.setStyleSheet("color: #aaa; font-size: 10px; background: transparent; border: none;")
        self.dash_lock_coord.setText("")

        # Manuel mod sayacı
        self.dash_manuel_count = QLabel(self.dash_status_frame)
        self.dash_manuel_count.setGeometry(QRect(310, 56, 60, 22))
        self.dash_manuel_count.setAlignment(Qt.AlignCenter)
        self.dash_manuel_count.setStyleSheet(
            "background-color: #555; color: #ffcc00; font-size: 11px; "
            "font-weight: bold; border-radius: 4px; border: 1px solid #777;")
        self.dash_manuel_count.setText("M: 0")

        # ── KOMUT ÇUBUĞU ─────────────────────────────────────
        self.dash_cmd_frame = QFrame(self.tab_dashboard)
        self.dash_cmd_frame.setGeometry(QRect(3, 429, W - 3, 60))
        self.dash_cmd_frame.setStyleSheet(f"background-color: {dark}; border: 1px solid #555; border-radius: 4px;")

        btn_names = [("ARM", "dash_btn_arm"), ("DISARM", "dash_btn_disarm"),
                     ("RTL", "dash_btn_rtl"), ("Acil İniş", "dash_btn_emergency")]
        for k, (text, attr) in enumerate(btn_names):
            btn = QPushButton(self.dash_cmd_frame)
            btn.setGeometry(QRect(20 + k * 120, 14, 100, 32))
            btn.setText(text)
            btn.setStyleSheet(btn_ss)
            setattr(self, attr, btn)

        # Acil iniş butonu farklı renk
        self.dash_btn_emergency.setStyleSheet(
            "QPushButton { background-color: #cc0000; color: white; "
            "border: 2px solid #990000; border-radius: 8px; padding: 6px; font-weight: bold; }\n"
            "QPushButton:hover { background-color: #ff0000; }\n"
            "QPushButton:pressed { background-color: #990000; }")

    def retranslateUi(self, QuanrumUAVArayz):
        QuanrumUAVArayz.setWindowTitle(QCoreApplication.translate("QuanrumUAVArayz", u"Quantum UAV Aray\u00fcz", None))
    # retranslateUi


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_QuanrumUAVArayz()
    ui.setupUi(window)

    # — Video thread başlat (webcam) —
    def update_frame(qimg):
        """Dashboard HUD video label'ını güncelle"""
        pix = QPixmap.fromImage(qimg).scaled(
            ui.dash_hud_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        ui.dash_hud_label.setPixmap(pix)

    video_thread = VideoThread(source=0)
    video_thread.frame_ready.connect(update_frame)
    video_thread.start()

    # Uygulama kapanırken thread'i durdur
    app.aboutToQuit.connect(video_thread.stop)

    window.show()
    sys.exit(app.exec())
