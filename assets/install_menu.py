import os
import sys
import winreg
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_context_menu():
    if not is_admin():
        # Re-run with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        return

    try:
        # We add to Desktop Background right click:
        # HKEY_CLASSES_ROOT\Directory\Background\shell\Nestly
        key_path = r"Directory\Background\shell\Nestly"
        
        # Create key
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "Создать сетку Nestly")
        
        # Add Icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "icoc.ico"))
        if os.path.exists(icon_path):
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            
        # Add Command
        command_key = winreg.CreateKey(key, "command")
        
        exe_path = sys.executable
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        
        # If running as built exe, command is just 'Nestly.exe --create-fence'
        if getattr(sys, 'frozen', False):
            command_str = f'"{sys.executable}" --create-fence'
        else:
            command_str = f'"{exe_path}" "{script_path}" --create-fence'
            
        winreg.SetValue(command_key, "", winreg.REG_SZ, command_str)
        
        winreg.CloseKey(command_key)
        winreg.CloseKey(key)
        
        print("Successfully added Nestly to Desktop context menu!")
        
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Nestly", "Успешно добавлено в контекстное меню рабочего стола!")
        
    except Exception as e:
        print(f"Error installing context menu: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    install_context_menu()