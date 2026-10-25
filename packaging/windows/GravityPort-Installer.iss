; GravityPort Windows installer built from audited v0.4.0 portable payload.
; SPDX-License-Identifier: GPL-2.0-or-later
; Game files / firmware / saves / proprietary NVIDIA NGX libraries are NOT bundled.
; Build with /DPayloadPath="..." /DOutputPath="..." via tools/build_windows_installer.ps1.
#ifndef PayloadPath
  #error Specify /DPayloadPath pointing to the audited public v0.4.0 folder
#endif
#ifndef OutputPath
  #error Specify /DOutputPath for compiled installer
#endif

#define GpVersion "0.4.0"
#define GpSetupBase "GravityPort-" + GpVersion + "-Setup"

[Setup]
AppId={{DD39B278-AC1E-44D3-9DCB-A654106DB772}
AppName=GravityPort
AppVersion={#GpVersion}
AppVerName=GravityPort {#GpVersion} - Windows Preview
AppPublisher=GravityPort contributors (Frontlier, baseado em LucaPazienza)
AppPublisherURL=https://github.com/Frontlier/GravityPort
AppSupportURL=https://github.com/Frontlier/GravityPort/issues
AppUpdatesURL=https://github.com/Frontlier/GravityPort/releases
DefaultDirName={localappdata}\Programs\GravityPort
DefaultGroupName=GravityPort
UninstallDisplayIcon={app}\GravityPort Launcher.exe
UninstallDisplayName=GravityPort - Windows Preview
SetupIconFile=..\..\launcher\gravityport.ico
LicenseFile=..\..\LICENSE
OutputDir={#OutputPath}
OutputBaseFilename={#GpSetupBase}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
CloseApplications=no
RestartApplications=no
UsePreviousAppDir=yes
DisableDirPage=no
ShowLanguageDialog=auto
AllowNoIcons=yes
; No machine-wide services, no drivers, no elevation, no telemetry.
; User saves and settings must survive upgrades and uninstallation.

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Files]
; Install only the already audited Windows preview package, from a clean build tree.
; Do not overwrite a player's modified graphics configuration on an upgrade.
Source: "{#PayloadPath}\*"; DestDir: "{app}"; Excludes: "gravityrush.ini"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadPath}\gravityrush.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{autoprograms}\GravityPort"; Filename: "{app}\GravityPort Launcher.exe"; WorkingDir: "{app}"; Comment: "Abrir GravityPort e selecionar seu Gravity Rush Remastered"
Name: "{autoprograms}\GravityPort - Jogar"; Filename: "{app}\GravityPort.exe"; WorkingDir: "{app}"; Comment: "Iniciar o jogo usando as configurações já salvas"
Name: "{autodesktop}\GravityPort"; Filename: "{app}\GravityPort Launcher.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\GravityPort Launcher.exe"; Description: "Abrir GravityPort agora"; Flags: nowait postinstall skipifsilent

[Code]
var
  GamePage: TWizardPage;
  GameInfo: TNewStaticText;
  GamePath: TNewEdit;
  GameBrowse: TNewButton;
  GameLater: TNewCheckBox;

procedure ToggleGamePath(Sender: TObject);
begin
  GamePath.Enabled := not GameLater.Checked;
  GameBrowse.Enabled := not GameLater.Checked;
end;

procedure SelectExistingGame(Sender: TObject);
var
  Directory: String;
begin
  Directory := Trim(GamePath.Text);
  if Directory = '' then Directory := ExpandConstant('{userdocs}');
  if BrowseForFolder('Selecione a pasta que contém eboot.bin (Gravity Rush Remastered CUSA01113)', Directory, False) then
  begin
    GamePath.Text := Directory;
    GameLater.Checked := False;
    ToggleGamePath(nil);
  end;
end;

procedure InitializeWizard;
var
  SilentFolder: String;
begin
  GamePage := CreateCustomPage(wpSelectDir,
    'Sua cópia de Gravity Rush Remastered (opcional)',
    'Você só precisa apontar a pasta do jogo. O GravityPort não copia, baixa ou modifica os arquivos do jogo.');

  GameInfo := TNewStaticText.Create(GamePage);
  GameInfo.Parent := GamePage.Surface;
  GameInfo.Top := ScaleY(7);
  GameInfo.Left := 0;
  GameInfo.Width := GamePage.SurfaceWidth;
  GameInfo.Height := ScaleY(55);
  GameInfo.AutoSize := False;
  GameInfo.WordWrap := True;
  GameInfo.Caption := 'Se você já possui Gravity Rush Remastered CUSA01113 v01.00 descompactado, ' +
     'selecione a pasta que contém eboot.bin (por exemplo CUSA01113\Image0). ' +
     'O jogo NÃO é incluído no instalador. Você pode configurar isso depois no launcher.';

  GamePath := TNewEdit.Create(GamePage);
  GamePath.Parent := GamePage.Surface;
  GamePath.Left := 0;
  GamePath.Top := GameInfo.Top + GameInfo.Height + ScaleY(8);
  GamePath.Width := GamePage.SurfaceWidth - ScaleX(93);
  GamePath.Text := '';

  GameBrowse := TNewButton.Create(GamePage);
  GameBrowse.Parent := GamePage.Surface;
  GameBrowse.Left := GamePath.Left + GamePath.Width + ScaleX(6);
  GameBrowse.Top := GamePath.Top - ScaleY(1);
  GameBrowse.Width := ScaleX(87);
  GameBrowse.Height := GamePath.Height + ScaleY(2);
  GameBrowse.Caption := 'Procurar...';
  GameBrowse.OnClick := @SelectExistingGame;

  GameLater := TNewCheckBox.Create(GamePage);
  GameLater.Parent := GamePage.Surface;
  GameLater.Left := 0;
  GameLater.Top := GamePath.Top + GamePath.Height + ScaleY(12);
  GameLater.Width := GamePage.SurfaceWidth;
  GameLater.Height := ScaleY(24);
  GameLater.Caption := 'Vou escolher a pasta do jogo na primeira abertura do GravityPort.';
  GameLater.Checked := True;
  GameLater.OnClick := @ToggleGamePath;

  SilentFolder := Trim(ExpandConstant('{param:GAMEFOLDER|}'));
  if SilentFolder <> '' then
  begin
    GamePath.Text := SilentFolder;
    GameLater.Checked := False;
  end;
  ToggleGamePath(nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Directory: String;
begin
  Result := True;
  if CurPageID <> GamePage.ID then Exit;

  if GameLater.Checked then Exit;
  Directory := Trim(GamePath.Text);
  if Directory = '' then
  begin
    MsgBox('Escolha a pasta do jogo ou marque a opção de configurar depois.',
           mbError, MB_OK);
    Result := False;
    Exit;
  end;
  if not FileExists(AddBackslash(Directory) + 'eboot.bin') then
  begin
    MsgBox('Não encontrei eboot.bin nesta pasta. Escolha CUSA01113\Image0 ' +
           'ou configure o caminho depois no launcher.', mbError, MB_OK);
    Result := False;
  end;
end;

function EscapeJsonPath(Value: String): String;
begin
  Result := Value;
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  TargetFile, Directory: String;
  Lines: TArrayOfString;
begin
  if CurStep <> ssPostInstall then Exit;

  // Never overwrite another GravityPort installation's controller or game preferences.
  TargetFile := ExpandConstant('{userappdata}\gravityport-launcher\settings.json');
  Directory := Trim(GamePath.Text);
  if GameLater.Checked or (Directory = '') or FileExists(TargetFile) then Exit;
  if not FileExists(AddBackslash(Directory) + 'eboot.bin') then Exit;

  if not ForceDirectories(ExtractFileDir(TargetFile)) then
  begin
    MsgBox('Não foi possível criar a configuração. Selecione a pasta em Jogo no launcher.',
           mbInformation, MB_OK);
    Exit;
  end;
  SetArrayLength(Lines, 3);
  Lines[0] := '{';
  Lines[1] := '  "game_dir": "' + EscapeJsonPath(Directory) + '"';
  Lines[2] := '}';
  if not SaveStringsToUTF8FileWithoutBOM(TargetFile, Lines, False) then
    MsgBox('O programa foi instalado, mas não foi possível salvar a pasta do jogo. ' +
           'Selecione a pasta em Jogo no launcher.', mbInformation, MB_OK);
end;
