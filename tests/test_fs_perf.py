import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QListView
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QFileSystemModel

class TestWindow(QWidget):
    def __init__(self, target_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: rgba(50, 50, 50, 200); border-radius: 10px;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.body_frame = QFrame()
        self.body_frame.setFixedHeight(500)
        
        b_layout = QVBoxLayout(self.body_frame)
        self.list_view = QListView()
        self.list_view.setViewMode(QListView.ViewMode.IconMode)
        self.list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.list_view.setLayoutMode(QListView.LayoutMode.Batched)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(target_path)
        self.model.directoryLoaded.connect(self.on_dir_loaded)
        self.list_view.setModel(self.model)
        self.list_view.setRootIndex(self.model.index(target_path))
        
        b_layout.addWidget(self.list_view)
        self.layout.addWidget(self.body_frame)
        
        self._anim_value = 50
        self.setFixedHeight(self._anim_value)

        self.animation = QPropertyAnimation(self, b"anim_prop")
        self.animation.setDuration(300)
        self.animation.setStartValue(50)
        self.animation.setEndValue(500)
        self.animation.finished.connect(self.close)
        
        self.start_time = 0
        self.frames = 0
        
    @pyqtProperty(int)
    def anim_prop(self):
        return self._anim_value
        
    @anim_prop.setter
    def anim_prop(self, value):
        self._anim_value = value
        self.frames += 1
        self.setFixedHeight(value)
        
    def on_dir_loaded(self, path):
        self.start_time = time.time()
        self.animation.start()
        
    def showEvent(self, event):
        super().showEvent(event)
        
    def closeEvent(self, event):
        elapsed = time.time() - self.start_time
        print(f"Finished in {elapsed:.3f}s with {self.frames} frames. FPS = {self.frames/elapsed:.1f}")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # create dummy files
    import os
    os.makedirs("test_grid", exist_ok=True)
    for i in range(10):
        with open(f"test_grid/dummy{i}.txt", "w") as f:
            f.write("test")
    w = TestWindow(os.path.abspath("test_grid"))
    w.show()
    app.exec()
