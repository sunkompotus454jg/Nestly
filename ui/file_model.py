import os
import queue
from PyQt6.QtGui import QFileSystemModel, QIcon
from PyQt6.QtCore import Qt, QFileInfo, QThread, pyqtSignal, QPersistentModelIndex

try:
    from PyQt6.QtWidgets import QFileIconProvider
except ImportError:
    try:
        from PyQt6.QtGui import QFileIconProvider
    except ImportError:
        from PyQt6.QtGui import QAbstractFileIconProvider as QFileIconProvider

class IconFetchThread(QThread):
    iconReady = pyqtSignal(str, QIcon)

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.running = True
        self.provider = QFileIconProvider()

    def run(self):
        while self.running:
            try:
                path = self.queue.get(timeout=0.1)
                if not self.running:
                    break
                
                # Resolve icon
                icon = None
                info = QFileInfo(path)
                
                if path.lower().endswith('.url'):
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                line = line.strip()
                                if line.lower().startswith("iconfile="):
                                    icon_path = line.split("=", 1)[1].strip().strip('"').strip("'")
                                    if os.path.exists(icon_path):
                                        if icon_path.lower().endswith('.exe'):
                                            icon = self.provider.icon(QFileInfo(icon_path))
                                        else:
                                            icon = QIcon(icon_path)
                                        break
                    except Exception:
                        pass
                        
                if icon is None:
                    icon = self.provider.icon(info)
                    
                if icon and not icon.isNull():
                    self.iconReady.emit(path, icon)
                    
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Icon fetch error for {path}: {e}")

    def queue_path(self, path):
        self.queue.put(path)
        
    def stop(self):
        self.running = False
        self.wait()


class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_cache = {}
        self.loading_paths = set()
        self.icon_thread = IconFetchThread()
        self.icon_thread.iconReady.connect(self.on_icon_ready)
        self.icon_thread.start()
        
        self.default_icon_provider = QFileIconProvider()

    def __del__(self):
        if hasattr(self, 'icon_thread'):
            self.icon_thread.stop()

    def on_icon_ready(self, path, icon):
        self.icon_cache[path] = icon
        if path in self.loading_paths:
            self.loading_paths.remove(path)
            
        # We need to trigger dataChanged for the index matching this path
        index = self.index(path)
        if index.isValid():
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])

    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid():
            return default_flags | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return default_flags

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole:
            file_info = self.fileInfo(index)
            path = file_info.absoluteFilePath()
            
            # If we already have the icon cached
            if path in self.icon_cache:
                return self.icon_cache[path]
                
            # If not cached and not loading, queue it
            if path not in self.loading_paths:
                self.loading_paths.add(path)
                self.icon_thread.queue_path(path)
                
            # Return a default icon immediately to not block UI
            return self.default_icon_provider.icon(QFileIconProvider.IconType.File)

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            file_info = self.fileInfo(index)
            name = file_info.fileName()
            if name:
                return os.path.splitext(name)[0]
                
        return super().data(index, role)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            file_info = self.fileInfo(index)
            old_path = file_info.absoluteFilePath()
            ext = file_info.suffix()
            
            new_base = str(value).strip()
            if not new_base or new_base == file_info.completeBaseName():
                return False
                
            new_name = f"{new_base}.{ext}" if ext and file_info.isFile() else new_base
            new_path = os.path.join(file_info.absolutePath(), new_name)
            
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    if old_path in self.icon_cache:
                        self.icon_cache[new_path] = self.icon_cache.pop(old_path)
                    return True 
                except Exception as e:
                    print(f"Ошибка переименования: {e}")
                    return False
            return True
        return super().setData(index, value, role)
