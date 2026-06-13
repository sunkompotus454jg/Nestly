import os
import json
import pytest
from core.config import ConfigManager
import core.config

@pytest.fixture
def temp_config_file(tmp_path, monkeypatch):
    """Fixture to set up a temporary config file for testing."""
    test_dir = tmp_path / "NestlyData"
    test_dir.mkdir()
    test_config_path = test_dir / "nestly_config.json"
    
    # Mock paths in core.config
    monkeypatch.setattr(core.config, "NESTLY_DIR", str(test_dir))
    monkeypatch.setattr(core.config, "CONFIG_FILE", str(test_config_path))
    
    return test_config_path

def test_initialization(temp_config_file):
    manager = ConfigManager()
    assert manager.config_data["version"] == 2
    assert manager.get_fences() == []
    assert "default" in manager.get_profiles()

def test_add_fence(temp_config_file):
    manager = ConfigManager()
    manager.add_fence({"id": "test1", "name": "Fence 1"})
    
    assert len(manager.get_fences()) == 1
    assert manager.get_fences()[0]["id"] == "test1"
    
    # Verify it saves to disk
    with open(temp_config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["profiles"]["default"]["fences"]) == 1
    assert data["profiles"]["default"]["fences"][0]["id"] == "test1"

def test_remove_fence(temp_config_file):
    manager = ConfigManager()
    manager.add_fence({"id": "test1"})
    manager.add_fence({"id": "test2"})
    
    manager.remove_fence("test1")
    fences = manager.get_fences()
    assert len(fences) == 1
    assert fences[0]["id"] == "test2"

def test_update_fence(temp_config_file):
    manager = ConfigManager()
    manager.add_fence({"id": "test1", "theme": "Blue"})
    
    success = manager.update_fence("test1", {"theme": "Red", "width": 800})
    assert success is True
    
    fences = manager.get_fences()
    assert fences[0]["theme"] == "Red"
    assert fences[0]["width"] == 800
    
def test_custom_themes(temp_config_file):
    manager = ConfigManager()
    manager.add_custom_theme("Custom_1", {"name": "Test Theme"})
    
    themes = manager.get_custom_themes()
    assert "Custom_1" in themes
    assert themes["Custom_1"]["name"] == "Test Theme"
    
    manager.remove_custom_theme("Custom_1")
    assert "Custom_1" not in manager.get_custom_themes()
