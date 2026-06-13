import pytest
import core.config
from core.config import ConfigManager
from core.themes import ThemeManager
from core.manager import FenceManager
import uuid
import os

@pytest.fixture
def temp_config_file(tmp_path, monkeypatch):
    test_dir = tmp_path / "MyFencesData"
    test_dir.mkdir()
    test_config_path = test_dir / "fences_config.json"
    monkeypatch.setattr(core.config, "MYFENCES_DIR", str(test_dir))
    monkeypatch.setattr(core.config, "CONFIG_FILE", str(test_config_path))
    return test_config_path

def test_fence_manager_initialization(temp_config_file):
    cfg = ConfigManager()
    themes = ThemeManager(cfg)
    manager = FenceManager(cfg, themes)
    
    # By default, if no fences exist, it creates one
    assert len(manager.fence_configs) == 1
    assert "fence_" in manager.fence_configs[0]["id"]

def test_callbacks_called_on_create_delete(temp_config_file):
    cfg = ConfigManager()
    themes = ThemeManager(cfg)
    
    # Pre-add one fence so __init__ doesn't trigger create_new_fence automatically
    cfg.add_fence({"id": "dummy_fence"})
    
    manager = FenceManager(cfg, themes)
    
    created_fences = []
    deleted_fences = []
    
    def on_created(fence_cfg):
        created_fences.append(fence_cfg)
        
    def on_deleted(fence_id):
        deleted_fences.append(fence_id)
        
    manager.set_callbacks(on_created, on_deleted)
    
    manager.create_new_fence()
    assert len(created_fences) == 1
    new_id = created_fences[0]["id"]
    
    manager.remove_fence(new_id)
    assert len(deleted_fences) == 1
    assert deleted_fences[0] == new_id
    
    # Also verify the dummy fence wasn't removed
    assert len(manager.fence_configs) == 1
    assert manager.fence_configs[0]["id"] == "dummy_fence"
