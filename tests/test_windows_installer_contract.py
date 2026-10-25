# SPDX-License-Identifier: GPL-2.0-or-later
"""Static security and UX checks for GravityPort's official v0.4.0 Windows setup."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "packaging/windows/GravityPort-Installer.iss").read_text(encoding="utf8")
BUILDER = (ROOT / "tools/build_windows_installer.ps1").read_text(encoding="utf8")


class InstallerContractTests(unittest.TestCase):
    def test_per_user_and_no_admin(self):
        for exact in ("PrivilegesRequired=lowest",
                      "DefaultDirName={localappdata}\\Programs\\GravityPort",
                      "ArchitecturesAllowed=x64compatible",
                      "WizardStyle=modern",
                      "CloseApplications=no"):
            with self.subTest(exact=exact):
                self.assertIn(exact, SOURCE)
        self.assertIn("compiler:Languages\\BrazilianPortuguese.isl", SOURCE)
        self.assertIn("compiler:Default.isl", SOURCE)

    def test_start_menu_desktop_optional_and_finish_launch(self):
        for exact in ("UninstallDisplayName=GravityPort", "{autoprograms}\\GravityPort",
                      "{autodesktop}\\GravityPort", "GravityPort Launcher.exe",
                      "GravityPort.exe", "nowait postinstall skipifsilent",
                      "Tasks: desktopicon"):
            self.assertIn(exact, SOURCE)

    def test_game_directory_optional_and_validated(self):
        for exact in ("CreateCustomPage", "BrowseForFolder", "GameLater.Checked := True",
                      "FileExists(AddBackslash(Directory) + 'eboot.bin')",
                      "ExpandConstant('{param:GAMEFOLDER|}')",
                      "SaveStringsToUTF8FileWithoutBOM", "EscapeJsonPath(Directory)"):
            self.assertIn(exact, SOURCE)

    def test_never_overwrites_settings_or_removes_personal_data(self):
        for exact in ("FileExists(TargetFile)", "onlyifdoesntexist uninsneveruninstall",
                      "gravityport-launcher\\settings.json"):
            self.assertIn(exact, SOURCE)
        self.assertNotIn("[UninstallDelete]", SOURCE)
        self.assertNotIn("DelTree(", SOURCE)
        self.assertNotIn("DeleteFile(TargetFile)", SOURCE)

    def test_installer_is_built_only_from_clean_verifiable_zip(self):
        for exact in ("verify_public_release.py", "installer-clean-extract",
                      "Expand-Archive", "MANIFEST-SHA256.json",
                      "OriginalZip.sha256", "Get-FileHash", "source_commit",
                      "nvngx_", r"gow3_dlss\.dll", r"eboot\.bin",
                      r"boot-linked\.bin", "GravityPort-0.4.0-Setup.exe"):
            with self.subTest(exact=exact):
                self.assertIn(exact, BUILDER)
        self.assertNotIn("Remove-Item", BUILDER)

    def test_public_docs_disclose_limitations(self):
        text=(ROOT / "docs/INSTALLER.md").read_text(encoding="utf8")
        for s in ("eboot.bin", "DLSS", "FSR 4", "NAO contem",
                  "SHA-256", "Desinstalar", "sem mudar o executavel"):
            self.assertIn(s, text)
        self.assertIn("Instalador opcional",
                      (ROOT / "CHANGELOG-GRAVITYPORT.md").read_text(encoding="utf8"))


if __name__ == "__main__":
    unittest.main()
