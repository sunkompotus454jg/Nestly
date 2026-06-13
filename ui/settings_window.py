import winreg
import os
import sys
import shutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QPushButton, QFileDialog, QMessageBox)

class SettingsWindow(QDialog):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.i18n = ui_manager.i18n
        self.config = ui_manager.core.config
        
        self.setWindowTitle(self.i18n.tr("settings_title"))
        self.resize(300, 200)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Language
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.i18n.tr("language"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.addItem("Українська", "uk")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        # Autostart
        self.autostart_checkbox = QCheckBox(self.i18n.tr("autostart"))
        layout.addWidget(self.autostart_checkbox)
        
        # Export/Import
        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton(self.i18n.tr("export"))
        self.btn_import = QPushButton(self.i18n.tr("import"))
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)
        layout.addLayout(btn_layout)
        
        self.btn_export.clicked.connect(self.export_config)
        self.btn_import.clicked.connect(self.import_config)
        
        # Save/Cancel
        controls_layout = QHBoxLayout()
        self.btn_save = QPushButton(self.i18n.tr("save"))
        self.btn_cancel = QPushButton(self.i18n.tr("cancel"))
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_save)
        controls_layout.addWidget(self.btn_cancel)
        layout.addLayout(controls_layout)
        
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel.clicked.connect(self.reject)
        
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
