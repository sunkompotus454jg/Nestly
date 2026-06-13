import os
from PyQt6.QtGui import QFileSystemModel, QIcon
from PyQt6.QtCore import Qt, QFileInfo

try:
    from PyQt6.QtWidgets import QFileIconProvider
except ImportError:
    try:
        from PyQt6.QtGui import QFileIconProvider
    except ImportError:
        from PyQt6.QtGui import QAbstractFileIconProvider as QFileIconProvider

class CustomIconProvider(QFileIconProvider):
    def icon(self, info):
        if isinstance(info, QFileInfo):
            path = info.absoluteFilePath()
            if path.lower().endswith('.url'):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line.lower().startswith("iconfile="):
                                icon_path = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if os.path.exists(icon_path):
                                    if icon_path.lower().endswith('.exe'):
                                        return super().icon(QFileInfo(icon_path))
                                    else:
                                        return QIcon(icon_path)
                except Exception:
                    pass
        return super().icon(info)


class CustomFileSystemModel(QFileSystemModel):
    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid():
            return default_flags | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return default_flags

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
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
                    return True 
                except Exception as e:
                    print(f"Ошибка переименования: {e}")
                    return False
            return True
        return super().setData(index, value, role)
