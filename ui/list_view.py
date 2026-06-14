import os
import shutil
import ctypes
from PyQt6.QtWidgets import QListView
from PyQt6.QtCore import Qt, QSize

class CustomListView(QListView):
    def __init__(self, target_path, parent=None):
        super().__init__(parent)
        self.target_path = target_path
        
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setIconSize(QSize(32, 32)) 
        self.setGridSize(QSize(90, 80)) 
        self.setUniformItemSizes(True)  
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setLayoutMode(QListView.LayoutMode.Batched)  # рендерит иконки пачками, не блокирует UI
        self.setBatchSize(20)  # по 20 иконок за раз
        self.setWordWrap(False) 
        
        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.setSelectionRectVisible(True) 
        self.setEditTriggers(QListView.EditTrigger.EditKeyPressed | QListView.EditTrigger.SelectedClicked)
        
        # Restore Movement.Snap to allow drag and drop. 
        # The main lag was fixed by optimizing the animation in fence_window.py
        self.setMovement(QListView.Movement.Snap)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        
        # Pixel-smooth scrolling
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and event.source() != self:
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls() and event.source() != self:
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            if event.source() == self:
                super().dropEvent(event)
            else:
                event.setDropAction(Qt.DropAction.MoveAction)
                event.accept()
                files_moved = False
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        src_path = url.toLocalFile()
                        file_name = os.path.basename(src_path)
                        dst_path = os.path.join(self.target_path, file_name)
                        try:
                            if src_path != dst_path: 
                                shutil.move(src_path, dst_path)
                                files_moved = True
                        except Exception as e: 
                            print(f"Ошибка: {e}")
                            
                if files_moved:
                    try:
                        desktop_dir = os.path.expanduser("~\\Desktop")
                        ctypes.windll.shell32.SHChangeNotify(0x00001000, 0x0005, desktop_dir, None)
                    except Exception as e:
                        pass
        else:
            super().dropEvent(event)
