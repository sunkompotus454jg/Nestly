import uuid
from PyQt6.QtGui import QColor

THEMES = {
    "Blue":   {"name": "Синий Неон",      "border": "#00d4ff", "bg": "#141419", "body": "#1a1a21", "title": "#00d4ff"},
    "Purple": {"name": "Фиолетовый Неон", "border": "#b82bf2", "bg": "#16101c", "body": "#1e1626", "title": "#b82bf2"},
    "Green":  {"name": "Зеленый Неон",    "border": "#00ff88", "bg": "#101c15", "body": "#16261c", "title": "#00ff88"},
    "Orange": {"name": "Оранжевый Неон",  "border": "#ffaa00", "bg": "#1c1610", "body": "#261e16", "title": "#ffaa00"},
    "Red":    {"name": "Красный Неон",    "border": "#ff0055", "bg": "#1c1014", "body": "#26161a", "title": "#ff0055"}
}

def qss(color_str):
    c = QColor(color_str)
    if not c.isValid(): 
        return color_str
    
    alpha = c.alpha()
    if alpha < 3: 
        alpha = 3 
        
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {alpha / 255.0:.3f})"

class ThemeManager:
    def __init__(self, config_manager):
        self.config = config_manager

    def get_all_themes(self):
        combined = THEMES.copy()
        customs = self.config.get_custom_themes()
        combined.update(customs)
        return combined

    def add_custom_theme(self, theme_data):
        theme_id = f"Custom_{uuid.uuid4().hex[:6]}"
        self.config.add_custom_theme(theme_id, theme_data)
        return theme_id

    def remove_custom_theme(self, theme_id):
        self.config.remove_custom_theme(theme_id)
