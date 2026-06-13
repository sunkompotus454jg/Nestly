import os
import json

USER_ROOT = os.path.expanduser("~")
MYFENCES_DIR = os.path.join(USER_ROOT, "MyFencesData")
CONFIG_FILE = os.path.join(MYFENCES_DIR, "fences_config.json")

class ConfigManager:
    def __init__(self):
        self.config_data = {"version": 1, "fences": [], "custom_themes": {}}
        os.makedirs(MYFENCES_DIR, exist_ok=True)
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "version" not in data:
                        data["version"] = 1
                    if "fences" not in data:
                        data["fences"] = []
                    if "custom_themes" not in data:
                        data["custom_themes"] = {}
                    self.config_data = data
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get_fences(self):
        return self.config_data.get("fences", [])
        
    def add_fence(self, fence_cfg):
        self.config_data["fences"].append(fence_cfg)
        self.save_config()
        
    def remove_fence(self, fence_id):
        self.config_data["fences"] = [f for f in self.config_data["fences"] if f["id"] != fence_id]
        self.save_config()

    def update_fence(self, fence_id, updates):
        """Updates multiple keys for a specific fence and saves config."""
        for f in self.config_data["fences"]:
            if f["id"] == fence_id:
                f.update(updates)
                self.save_config()
                return True
        return False

    def get_custom_themes(self):
        return self.config_data.get("custom_themes", {})
        
    def add_custom_theme(self, theme_id, theme_data):
        if "custom_themes" not in self.config_data:
            self.config_data["custom_themes"] = {}
        self.config_data["custom_themes"][theme_id] = theme_data
        self.save_config()
        
    def remove_custom_theme(self, theme_id):
        if "custom_themes" in self.config_data and theme_id in self.config_data["custom_themes"]:
            del self.config_data["custom_themes"][theme_id]
            self.save_config()
