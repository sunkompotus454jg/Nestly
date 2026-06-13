import os
import ctypes
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QMenu,
                             QApplication, QSizePolicy, QMessageBox, QDialog, QListView)
from PyQt6.QtGui import QCursor, QColor, QDesktopServices
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QRect, QUrl, QItemSelectionModel

from core.themes import qss, THEMES
from ui.widgets import VectorSearchButton, CustomThemeDialog, ThemeMenu, ResizeHandle, BORDER_RADIUS
from ui.file_model import CustomFileSystemModel, CustomIconProvider
from ui.list_view import CustomListView

HEADER_HEIGHT = 35 

class FenceInstance(QWidget):
    @pyqtProperty(int)
    def current_body_height(self):
        return self.body_frame.maximumHeight()

    @current_body_height.setter
    def current_body_height(self, value):
        self.body_frame.setMinimumHeight(value)
        self.body_frame.setMaximumHeight(value)
        self.setFixedHeight(HEADER_HEIGHT + value)
        
    def __init__(self, config, ui_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.config = config
        
        self.id = config.get("id", "default")
        self.title = config.get("title", "Новая Сетка") 
        
        raw_path = config.get("path", "")
        self.target_path = os.path.abspath(raw_path) if raw_path else os.getcwd()
        
        self.current_theme = config.get("theme", "Blue")
        self.is_locked = config.get("locked", False)
        
        os.makedirs(self.target_path, exist_ok=True)

        self.start_width = config.get("width", 500)
        self.full_height = config.get("height", 600)
        start_x = config.get("x", 100)
        start_y = config.get("y", 100)

        screen = QApplication.primaryScreen().availableGeometry()
        if start_x < screen.left() or start_x > screen.right() - 50:
            start_x = screen.left() + 50
        if start_y < screen.top() or start_y > screen.bottom() - HEADER_HEIGHT:
            start_y = screen.top() + 50

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAcceptDrops(False) 
        
        self.setFixedWidth(self.start_width)
        self.setFixedHeight(HEADER_HEIGHT)
        self.move(start_x, start_y)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(HEADER_HEIGHT)
        self.header_frame.setObjectName("HeaderFrame")
        
        h_layout = QHBoxLayout(self.header_frame)
        h_layout.setContentsMargins(15, 0, 10, 0) 
        h_layout.setSpacing(0)
        
        self.title_edit = QLineEdit(self.title)
        self.title_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_edit.setReadOnly(True)
        self.title_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.title_edit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        self.search_btn = VectorSearchButton(self)
        self.search_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.search_btn.clicked.connect(self.toggle_search)

        dummy = QWidget()
        dummy.setFixedSize(self.search_btn.width(), self.search_btn.height())
        dummy.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        h_layout.addWidget(dummy)
        h_layout.addWidget(self.title_edit, 1) 
        h_layout.addWidget(self.search_btn)

        self.body_frame = QFrame()
        self.body_frame.setObjectName("BodyFrame")
        self.body_frame.setMinimumHeight(0)
        self.body_frame.setMaximumHeight(0)
        
        b_layout = QVBoxLayout(self.body_frame)
        b_layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.hide()
        
        self.model = CustomFileSystemModel()
        self.model.setRootPath(self.target_path)
        self.model.setReadOnly(False)
        self.model.setNameFilterDisables(False) 
        
        self.icon_provider = CustomIconProvider()
        self.model.setIconProvider(self.icon_provider)
        
        self.search_input.textChanged.connect(self.apply_search)
        
        self.list_view = CustomListView(self.target_path)
        self.list_view.setModel(self.model) 
        
        self.model.directoryLoaded.connect(self.on_directory_loaded)
        self.list_view.setRootIndex(self.model.index(self.target_path))

        self.list_view.doubleClicked.connect(self.open_file_double_click)
        self.list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
        
        b_layout.addWidget(self.search_input)
        b_layout.addWidget(self.list_view)

        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.body_frame)

        self.resizer = ResizeHandle(self, self)

        self.animation = QPropertyAnimation(self, b"current_body_height")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.drag_pos = None
        self.resizing = False
        self.is_expanded = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse)
        self.timer.start(50)

        self.header_frame.mousePressEvent = self.h_press
        self.header_frame.mouseMoveEvent = self.h_move
        self.header_frame.mouseReleaseEvent = self.h_release
        self.header_frame.mouseDoubleClickEvent = self.enable_edit 
        
        self.title_edit.returnPressed.connect(self.disable_edit)
        self.title_edit.editingFinished.connect(self.disable_edit)

        self.apply_theme(self.current_theme)
        self.show()

    def toggle_search(self):
        visible = not self.search_input.isVisible()
        if visible:
            self.search_input.setVisible(True)
            self.search_input.setFocus()
            self.anim = QPropertyAnimation(self.search_input, b"maximumWidth")
            self.anim.setDuration(200)
            self.anim.setStartValue(0)
            self.anim.setEndValue(120)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.start()
        else:
            self.anim = QPropertyAnimation(self.search_input, b"maximumWidth")
            self.anim.setDuration(200)
            self.anim.setStartValue(self.search_input.width())
            self.anim.setEndValue(0)
            self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
            self.anim.finished.connect(lambda: self.search_input.setVisible(False))
            self.anim.finished.connect(self.search_input.clear)
            self.anim.start()

    def apply_search(self, text):
        # Improve filter matching case-insensitively
        if text:
            self.model.setNameFilters([f"*{text}*"])
        else:
            self.model.setNameFilters([])

    def tr(self, key, **kwargs):
        if self.ui_manager and self.ui_manager.i18n:
            return self.ui_manager.i18n.tr(key, **kwargs)
        return key 

    def on_directory_loaded(self, path):
        if os.path.normpath(path) == os.path.normpath(self.target_path):
            self.list_view.setRootIndex(self.model.index(self.target_path))

    def toggle_search(self):
        if self.search_input.isVisible():
            self.search_input.hide()
            self.search_input.clear() 
        else:
            self.search_input.show()
            self.search_input.setFocus()

    def apply_theme(self, theme_key):
        all_themes = self.ui_manager.get_all_themes()
        if theme_key not in all_themes:
            theme_key = "Blue"
            
        self.current_theme = theme_key
        theme = all_themes[theme_key]
        
        self.ui_manager.update_fence_config(self.id, {"theme": theme_key})

        border_qss = qss(theme['border'])
        bg_qss = qss(theme['bg'])
        body_qss = qss(theme['body'])
        title_qss = qss(theme.get('title', theme['border']))

        self.title_edit.setStyleSheet(f"color: {title_qss}; font-family: 'Segoe UI Variable', 'Segoe UI'; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        self.resizer.setStyleSheet(f"background-color: transparent; border-bottom: 3px solid {border_qss}; border-right: 3px solid {border_qss}; border-bottom-right-radius: {BORDER_RADIUS}px;")
        
        self.search_btn.set_theme_color(theme.get('title', theme['border']))
        self.search_btn.update()
        
        self.search_input.setStyleSheet(f"QLineEdit {{ background: {bg_qss}; color: white; border: 1px solid {border_qss}; border-radius: 4px; padding: 4px; font-family: 'Segoe UI'; font-size: 12px; margin-bottom: 4px; }}")
        
        self.body_frame.setStyleSheet(f"QFrame#BodyFrame {{ background-color: {body_qss}; border: 2px solid {border_qss}; border-top: none; border-bottom-left-radius: {BORDER_RADIUS}px; border-bottom-right-radius: {BORDER_RADIUS}px; }} QListView {{ background: transparent; border: none; color: white; outline: none; selection-background-color: rgba(255,255,255, 30); }} QListView::item:selected {{ background: rgba(255,255,255, 30); border-radius: 5px; }} QListView QLineEdit {{ background: {bg_qss}; color: white; border: 1px solid {border_qss}; }}")
        
        self.set_header_style(expanded=self.is_expanded)

    def set_header_style(self, expanded):
        all_themes = self.ui_manager.get_all_themes()
        theme = all_themes.get(self.current_theme, THEMES["Blue"])
        
        border_qss = qss(theme['border'])
        bg_qss = qss(theme['bg'])
            
        if expanded:
            self.header_frame.setStyleSheet(f"QFrame#HeaderFrame {{ background-color: {bg_qss}; border: 2px solid {border_qss}; border-bottom: none; border-top-left-radius: {BORDER_RADIUS}px; border-top-right-radius: {BORDER_RADIUS}px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }}")
        else:
            self.header_frame.setStyleSheet(f"QFrame#HeaderFrame {{ background-color: {bg_qss}; border: 2px solid {border_qss}; border-radius: {BORDER_RADIUS}px; }}")

    def prompt_custom_theme(self, apply_globally=False):
        all_themes = self.ui_manager.get_all_themes()
        curr = all_themes.get(self.current_theme, THEMES["Blue"])
        
        default_title = curr.get('title', curr['border'])
        dialog = CustomThemeDialog(self, default_border=curr['border'], default_body=curr['body'], default_title=default_title)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme_data = dialog.get_theme_data()
            theme_id = self.ui_manager.add_custom_theme(theme_data)

            if apply_globally: self.ui_manager.apply_global_theme(theme_id)
            else: self.apply_theme(theme_id)

    def auto_fit_horizontal(self):
        if getattr(self, 'is_locked', False): return
        screen = QApplication.primaryScreen().availableGeometry()
        my_rect = self.geometry()
        
        min_x, max_x = screen.left(), screen.right()
        
        for fence in self.ui_manager.get_all_windows():
            if fence is self: continue
            other = fence.geometry()
            if not (my_rect.bottom() < other.top() or my_rect.top() > other.bottom()):
                if other.right() <= my_rect.left() and other.right() > min_x:
                    min_x = other.right()
                if other.left() >= my_rect.right() and other.left() < max_x:
                    max_x = other.left()
        
        new_width = max_x - min_x
        if new_width > 200:
            self.move(min_x, self.y())
            self.setFixedWidth(new_width)
            self.ui_manager.update_fence_config(self.id, {"x": min_x, "width": new_width})

    def toggle_lock(self):
        self.is_locked = not getattr(self, 'is_locked', False)
        self.ui_manager.update_fence_config(self.id, {"locked": self.is_locked})

    def show_context_menu(self, pos):
        index = self.list_view.indexAt(pos) 
        selected_indexes = self.list_view.selectionModel().selectedIndexes()
        
        if not index.isValid():
            self.list_view.clearSelection()
            selected_indexes = []
        elif index not in selected_indexes:
            self.list_view.selectionModel().clearSelection()
            self.list_view.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
            selected_indexes = [index]

        all_themes = self.ui_manager.get_all_themes()
        theme = all_themes.get(self.current_theme, THEMES["Blue"])
        
        c_menu_bg = QColor(theme['body'])
        if c_menu_bg.alpha() < 240: 
            c_menu_bg.setAlpha(240)
            
        menu_bg_qss = qss(c_menu_bg.name(QColor.NameFormat.HexArgb))
        border_qss = qss(theme['border'])
        
        menu_style = f"QMenu {{ background-color: {menu_bg_qss}; color: white; border: 1px solid {border_qss}; border-radius: 5px; font-family: 'Segoe UI'; font-size: 13px; }} QMenu::item {{ padding: 8px 20px; }} QMenu::item:selected {{ background-color: rgba(255, 255, 255, 20); }}"

        if selected_indexes:
            file_menu = QMenu(self)
            file_menu.setStyleSheet(menu_style)
            
            count = len(selected_indexes)
            
            if count == 1:
                open_action = file_menu.addAction("Открыть")
                run_admin_action = file_menu.addAction("Запуск от имени администратора")
                rename_action = file_menu.addAction("Переименовать")
                folder_action = file_menu.addAction("Показать в папке")
                prop_action = file_menu.addAction("Свойства") 
                file_menu.addSeparator()
                del_action = file_menu.addAction("Удалить файл")
            else:
                open_action = file_menu.addAction(f"Открыть ({count})")
                run_admin_action = None
                rename_action = None
                folder_action = None
                prop_action = None
                file_menu.addSeparator()
                del_action = file_menu.addAction(f"Удалить выбранные ({count})")

            action = file_menu.exec(self.list_view.mapToGlobal(pos))
            
            if action == open_action:
                for idx in selected_indexes:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(self.model.filePath(idx)))
                    
            elif action == run_admin_action and count == 1:
                path = self.model.filePath(index)
                ctypes.windll.shell32.ShellExecuteW(None, "runas", os.path.normpath(path), None, None, 1)
                    
            elif action == rename_action and count == 1:
                self.list_view.edit(index)
                        
            elif action == folder_action and count == 1:
                path = self.model.filePath(index)
                os.system(f'explorer /select,"{os.path.normpath(path)}"')
                
            elif action == prop_action and count == 1:
                path = self.model.filePath(index)
                ctypes.windll.shell32.ShellExecuteW(None, "properties", os.path.normpath(path), None, None, 1)
                
            elif action == del_action:
                msg = f"Вы уверены, что хотите удалить выбранные файлы ({count} шт.)?"
                if count == 1:
                    msg = f"Вы уверены, что хотите удалить '{self.model.fileName(index)}'?"
                    
                reply = QMessageBox.question(self, 'Подтверждение удаления', msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    for idx in selected_indexes:
                        self.model.remove(idx)
            return

        menu = QMenu(self)
        menu.setStyleSheet(menu_style)
        
        manage_menu = QMenu("Управление сетками", self)
        manage_menu.setStyleSheet(menu_style)
        
        for f in self.ui_manager.get_all_windows():
            fence_title = f.title_edit.text()
            f_menu = QMenu(fence_title, self)
            f_menu.setStyleSheet(menu_style)
            
            del_fence_action = f_menu.addAction("Удалить эту сетку")
            del_fence_action.triggered.connect(lambda checked, target_fence=f: target_fence.delete_fence())
            
            manage_menu.addMenu(f_menu)
            
        menu.addMenu(manage_menu)
        menu.addSeparator()
        
        lock_text = "Открепить сетку" if getattr(self, 'is_locked', False) else "Закрепить сетку"
        lock_action = menu.addAction(lock_text)
        lock_action.triggered.connect(self.toggle_lock)
        
        fit_action = menu.addAction("Заполнить свободное место")
        fit_action.triggered.connect(self.auto_fit_horizontal)
        
        search_action = menu.addAction("Поиск иконок")
        search_action.triggered.connect(self.toggle_search)
        menu.addSeparator()

        color_menu = ThemeMenu("Цвет этого окна", self.ui_manager)
        color_menu.setStyleSheet(menu_style)
        for key, data in all_themes.items():
            display_name = data["name"] + " (удалить)" if str(key).startswith("Custom_") else data["name"]
            action = color_menu.addAction(display_name)
            action.setData(key) 
            action.triggered.connect(lambda checked, k=key: self.apply_theme(k))
            
        color_menu.addSeparator()
        custom_action = color_menu.addAction("Создать свой пресет...")
        custom_action.triggered.connect(lambda: self.prompt_custom_theme(apply_globally=False))
        menu.addMenu(color_menu)

        global_color_menu = ThemeMenu("Цвет всех окон", self.ui_manager)
        global_color_menu.setStyleSheet(menu_style)
        for key, data in all_themes.items():
            display_name = data["name"] + " (удалить)" if str(key).startswith("Custom_") else data["name"]
            action = global_color_menu.addAction(display_name)
            action.setData(key)
            action.triggered.connect(lambda checked, k=key: self.ui_manager.apply_global_theme(k))
            
        global_color_menu.addSeparator()
        global_custom_action = global_color_menu.addAction("Создать свой пресет...")
        global_custom_action.triggered.connect(lambda: self.prompt_custom_theme(apply_globally=True))
        menu.addMenu(global_color_menu)

        menu.addSeparator()
        delete_action = menu.addAction("Удалить сетку")
        delete_action.triggered.connect(self.delete_fence)

        menu.exec(self.list_view.mapToGlobal(pos))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizer.move(self.width() - 20, self.height() - 20)

    def check_mouse(self):
        if self.title_edit.hasFocus() or self.search_input.hasFocus() or self.resizing or self.list_view.state() == QListView.State.EditingState: 
            return

        mouse = QCursor.pos()
        over_window = self.geometry().contains(mouse)

        if QApplication.activePopupWidget(): return

        if over_window and not self.is_expanded:
            self.is_expanded = True
            self.animation.stop()
            try: self.animation.finished.disconnect(self.on_collapse_finished)
            except: pass
            
            self.set_header_style(expanded=True)
            self.animation.setStartValue(self.current_body_height)
            self.animation.setEndValue(self.full_height)
            self.resizer.show()
            self.animation.start()

        elif not over_window and self.is_expanded:
            self.is_expanded = False
            self.animation.stop()
            self.resizer.hide()
            
            if self.search_input.isVisible():
                self.search_input.hide()
                self.search_input.clear()
            
            self.list_view.clearSelection()
            
            self.animation.setStartValue(self.current_body_height)
            self.animation.setEndValue(0)
            self.animation.finished.connect(self.on_collapse_finished)
            self.animation.start()

    def on_collapse_finished(self):
        try: self.animation.finished.disconnect(self.on_collapse_finished)
        except: pass
        if self.current_body_height == 0:
            self.set_header_style(expanded=False)

    def start_resizing(self, global_pos):
        if getattr(self, 'is_locked', False): return
        self.resizing = True
        self.resize_start_pos = global_pos
        self.start_width = self.width()
        self.start_height = self.full_height
        self.animation.stop()

    def do_resizing(self, global_pos):
        if not self.resizing: return
        delta = global_pos - self.resize_start_pos
        new_width = max(200, self.start_width + delta.x())
        new_height = max(100, self.start_height + delta.y())
        
        self.setFixedWidth(new_width)
        self.full_height = new_height
        self.current_body_height = new_height

    def stop_resizing(self):
        self.resizing = False
        self.ui_manager.update_fence_config(self.id, {"width": self.width(), "height": self.full_height})

    def delete_fence(self):
        self.ui_manager.delete_fence(self.id)
        # self.close() is called by the UIManager

    def snap_to_edges(self, new_pos):
        snap_dist = 20
        new_rect = QRect(new_pos.x(), new_pos.y(), self.width(), self.height())
        screen = QApplication.primaryScreen().availableGeometry()
        
        snapped_x = False; snapped_y = False
        
        for fence in self.ui_manager.get_all_windows():
            if fence is self: continue
            other = fence.geometry()
            
            if not snapped_x:
                if abs(new_rect.left() - other.right()) < snap_dist: new_pos.setX(other.right()); snapped_x = True
                elif abs(new_rect.right() - other.left()) < snap_dist: new_pos.setX(other.left() - self.width()); snapped_x = True
                elif abs(new_rect.left() - other.left()) < snap_dist: new_pos.setX(other.left()); snapped_x = True
                    
            if not snapped_y:
                if abs(new_rect.top() - other.bottom()) < snap_dist: new_pos.setY(other.bottom()); snapped_y = True
                elif abs(new_rect.bottom() - other.top()) < snap_dist: new_pos.setY(other.top() - self.height()); snapped_y = True
                elif abs(new_rect.top() - other.top()) < snap_dist: new_pos.setY(other.top()); snapped_y = True

        if not snapped_x:
            if abs(new_rect.left() - screen.left()) < snap_dist: new_pos.setX(screen.left())
            elif abs(new_rect.right() - screen.right()) < snap_dist: new_pos.setX(screen.right() - self.width())
                
        if not snapped_y:
            if abs(new_rect.top() - screen.top()) < snap_dist: new_pos.setY(screen.top())
            elif abs(new_rect.bottom() - screen.bottom()) < snap_dist: new_pos.setY(screen.bottom() - self.height())

        if new_pos.y() < screen.top():
            new_pos.setY(screen.top())
        if new_pos.x() < screen.left():
            new_pos.setX(screen.left())
        if new_pos.x() + self.width() > screen.right():
            new_pos.setX(screen.right() - self.width())
        if new_pos.y() + HEADER_HEIGHT > screen.bottom():
            new_pos.setY(screen.bottom() - HEADER_HEIGHT)

        return new_pos

    def h_press(self, event):
        if getattr(self, 'is_locked', False): return 
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def h_move(self, event):
        if getattr(self, 'is_locked', False): return 
        if event.buttons() == Qt.MouseButton.LeftButton and not self.title_edit.hasFocus() and self.drag_pos:
            raw_new_pos = event.globalPosition().toPoint() - self.drag_pos
            snapped_pos = self.snap_to_edges(raw_new_pos)
            self.move(snapped_pos)

    def h_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.drag_pos = None
            self.ui_manager.update_fence_config(self.id, {"x": self.x(), "y": self.y()})

    def enable_edit(self, event):
        self.title_edit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.title_edit.setReadOnly(False)
        self.title_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.title_edit.setFocus()
        self.title_edit.selectAll()

    def disable_edit(self):
        self.title_edit.setReadOnly(True)
        self.title_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.title_edit.clearFocus()
        self.title_edit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.ui_manager.update_fence_config(self.id, {"title": self.title_edit.text()})

    def open_file_double_click(self, index):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.model.filePath(index)))
