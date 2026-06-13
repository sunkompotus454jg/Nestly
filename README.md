# Nestly

Nestly is a premium, lightweight, and modern desktop organization tool for Windows. It allows you to group your shortcuts, files, and folders into customizable grids (fences) directly on your desktop, helping you maintain a clean and organized workspace.

## Features

*   **Desktop Grids:** Create resizable, movable windows to hold desktop items.
*   **Premium UI:** Frameless design, custom drop shadows, and modern glassmorphism elements.
*   **Auto-Collapse:** Fences can automatically collapse into a title bar when the mouse leaves, saving screen space.
*   **Profile Management:** Create and switch between multiple profiles (e.g., Home, Work, Gaming) with entirely different layouts and fences.
*   **Global Hotkeys:** Use keyboard shortcuts to quickly hide or show all your grids.
*   **Search Functionality:** Built-in animated search bar to instantly find files within a grid.
*   **Custom Themes:** Fully customizable colors, borders, and background opacity. Includes a built-in theme editor.
*   **System Tray Integration:** Manage profiles, access settings, and create new grids directly from the Windows system tray.
*   **Context Menu Integration:** Adds a "Create Nestly Grid" option directly to your Windows desktop right-click menu.
*   **Multi-language Support:** Available in English, Russian, and Ukrainian.
*   **Autostart:** Option to launch automatically with Windows.

## Installation

### Using the Installer (Recommended)
1. Download the latest `Nestly_Installer.exe` from the releases page.
2. Run the installer and follow the instructions.
3. The installer will automatically set up the desktop shortcuts and context menu integrations.

### Portable Version
1. Download the `Nestly.exe` portable build.
2. Place it anywhere on your computer and run it.

## Building from Source

Nestly is built using Python 3 and PyQt6.

### Prerequisites
* Python 3.10 or higher
* pip (Python package installer)

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/sunkompotus454jg/MyFences.git
   cd MyFences
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Building the Executable
To build a standalone executable and installer:
1. Run `build.cmd` in the project root. This will install PyInstaller and build `Nestly.exe` in the `dist` folder.
2. Download and install Inno Setup.
3. Open `installer.iss` in Inno Setup and click "Compile". This will generate the final installer in the `Output` folder.

## Usage

*   **Create a Grid:** Right-click on your desktop and select "Создать сетку Nestly" or use the System Tray menu.
*   **Add Files:** Drag and drop files, folders, or shortcuts from your desktop directly into a grid.
*   **Resize and Move:** Drag the edges to resize. Drag the title bar to move the grid around your desktop.
*   **Settings:** Access the Settings menu from the System Tray to change languages, manage profiles, or configure auto-start.

## Architecture

*   **Core:** Handles data persistence, multi-language support, theming, and profile management.
*   **UI:** Manages the visual rendering of the fences, custom premium dialogs, and animations.
*   **IPC:** Manages single-instance enforcement and communication between instances (e.g., when creating a new fence from the context menu).
