import os
import queue
from PyQt6.QtGui import QFileSystemModel, QIcon
from PyQt6.QtCore import Qt, QFileInfo, QThread, pyqtSignal, QPersistentModelIndex, QTimer, QSortFilterProxyModel

try:
    from PyQt6.QtWidgets import QFileIconProvider
except ImportError:
    try:
        from PyQt6.QtGui import QFileIconProvider
    except ImportError:
        from PyQt6.QtGui import QAbstractFileIconProvider as QFileIconProvider


# ── Global extension-based icon cache ──────────────────────────
# QFileIconProvider.icon(QFileInfo) calls Windows Shell API (SHGetFileInfo)
# which takes 50-200ms per call.  For non-.url files the icon depends only
# on the extension, so we call it ONCE per extension and reuse.
_EXT_ICON_CACHE = {}          # ".lnk" -> QIcon, ".txt" -> QIcon, …
_EXT_ICON_PROVIDER = None     # lazy-init QFileIconProvider


def _icon_cache_key(file_info: QFileInfo):
    """Compute the _EXT_ICON_CACHE key for a file, or None if this file
    type isn't extension-cacheable (.lnk/.exe/.ico/.url use per-path caching
    via icon_cache instead)."""
    ext = file_info.suffix().lower()
    is_dir = file_info.isDir()

    if is_dir:
        return "__dir__"
    elif ext:
        if ext in ('lnk', 'exe', 'ico', 'url'):
            return None
        return ext
    else:
        return "__noext__"


def _get_icon_by_extension(file_info: QFileInfo) -> QIcon:
    """Return icon for a file based on its extension (cached).
    
    Falls back to a generic File icon if the provider returns null.
    First call per extension triggers a Shell API call; subsequent calls
    are instant dictionary lookups.
    """
    global _EXT_ICON_PROVIDER
    if _EXT_ICON_PROVIDER is None:
        _EXT_ICON_PROVIDER = QFileIconProvider()

    key = _icon_cache_key(file_info)
    if key is None:
        # .lnk/.exe/.ico/.url — cached per-path elsewhere
        key = file_info.absoluteFilePath()

    cached = _EXT_ICON_CACHE.get(key)
    if cached is not None:
        return cached

    icon = _EXT_ICON_PROVIDER.icon(file_info)
    if icon.isNull():
        icon = _EXT_ICON_PROVIDER.icon(
            QFileIconProvider.IconType.Folder if is_dir else QFileIconProvider.IconType.File
        )
    _EXT_ICON_CACHE[key] = icon
    return icon


# ── Lightweight generic fallback ───────────────────────────────
_GENERIC_FILE_ICON = None

def _get_generic_file_icon() -> QIcon:
    """Return a cheap generic file icon (no Shell API call)."""
    global _GENERIC_FILE_ICON, _EXT_ICON_PROVIDER
    if _GENERIC_FILE_ICON is not None:
        return _GENERIC_FILE_ICON
    if _EXT_ICON_PROVIDER is None:
        _EXT_ICON_PROVIDER = QFileIconProvider()
    _GENERIC_FILE_ICON = _EXT_ICON_PROVIDER.icon(QFileIconProvider.IconType.File)
    return _GENERIC_FILE_ICON


class IconFetchThread(QThread):
    iconReady = pyqtSignal(str, QIcon, str)

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.running = True
        self.provider = QFileIconProvider()

    def run(self):
        import ctypes
        try:
            ctypes.windll.ole32.CoInitialize(None)
        except Exception:
            pass
            
        try:
            while self.running:
                try:
                    path = self.queue.get(timeout=0.1)
                    if not self.running:
                        break
                    
                    # Resolve icon
                    icon = None
                    info = QFileInfo(path)
                    resolved_path = ""
                    
                    if path.lower().endswith('.url'):
                        try:
                            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                                for line in f:
                                    line = line.strip()
                                    if line.lower().startswith("iconfile="):
                                        icon_path = line.split("=", 1)[1].strip().strip('"').strip("'")
                                        if os.path.exists(icon_path):
                                            resolved_path = icon_path
                                            if icon_path.lower().endswith('.exe'):
                                                icon = self.provider.icon(QFileInfo(icon_path))
                                            else:
                                                icon = QIcon(icon_path)
                                            break
                        except Exception:
                            pass
                    else:
                        icon = self.provider.icon(info)
                            
                    if icon and not icon.isNull():
                        self.iconReady.emit(path, icon, resolved_path)
                    else:
                        self.iconReady.emit(path, QIcon(), "") # Emit empty icon if not found
                        
                    self.queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Icon fetch error for {path}: {e}")
        finally:
            try:
                ctypes.windll.ole32.CoUninitialize()
            except Exception:
                pass

    def queue_path(self, path):
        self.queue.put(path)
        
    def stop(self):
        self.running = False
        self.wait()


class CustomFileSystemModel(QFileSystemModel):
    iconCacheUpdated = pyqtSignal(str, str)
    # Emitted when ALL icons for the root directory have been resolved
    # (either from cache or from the background thread).
    allIconsReady = pyqtSignal()
    
    def __init__(self, parent=None, icon_cache_persist=None):
        super().__init__(parent)
        self.icon_cache = {}
        self.icon_cache_persist = icon_cache_persist if icon_cache_persist else {}
        self.loading_paths = set()
        self.icon_thread = IconFetchThread()
        self.icon_thread.iconReady.connect(self.on_icon_ready)
        self.icon_thread.start()
        
        self._pending_icons = set()
        self._flush_timer = QTimer(self)
        self._flush_timer.setInterval(200)  # 200ms - меньше нагрузки при массовой загрузке иконок
        self._flush_timer.timeout.connect(self._flush_icons)
        self._flush_timer.start()
        
        # Track whether initial icon preload is complete
        self._preload_pending = 0
        self._preloaded = False

        # Maps a representative file path queued for *extension* icon
        # resolution -> the _EXT_ICON_CACHE key it should populate.
        # Used so SHGetFileInfo for "new" extensions runs on the
        # background icon thread instead of synchronously inside data()
        # the first time the view is laid out.
        self._ext_preload_paths = {}
        self._preload_root = None

    def __del__(self):
        if hasattr(self, 'icon_thread'):
            self.icon_thread.stop()

    def preload_icons(self, directory_path):
        """Pre-load icons for all .url files in the given directory.
        
        Called once after directoryLoaded.  For each .url file:
        1. If persisted icon exists on disk — load it into icon_cache immediately (sync, cheap).
        2. Otherwise — queue it for background thread resolution.
        
        This ensures that by the time the user hovers over the fence,
        most/all icons are already in memory.
        """
        self._preloaded = False
        self._preload_pending = 0
        
        try:
            entries = os.listdir(directory_path)
        except OSError:
            self._preloaded = True
            self.allIconsReady.emit()
            return
        
        urls_to_fetch = []
        
        for name in entries:
            if not name.lower().endswith(('.url', '.lnk', '.exe', '.ico')):
                continue
                
            full_path = os.path.join(directory_path, name)
            
            # Already cached?
            if full_path in self.icon_cache:
                continue
            
            # Try persisted path first (instant, no Shell call)
            persisted = self.icon_cache_persist.get(full_path)
            if persisted and os.path.exists(persisted):
                if persisted.lower().endswith('.exe'):
                    # Queue it to the background thread instead of blocking
                    if full_path not in self.loading_paths:
                        self.loading_paths.add(full_path)
                        self.icon_thread.queue_path(full_path)
                    continue
                else:
                    icon = QIcon(persisted)
                if not icon.isNull():
                    self.icon_cache[full_path] = icon.pixmap(32, 32)
                    continue
            
            # Need background resolution
            if full_path not in self.loading_paths:
                self.loading_paths.add(full_path)
                urls_to_fetch.append(full_path)
        
        # ── Pre-warm per-extension icon cache for regular files ──
        # Avoids a synchronous 50-200ms SHGetFileInfo call on the UI
        # thread the first time the view lays out items with a new
        # extension — this is what causes the freeze on first expand
        # of fences that contain many different file types.
        self._preload_root = directory_path
        seen_keys = set()
        ext_paths_to_fetch = []

        for name in entries:
            if name.lower().endswith(('.url', '.lnk', '.exe', '.ico')):
                continue

            full_path = os.path.join(directory_path, name)
            file_info = QFileInfo(full_path)
            key = _icon_cache_key(file_info)

            if key in _EXT_ICON_CACHE or key in seen_keys:
                continue
            seen_keys.add(key)

            if full_path not in self.loading_paths:
                self.loading_paths.add(full_path)
                self._ext_preload_paths[full_path] = key
                ext_paths_to_fetch.append(full_path)

        self._preload_pending = len(urls_to_fetch) + len(ext_paths_to_fetch)
        
        if self._preload_pending == 0:
            self._preloaded = True
            self.allIconsReady.emit()
        else:
            for p in urls_to_fetch:
                self.icon_thread.queue_path(p)
            for p in ext_paths_to_fetch:
                self.icon_thread.queue_path(p)

    def on_icon_ready(self, path, icon, resolved_path):
        if path in self.loading_paths:
            self.loading_paths.remove(path)

        if path in self._ext_preload_paths:
            # This was a representative file queued purely to pre-warm
            # _EXT_ICON_CACHE for its extension — store it under the
            # extension key, then refresh any visible items so they
            # pick up the new icon.
            ext_key = self._ext_preload_paths.pop(path)
            _EXT_ICON_CACHE[ext_key] = icon if not icon.isNull() else _get_generic_file_icon()

            if self._preload_root:
                root_idx = self.index(self._preload_root)
                row_count = self.rowCount(root_idx)
                if row_count > 0:
                    top = self.index(0, 0, root_idx)
                    bottom = self.index(row_count - 1, 0, root_idx)
                    self.dataChanged.emit(top, bottom, [Qt.ItemDataRole.DecorationRole])
        else:
            if icon.isNull():
                self.icon_cache[path] = False
            else:
                self.icon_cache[path] = icon.pixmap(32, 32)
                if resolved_path:
                    self.icon_cache_persist[path] = resolved_path
                    self.iconCacheUpdated.emit(path, resolved_path)

            self._pending_icons.add(path)
        
        # Track preload completion
        if self._preload_pending > 0:
            self._preload_pending -= 1
            if self._preload_pending == 0:
                self._preloaded = True
                self.allIconsReady.emit()

    def _flush_icons(self):
        if not self._pending_icons:
            return
        paths = list(self._pending_icons)
        self._pending_icons.clear()
        for path in paths:
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
            
            if path.lower().endswith(('.url', '.lnk', '.exe', '.ico')):
                cached = self.icon_cache.get(path, None)
                if cached is False:
                    # Failed to resolve — use generic icon (cheap, no Shell call)
                    return _get_generic_file_icon()
                elif cached is not None:
                    return cached
                    
                persisted_path = self.icon_cache_persist.get(path)
                if persisted_path and os.path.exists(persisted_path):
                    if persisted_path.lower().endswith('.exe'):
                        # Do NOT extract synchronously. Queue it.
                        if path not in self.loading_paths:
                            self.loading_paths.add(path)
                            self.icon_thread.queue_path(path)
                        return _get_generic_file_icon()
                    else:
                        icon = QIcon(persisted_path)
                    if not icon.isNull():
                        pixmap = icon.pixmap(32, 32)
                        self.icon_cache[path] = pixmap
                        return pixmap
                    
                # Queue for background loading if not already queued
                if path not in self.loading_paths:
                    self.loading_paths.add(path)
                    self.icon_thread.queue_path(path)
                    
                # Return generic icon while loading (NO Shell API call)
                return _get_generic_file_icon()
                
            # Non-.url files: use extension-based cache (one Shell call per ext)
            return _get_icon_by_extension(file_info)

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

class CustomOrderProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, custom_order=None):
        super().__init__(parent)
        self.custom_order = custom_order if custom_order else []
        self._order_dict = {name: idx for idx, name in enumerate(self.custom_order)}

    def set_custom_order(self, order):
        self.custom_order = order
        self._order_dict = {name: idx for idx, name in enumerate(self.custom_order)}
        self.invalidate()

    def append_if_missing(self, name):
        if name not in self.custom_order:
            self.custom_order.append(name)
            self._order_dict[name] = len(self.custom_order) - 1
            return True
        return False

    def lessThan(self, source_left, source_right):
        model = self.sourceModel()
        left_name = model.fileName(source_left)
        right_name = model.fileName(source_right)
        
        left_idx = self._order_dict.get(left_name, -1)
        right_idx = self._order_dict.get(right_name, -1)
        
        # Both in custom_order: sort by custom position
        if left_idx >= 0 and right_idx >= 0:
            return left_idx < right_idx
        
        # One in custom_order, one not: custom_order items first
        if left_idx >= 0 and right_idx < 0:
            return True
        if left_idx < 0 and right_idx >= 0:
            return False
            
        # Neither in custom_order: preserve native row order (not alphabetical)
        return source_left.row() < source_right.row()