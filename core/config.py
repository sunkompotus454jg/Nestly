import os
import json

USER_ROOT = os.path.expanduser("~")
NESTLY_DIR = os.path.join(USER_ROOT, "NestlyData")
CONFIG_FILE = os.path.join(NESTLY_DIR, "nestly_config.json")

class ConfigManager:
    def __init__(self):
        self.config_data = {
            "version": 2, 
            "current_profile": "default",
            "profiles": {
                "default": {"name": "Default", "fences": []}
            },
            "custom_themes": {}
        }
        os.makedirs(NESTLY_DIR, exist_ok=True)
        self.load_config()
        self.migrate_config()

    def migrate_config(self):
        if "fences" in self.config_data:
            # Migrate from v1
            self.config_data["profiles"]["default"]["fences"] = self.config_data.pop("fences")
            self.config_data["version"] = 2
            self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config_data.update(data)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_current_profile(self):
        return self.config_data.get("current_profile", "default")

    def get_profiles(self):
        return list(self.config_data["profiles"].keys())

    def create_profile(self, profile_name):
        if profile_name not in self.config_data["profiles"]:
            self.config_data["profiles"][profile_name] = {"name": profile_name, "fences": []}
            self.save_config()

    def set_current_profile(self, profile_name):
        if profile_name in self.config_data["profiles"]:
            self.config_data["current_profile"] = profile_name
            self.save_config()

    def get_fences(self):
        profile = self.get_current_profile()
        return self.config_data["profiles"].get(profile, {}).get("fences", [])
        
    def add_fence(self, fence_cfg):
        profile = self.get_current_profile()
        if "fences" not in self.config_data["profiles"][profile]:
            self.config_data["profiles"][profile]["fences"] = []
        self.config_data["profiles"][profile]["fences"].append(fence_cfg)
        self.save_config()
        
    def remove_fence(self, fence_id):
        profile = self.get_current_profile()
        fences = self.config_data["profiles"].get(profile, {}).get("fences", [])
        self.config_data["profiles"][profile]["fences"] = [f for f in fences if f["id"] != fence_id]
        self.save_config()

    def update_fence(self, fence_id, updates):
        """Updates multiple keys for a specific fence and saves config."""
        profile = self.get_current_profile()
        fences = self.config_data["profiles"].get(profile, {}).get("fences", [])
        for f in fences:
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
