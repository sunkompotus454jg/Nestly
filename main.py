import sys
from PyQt6.QtWidgets import QApplication

from core.config import ConfigManager
from core.themes import ThemeManager
from core.manager import FenceManager
from core.i18n import I18nManager
from ui.app import UIManager
from ipc.single_instance import IPCManager

def main():
    app = QApplication(sys.argv)
    
    import os
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "nestly_icon.png")
    app.setWindowIcon(QIcon(icon_path))
    
    app.setStyleSheet("""
        QDialog, QMessageBox, QInputDialog {
            background-color: #1a1a21;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QLabel {
            color: #ffffff;
        }
        QPushButton {
            background-color: #141419;
            color: #ffffff;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px 15px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QPushButton:hover {
            background-color: #00d4ff;
            color: #000000;
            border: 1px solid #00d4ff;
        }
        QLineEdit, QComboBox {
            background-color: #141419;
            color: #ffffff;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 6px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #00d4ff;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #00d4ff;
        }
        QComboBox QAbstractItemView {
            background-color: #1a1a21;
            color: #ffffff;
            border: 1px solid #555;
            selection-background-color: rgba(255, 255, 255, 30);
        }
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #555;
            background-color: #141419;
        }
        QCheckBox::indicator:hover {
            border: 1px solid #00d4ff;
        }
        QCheckBox::indicator:checked {
            background-color: #00d4ff;
            border: 1px solid #00d4ff;
        }
        QMenu {
            background-color: #1a1a21;
            color: white;
            border: 1px solid #00d4ff;
            border-radius: 5px;
            font-family: 'Segoe UI';
            font-size: 13px;
        }
        QMenu::item {
            padding: 8px 20px;
        }
        QMenu::item:selected {
            background-color: rgba(255, 255, 255, 20);
        }
    """)
    
    # 1. Initialize IPC and check if already running
    # If running, we might send a message (e.g. CREATE_NEW) and exit
    ipc_manager = IPCManager("NestlyApp", None)
    if ipc_manager.check_running():
        sys.exit(0)
        
    # 2. Initialize Core components
    config_manager = ConfigManager()
    theme_manager = ThemeManager(config_manager)
    i18n_manager = I18nManager(config_manager)
    fence_manager = FenceManager(config_manager, theme_manager, i18n_manager)
    
    # 3. Initialize UI
    ui_manager = UIManager(fence_manager, i18n_manager)
    
    # 4. Initialize Hotkeys
    from core.hotkeys import HotkeyManager
    hotkey_manager = HotkeyManager(ui_manager)
    
    # Update IPC callback to UI so that CREATE_NEW can be handled
    ipc_manager.on_create_new = fence_manager.create_new_fence
    ipc_manager.start_server()

    # If launched with --create and it was the first instance, maybe create one?
    # Actually, FenceManager creates one by default if none exist.
    if ("--create-fence" in sys.argv or "--create" in sys.argv) and len(fence_manager.fence_configs) > 0:
        fence_manager.create_new_fence()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()