# SPDX-License-Identifier: GPL-2.0-or-later
"""Regression for external XML patches with tuple-based game title IDs."""
import sys
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from paths import ROOT
sys.path.insert(0,str(ROOT/"scripts"))
import patches

class ExternalIdTests(unittest.TestCase):
    def test_matching_title_id_accepts_tuple(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            xml=directory/"compatibility.xml"
            xml.write_text(
                '<Patch><ID>CUSA01113</ID><Metadata AppVer="01.00" '
                'AppElf="eboot.bin" Name="ThirdParty Patch" isEnabled="true"/></Patch>',
                encoding="utf-8"
            )
            entries=patches.external_patches(directory,"01.00",directory/"builtin.xml",
                                            ("CUSA01113","CUSA01130"))
        self.assertEqual(len(entries),1)
        self.assertEqual(entries[0][0],"compatibility.xml/ThirdParty Patch")
    def test_nonmatching_id_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            xml=directory/"other.xml"
            xml.write_text(
                '<Patch><ID>CUSA99999</ID><Metadata AppVer="01.00" '
                'Name="Wrong Region"/></Patch>',encoding="utf-8"
            )
            entries=patches.external_patches(directory,"01.00",directory/"builtin.xml",
                                            ("CUSA01113",))
        self.assertEqual(entries,[])
    def test_invalid_xml_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            (directory/"broken.xml").write_text("<broken",encoding="utf-8")
            entries=patches.external_patches(directory,"01.00",directory/"builtin.xml",
                                            ("CUSA01113",))
        self.assertEqual(entries,[])

if __name__=="__main__":
    unittest.main()
