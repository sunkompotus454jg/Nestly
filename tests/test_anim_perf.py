import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QRegion

class TestWindow(QWidget):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedSize(300, 500)
        self.setStyleSheet("background-color: rgba(50, 50, 50, 200); border-radius: 10px;")
        
        self._anim_value = 50
        
        if mode == "resize":
            self.setFixedHeight(self._anim_value)
        elif mode == "mask":
            self.setMask(QRegion(0, 0, 300, self._anim_value))

        self.animation = QPropertyAnimation(self, b"anim_prop")
        self.animation.setDuration(500)
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
        if self.mode == "resize":
            self.setFixedHeight(value)
        elif self.mode == "mask":
            self.setMask(QRegion(0, 0, 300, value))
            
    def showEvent(self, event):
        super().showEvent(event)
        self.start_time = time.time()
        self.animation.start()
        
    def closeEvent(self, event):
        elapsed = time.time() - self.start_time
        print(f"[{self.mode}] Finished in {elapsed:.3f}s with {self.frames} frames. FPS = {self.frames/elapsed:.1f}")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    print("Testing RESIZE mode...")
    w1 = TestWindow("resize")
    w1.show()
    app.exec()
    
    print("Testing MASK mode...")
    w2 = TestWindow("mask")
    w2.show()
    app.exec()
