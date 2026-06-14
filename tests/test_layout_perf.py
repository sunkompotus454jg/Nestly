import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QListView, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty

class BodyFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.resize_count = 0
    def resizeEvent(self, event):
        self.resize_count += 1
        super().resizeEvent(event)

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(300, 50)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.header = QLabel("Header")
        self.header.setFixedHeight(50)
        self.layout.addWidget(self.header)
        
        self.body_frame = BodyFrame()
        self.body_frame.setFixedHeight(500)
        self.layout.addWidget(self.body_frame)
        
        self._anim_value = 0
        self.animation = QPropertyAnimation(self, b"anim_prop")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(500)
        self.animation.finished.connect(self.close)
        
    @pyqtProperty(int)
    def anim_prop(self):
        return self._anim_value
        
    @anim_prop.setter
    def anim_prop(self, value):
        self._anim_value = value
        self.setFixedHeight(50 + value)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.animation.start()

    def closeEvent(self, event):
        print(f"BodyFrame resized {self.body_frame.resize_count} times")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TestWindow()
    w.show()
    app.exec()
