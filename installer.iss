[Setup]
AppName=Nestly
AppVersion=1.0.0
AppPublisher=Nestly
DefaultDirName={pf}\Nestly
DefaultGroupName=Nestly
OutputBaseFilename=Nestly_Installer
SetupIconFile=resources\icons\nestly_icon.ico
UninstallDisplayIcon={app}\Nestly.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Run Nestly on Windows startup"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\Nestly.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\icons\*"; DestDir: "{app}\resources\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Nestly"; Filename: "{app}\Nestly.exe"; IconFilename: "{app}\resources\icons\nestly_icon.ico"
Name: "{commondesktop}\Nestly"; Filename: "{app}\Nestly.exe"; IconFilename: "{app}\resources\icons\nestly_icon.ico"; Tasks: desktopicon
Name: "{userstartup}\Nestly"; Filename: "{app}\Nestly.exe"; Tasks: startupicon

[Run]
Filename: "{app}\Nestly.exe"; Description: "Launch Nestly"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCR; Subkey: "Directory\Background\shell\Nestly"; ValueType: string; ValueName: ""; ValueData: "Создать сетку Nestly"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\Background\shell\Nestly"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\resources\icons\nestly_icon.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\Background\shell\Nestly\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Nestly.exe"" --create-fence"; Flags: uninsdeletekey
