from ui.fence_window import FenceInstance

class UIManager:
    """Manages all the PyQt UI windows and coordinates with Core FenceManager."""
    def __init__(self, core_manager):
        self.core = core_manager
        self.windows = {} # fence_id -> FenceInstance
        
        # Listen to core events
        self.core.set_callbacks(self.on_fence_created, self.on_fence_deleted)
        
        # Initialize windows for existing fences
        for cfg in self.core.fence_configs:
            self.on_fence_created(cfg)

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
        self.core.remove_custom_theme(theme_id)
        # Revert theme in all windows using it
        for window in self.windows.values():
            if window.current_theme == theme_id:
                window.apply_theme("Blue")

    def delete_fence(self, fence_id):
        self.core.remove_fence(fence_id)
