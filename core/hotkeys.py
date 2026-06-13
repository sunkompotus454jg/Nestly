import ctypes
import ctypes.wintypes
from PyQt6.QtCore import QAbstractNativeEventFilter, QEvent, QObject

class GlobalHotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.registered = False
        
        # Register Alt+Shift+D (Alt=0x0001, Shift=0x0004) VK_D=0x44
        # Since the user asked for Win+D-like, let's try Alt+Shift+D to avoid OS conflicts.
        # Hotkey ID = 1
        MOD_ALT = 0x0001
        MOD_SHIFT = 0x0004
        VK_D = 0x44
        
        self.user32 = ctypes.windll.user32
        # Try to register
        if self.user32.RegisterHotKey(None, 1, MOD_ALT | MOD_SHIFT, VK_D):
            self.registered = True
        else:
            print("Failed to register global hotkey Alt+Shift+D")

    def nativeEventFilter(self, eventType, message):
        if eventType == b"windows_generic_MSG" or eventType == b"windows_dispatcher_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == 0x0312:  # WM_HOTKEY
                if msg.wParam == 1:
                    self.callback()
                    return True, 0
        return False, 0

    def cleanup(self):
        if self.registered:
            self.user32.UnregisterHotKey(None, 1)

class HotkeyManager(QObject):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.visible = True
        self.filter = GlobalHotkeyFilter(self.toggle_fences)
        
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().installNativeEventFilter(self.filter)

    def toggle_fences(self):
        self.visible = not self.visible
        for window in self.ui_manager.get_all_windows():
            if self.visible:
                window.show()
            else:
                window.hide()

    def __del__(self):
        self.filter.cleanup()
