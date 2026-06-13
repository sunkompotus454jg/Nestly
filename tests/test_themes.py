import pytest
from core.themes import ThemeManager, qss, THEMES
from core.config import ConfigManager
import core.config

@pytest.fixture
def temp_config_file(tmp_path, monkeypatch):
    test_dir = tmp_path / "NestlyData"
    test_dir.mkdir()
    test_config_path = test_dir / "nestly_config.json"
    monkeypatch.setattr(core.config, "NESTLY_DIR", str(test_dir))
    monkeypatch.setattr(core.config, "CONFIG_FILE", str(test_config_path))
    return test_config_path

def test_qss():
    # test qss function for correct rgba parsing
    res = qss("#ff0000")
    # depending on PyQt's QColor behavior, we know it returns rgba(255, 0, 0, x)
    assert "rgba(255, 0, 0" in res

def test_theme_manager_defaults(temp_config_file):
    cfg = ConfigManager()
    manager = ThemeManager(cfg)
    
    themes = manager.get_all_themes()
    # It should have all defaults
    assert "Blue" in themes
    assert "Purple" in themes
    assert themes["Blue"]["name"] == "Синий Неон"

def test_add_remove_custom_theme(temp_config_file):
    cfg = ConfigManager()
    manager = ThemeManager(cfg)
    
    theme_id = manager.add_custom_theme({
        "name": "My Custom",
        "border": "#123456",
        "bg": "#000000",
        "body": "#111111",
        "title": "#ffffff"
    })
    
    themes = manager.get_all_themes()
    assert theme_id in themes
    assert themes[theme_id]["name"] == "My Custom"
    
    manager.remove_custom_theme(theme_id)
    assert theme_id not in manager.get_all_themes()
