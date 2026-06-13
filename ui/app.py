from ui.fence_window import FenceInstance
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
import sys

class UIManager:
    """Orchestrates UI windows based on Core Manager state."""
    def __init__(self, fence_manager, i18n_manager=None):
        self.core = fence_manager
        self.i18n = i18n_manager
        self.windows = {} # fence_id -> FenceInstance
        
        QApplication.instance().setQuitOnLastWindowClosed(False)
        self.setup_tray()
        
        # Subscribe to Core events
        self.core.set_callbacks(self.on_fence_created, self.on_fence_deleted)
        
        # Create initial windows for existing fences
        for cfg in self.core.fence_configs:
            self.on_fence_created(cfg)

    def setup_tray(self):
        from ui.settings_window import SettingsWindow
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("resources/icons/nestly_icon.png"))
        
        self.tray_menu = QMenu()
        self.action_create = self.tray_menu.addAction(self.tr("tray_create"))
        self.action_create.triggered.connect(self.core.create_new_fence)
        
        # Profiles submenu
        self.profiles_menu = QMenu(self.tr("tray_profiles"), self.tray_menu)
        self.tray_menu.addMenu(self.profiles_menu)
        self.update_tray_profiles_menu()
        
        self.action_settings = self.tray_menu.addAction(self.tr("tray_settings"))
        self.action_settings.triggered.connect(self.open_settings)
        
        self.action_exit = self.tray_menu.addAction(self.tr("tray_exit"))
        self.action_exit.triggered.connect(QApplication.instance().quit)
        
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

    def update_tray_profiles_menu(self):
        self.profiles_menu.clear()
        current_profile = self.core.config.get_current_profile()
        
        from PyQt6.QtGui import QAction
        for p in self.core.config.get_profiles():
            action = QAction(f"{p} {'(Active)' if p == current_profile else ''}", self.profiles_menu)
            action.triggered.connect(lambda checked, name=p: self.switch_profile(name))
            self.profiles_menu.addAction(action)
            
        self.profiles_menu.addSeparator()
        create_action = QAction(self.tr("create_profile"), self.profiles_menu)
        create_action.triggered.connect(self.prompt_create_profile)
        self.profiles_menu.addAction(create_action)

    def prompt_create_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(None, self.tr("create_profile"), "Profile Name:")
        if ok and name:
            self.core.config.create_profile(name)
            self.switch_profile(name)

    def switch_profile(self, profile_name):
        self.core.config.set_current_profile(profile_name)
        self.reload_all()

    def reload_all(self):
        # Close all existing windows
        for window in list(self.windows.values()):
            window.close()
        self.windows.clear()
        
        # Load fences for current profile
        self.core.fence_configs = self.core.config.get_fences()
        if not self.core.fence_configs:
            self.core.create_new_fence()
        else:
            for cfg in self.core.fence_configs:
                self.on_fence_created(cfg)
                
        self.update_tray_profiles_menu()

    def open_settings(self):
        from ui.settings_window import SettingsWindow
        self.settings_win = SettingsWindow(self)
        self.settings_win.exec()

    def tr(self, key, **kwargs):
        return self.i18n.tr(key, **kwargs) if self.i18n else key

    def on_fence_created(self, fence_cfg):
        window = FenceInstance(fence_cfg, self)
        self.windows[fence_cfg["id"]] = window
        # window.show() is called inside FenceInstance

    def on_fence_deleted(self, fence_id):
        if fence_id in self.windows:
            window = self.windows.pop(fence_id)
            window.close()

    def get_all_windows(self):
        return list(self.windows.values())

    def get_all_themes(self):
        return self.core.themes.get_all_themes()

    def apply_global_theme(self, theme_key):
        for window in self.windows.values():
            window.apply_theme(theme_key)
            
    def update_fence_config(self, fence_id, updates):
        self.core.config.update_fence(fence_id, updates)

    def add_custom_theme(self, theme_data):
        return self.core.themes.add_custom_theme(theme_data)

    def remove_custom_theme(self, theme_id):
        self.core.themes.remove_custom_theme(theme_id)
        # Revert theme in all windows using it
        for window in self.windows.values():
            if window.current_theme == theme_id:
                window.apply_theme("Blue")

    def delete_fence(self, fence_id):
        self.core.remove_fence(fence_id)
