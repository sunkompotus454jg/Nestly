from PyQt6.QtWidgets import QPushButton, QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QColorDialog, QMenu, QWidget
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtCore import Qt, QPoint

from core.themes import qss

# Default border radius across app
BORDER_RADIUS = 5

class VectorSearchButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(26, 26) 
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Поиск")
        self._current_color = QColor("white")
        self._base_color = QColor("white")
        self._hover_color = QColor("white")
        self._pressed = False

    def set_theme_color(self, color_str):
        self._base_color = QColor(color_str)
        if not self.underMouse():
            self._current_color = self._base_color
        self.update()

    def enterEvent(self, event):
        self._current_color = self._hover_color
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._current_color = self._base_color
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        offset = 1 if self._pressed else 0
        
        pen = QPen(self._current_color)
        pen.setWidthF(1.3) 
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        w = self.width()
        h = self.height()
        
        cx = w / 2 + offset
        cy = h / 2 + offset
        r = 5 
        
        draw_cx = cx - 2
        painter.drawEllipse(QPoint(int(draw_cx), int(cy)), r, r)
        
        handle_start_x = draw_cx + r * 0.707
        handle_start_y = cy + r * 0.707
        handle_end_x = draw_cx + r * 1.5 
        handle_end_y = cy + r * 1.5
        
        painter.drawLine(QPoint(int(handle_start_x), int(handle_start_y)), 
                         QPoint(int(handle_end_x), int(handle_end_y)))

class CustomThemeDialog(QDialog):
    def __init__(self, parent=None, default_border="#00d4ff", default_body="#1a1a21", default_title="#ffffff"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 420)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame(self)
        self.container.setObjectName("MainContainer")
        self.layout.addWidget(self.container)
        
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(10)
        
        c_layout.addWidget(QLabel("Название пресета:"))
        self.name_input = QLineEdit("Мой цвет")
        c_layout.addWidget(self.name_input)
        
        c_layout.addWidget(QLabel("Цвет контура (HEX):"))
        border_layout = QHBoxLayout()
        self.border_input = QLineEdit(default_border)
        self.border_btn = QPushButton("...")
        self.border_btn.setFixedSize(32, 30)
        border_layout.addWidget(self.border_input)
        border_layout.addWidget(self.border_btn)
        c_layout.addLayout(border_layout)

        c_layout.addWidget(QLabel("Цвет текста заголовка (HEX):"))
        title_layout = QHBoxLayout()
        self.title_input = QLineEdit(default_title)
        self.title_btn = QPushButton("...")
        self.title_btn.setFixedSize(32, 30)
        title_layout.addWidget(self.title_input)
        title_layout.addWidget(self.title_btn)
        c_layout.addLayout(title_layout)
        
        c_layout.addWidget(QLabel("Основной цвет фона (HEX):"))
        body_layout = QHBoxLayout()
        self.body_input = QLineEdit(default_body)
        self.body_btn = QPushButton("...")
        self.body_btn.setFixedSize(32, 30)
        body_layout.addWidget(self.body_input)
        body_layout.addWidget(self.body_btn)
        c_layout.addLayout(body_layout)

        c_layout.addWidget(QLabel("Превью:"))
        self.preview_frame = QFrame()
        self.preview_frame.setFixedHeight(40)
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_label = QLabel("Моя Сетка")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        c_layout.addWidget(self.preview_frame)

        c_layout.addSpacing(10)
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_ok = QPushButton("Сохранить")
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        c_layout.addLayout(btn_layout)
        
        self.border_btn.clicked.connect(lambda: self.pick_color(self.border_input))
        self.title_btn.clicked.connect(lambda: self.pick_color(self.title_input))
        self.body_btn.clicked.connect(lambda: self.pick_color(self.body_input))
        
        self.border_input.textChanged.connect(self.update_preview)
        self.title_input.textChanged.connect(self.update_preview)
        self.body_input.textChanged.connect(self.update_preview)
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.drag_pos = None
        self.update_preview() 
        
    def pick_color(self, line_edit):
        color = QColorDialog.getColor(QColor(line_edit.text()), self, "Выберите цвет", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            line_edit.setText(color.name(QColor.NameFormat.HexArgb) if color.alpha() < 255 else color.name())

    def update_preview(self):
        border = self.border_input.text().strip()
        body = self.body_input.text().strip()
        title = self.title_input.text().strip()
        
        border_qss = qss(border)
        body_qss = qss(body)
        title_qss = qss(title)
        
        self.preview_frame.setStyleSheet(f"QFrame {{ background-color: {body_qss}; border: 2px solid {border_qss}; border-radius: {BORDER_RADIUS}px; }}")
        self.preview_label.setStyleSheet(f"QLabel {{ color: {title_qss}; font-weight: bold; font-family: 'Segoe UI Variable', 'Segoe UI'; font-size: 14px; border: none; background: transparent; }}")
        
        c_border = QColor(border)
        preview_border = border_qss if c_border.isValid() and c_border.alpha() > 10 else "rgba(0, 212, 255, 1.0)"
        
        self.container.setStyleSheet(f"""
            QFrame#MainContainer {{ background-color: #1a1a21; border: 2px solid {preview_border}; border-radius: {BORDER_RADIUS}px; }}
            QLabel {{ color: white; border: none; font-family: 'Segoe UI'; font-size: 13px; }}
            QLineEdit {{ background-color: #141419; color: white; border: 1px solid #555; border-radius: 3px; padding: 6px; font-family: 'Segoe UI'; font-size: 13px; }}
            QPushButton {{ background-color: #141419; color: white; border: 1px solid #555; border-radius: 4px; padding: 6px 15px; font-family: 'Segoe UI'; }}
            QPushButton:hover {{ background-color: {preview_border}; color: black; border: 1px solid {preview_border}; }}
        """)

    def get_theme_data(self):
        border = self.border_input.text().strip()
        body = self.body_input.text().strip()
        title = self.title_input.text().strip()
        name = self.name_input.text().strip() or "Мой цвет"
        
        c_border = QColor(border) if QColor(border).isValid() else QColor("#00d4ff")
        c_body = QColor(body) if QColor(body).isValid() else QColor("#1a1a21")
        c_title = QColor(title) if QColor(title).isValid() else QColor("#ffffff")
        
        if c_border.alpha() < 3: c_border.setAlpha(3)
        if c_body.alpha() < 3: c_body.setAlpha(3)
        if c_title.alpha() < 3: c_title.setAlpha(3)
        
        border_hex = c_border.name(QColor.NameFormat.HexArgb)
        body_hex = c_body.name(QColor.NameFormat.HexArgb)
        title_hex = c_title.name(QColor.NameFormat.HexArgb)
        
        if c_body.alpha() <= 10:
            bg_hex = body_hex
        else:
            c_bg = c_body.darker(110)
            bg_hex = c_bg.name(QColor.NameFormat.HexArgb)
            
        return {"name": name, "border": border_hex, "bg": bg_hex, "body": body_hex, "title": title_hex}

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos: self.move(event.globalPosition().toPoint() - self.drag_pos)
    def mouseReleaseEvent(self, event):
        self.drag_pos = None

class ThemeMenu(QMenu):
    def __init__(self, title, parent_window):
        super().__init__(title, parent_window)
        self.parent_window = parent_window 
        
    def mouseReleaseEvent(self, event):
        action = self.actionAt(event.pos())
        if action and event.button() == Qt.MouseButton.RightButton:
            theme_key = action.data()
            if theme_key and str(theme_key).startswith("Custom_"):
                # We need to call a method on the app to handle this
                if hasattr(self.parent_window, "remove_custom_theme"):
                    self.parent_window.remove_custom_theme(theme_key)
                self.removeAction(action)
                self.close() 
                return
        super().mouseReleaseEvent(event)

class ResizeHandle(QWidget):
    def __init__(self, parent_widget, instance):
        super().__init__(parent_widget)
        self.instance = instance
        self.setFixedSize(20, 20)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.instance.start_resizing(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.instance.do_resizing(event.globalPosition().toPoint())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.instance.stop_resizing()
            event.accept()
