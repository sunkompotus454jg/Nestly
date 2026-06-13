@echo off
echo Installing PyInstaller...
pip install pyinstaller pillow

echo.
echo Building Nestly.exe...
python -m PyInstaller --noconsole --onefile --icon=resources/icons/nestly_icon.ico --name=Nestly main.py

echo.
echo ========================================================
echo Build complete! Nestly.exe is located in the "dist" folder.
echo.
echo To create the installer (Nestly_Installer.exe), please 
echo download and install Inno Setup (https://jrsoftware.org/isinfo.php).
echo Then, right click "installer.iss" and select "Compile".
echo ========================================================
pause
