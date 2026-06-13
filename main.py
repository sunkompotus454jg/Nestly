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
    if "--create" in sys.argv and len(fence_manager.fence_configs) > 0:
        fence_manager.create_new_fence()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()