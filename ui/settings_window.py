import winreg
import os
import sys
import shutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QPushButton, QFileDialog, QMessageBox, QFrame, QGraphicsDropShadowEffect, QWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QColor

class SettingsWindow(QDialog):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.i18n = ui_manager.i18n
        self.config = ui_manager.core.config
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(380, 280)
        self.drag_pos = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        # Main shadow and container
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        
        self.container = QFrame(self)
        self.container.setObjectName("SettingsContainer")
        self.container.setStyleSheet("""
            QFrame#SettingsContainer {
                background-color: #1e1e24;
                border: 1px solid #3f414d;
                border-radius: 8px;
            }
        """)
        self.container.setGraphicsEffect(self.shadow)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header (Custom Title Bar)
        self.header = QFrame(self.container)
        self.header.setStyleSheet("background-color: #262831; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "nestly_icon.png")
        icon_label.setPixmap(QIcon(icon_path).pixmap(20, 20))
        
        title_label = QLabel(self.i18n.tr("settings_title"))
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton#closeBtn { background: transparent; border: none; font-size: 14px; color: #a0a0a0; }
            QPushButton#closeBtn:hover { color: #ff4747; background: rgba(255, 71, 71, 0.1); border-radius: 4px; }
        """)
        close_btn.clicked.connect(self.reject)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        layout.addWidget(self.header)
        
        # Separator line
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #3f414d;")
        layout.addWidget(sep)
        
        # Body
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)
        
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.i18n.tr("language"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.addItem("Українська", "uk")
        lang_layout.addWidget(lang_label)
        lang_layout.addStretch()
        lang_layout.addWidget(self.lang_combo)
        body_layout.addLayout(lang_layout)
        
        self.autostart_checkbox = QCheckBox(self.i18n.tr("autostart"))
        body_layout.addWidget(self.autostart_checkbox)
        
        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton(self.i18n.tr("export"))
        self.btn_import = QPushButton(self.i18n.tr("import"))
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)
        body_layout.addLayout(btn_layout)
        
        self.btn_export.clicked.connect(self.export_config)
        self.btn_import.clicked.connect(self.import_config)
        
        layout.addWidget(body_widget)
        
        # Footer
        footer = QFrame()
        footer.setStyleSheet("background-color: #262831; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        self.btn_save = QPushButton(self.i18n.tr("save"))
        self.btn_save.setObjectName("primaryBtn")
        self.btn_cancel = QPushButton(self.i18n.tr("cancel"))
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_cancel)
        footer_layout.addWidget(self.btn_save)
        
        layout.addWidget(footer)
        
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel.clicked.connect(self.reject)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.header.geometry().contains(event.pos()):
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            
    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def load_settings(self):
        current_lang = self.i18n.current_lang
        idx = self.lang_combo.findData(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.autostart_checkbox.setChecked(self.is_autostart_enabled())
        
    def save_settings(self):
        lang = self.lang_combo.currentData()
        self.i18n.set_language(lang)
        self.set_autostart(self.autostart_checkbox.isChecked())
        self.accept()

    def export_config(self):
        path, _ = QFileDialog.getSaveFileName(self, self.i18n.tr("export"), "", "JSON Files (*.json)")
        if path:
            from core.config import CONFIG_FILE
            shutil.copyfile(CONFIG_FILE, path)
            QMessageBox.information(self, "Export", "Config exported successfully.")
            
    def import_config(self):
        path, _ = QFileDialog.getOpenFileName(self, self.i18n.tr("import"), "", "JSON Files (*.json)")
        if path:
            from core.config import CONFIG_FILE
            shutil.copyfile(path, CONFIG_FILE)
            self.config.load_config()
            if hasattr(self.ui_manager, 'reload_all'):
                self.ui_manager.reload_all()
            QMessageBox.information(self, "Import", "Config imported successfully.")

    def is_autostart_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "Nestly")
            winreg.CloseKey(key)
            return True
        except OSError:
            return False

    def set_autostart(self, enable):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            if enable:
                exe_path = sys.executable
                script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                if getattr(sys, 'frozen', False):
                    command = f'"{sys.executable}"'
                else:
                    command = f'"{exe_path}" "{script_path}"'
                winreg.SetValueEx(key, "Nestly", 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, "Nestly")
                except OSError:
                    pass
            winreg.CloseKey(key)
        except OSError:
            pass
