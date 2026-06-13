import os
import uuid
import shutil
from core.config import MYFENCES_DIR

class FenceManager:
    """Manages the logic and state of Fences, completely decoupled from UI."""
    def __init__(self, config_manager, theme_manager):
        self.config = config_manager
        self.themes = theme_manager
        
        self.on_fence_created = None
        self.on_fence_deleted = None
        
        self.fence_configs = self.config.get_fences()
        
        if not self.fence_configs:
            self.create_new_fence()

    def set_callbacks(self, on_created, on_deleted):
        self.on_fence_created = on_created
        self.on_fence_deleted = on_deleted

    def create_new_fence(self):
        new_id = f"fence_{uuid.uuid4().hex[:6]}"
        new_folder_path = os.path.join(MYFENCES_DIR, new_id)
        os.makedirs(new_folder_path, exist_ok=True)

        new_config = {
            "id": new_id,
            "title": "Новая Сетка",
            "path": new_folder_path,
            "x": 100, "y": 100,
            "width": 500, "height": 600,
            "theme": "Blue",
            "locked": False
        }
        self.config.add_fence(new_config)
        self.fence_configs = self.config.get_fences() # Refresh the list
        
        if self.on_fence_created:
            self.on_fence_created(new_config)
            
    def remove_fence(self, fence_id):
        fence_cfg = next((f for f in self.fence_configs if f["id"] == fence_id), None)
        if fence_cfg:
            target_path = fence_cfg.get("path", "")
            desktop_dir = os.path.expanduser("~\\Desktop")
            if target_path and os.path.exists(target_path):
                for item in os.listdir(target_path):
                    src_path = os.path.join(target_path, item)
                    try:
                        shutil.move(src_path, desktop_dir)
                    except Exception as e:
                        print(f"Файл {item} занят. ({e})")
                try:
                    shutil.rmtree(target_path)
                except:
                    pass

            self.config.remove_fence(fence_id)
            self.fence_configs = self.config.get_fences()
            
            if self.on_fence_deleted:
                self.on_fence_deleted(fence_id)

    def remove_custom_theme(self, theme_id):
        self.themes.remove_custom_theme(theme_id)
        # We rely on UI components calling a method to refresh themselves if their theme was removed

