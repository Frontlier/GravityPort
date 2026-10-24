# SPDX-License-Identifier: GPL-2.0-or-later
"""Smoke-test the real Tk window; does not launch the game or write saves."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"launcher"))
sys.path.insert(0,str(ROOT/"scripts"))
import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab
import gravityrush_launcher as logic
import launcher_ui

def main():
    root=tk.Tk()
    ui=launcher_ui.LauncherWindow(root,tk,filedialog,logic)
    page = sys.argv[1] if len(sys.argv)>1 else "dashboard"
    if page not in {"dashboard","game","video","controls","advanced","log"}:
        raise ValueError("Invalid UI page")
    output=ROOT/"out"/f"gravityport-native-{page}.png"
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        root.attributes("-topmost",True)
    except tk.TclError:
        pass
    def capture():
        print("WINDOW_TITLE",root.title(),flush=True)
        print("PAGE",ui.page,"LANGUAGE",launcher_ui.LANG,flush=True)
        print("GAME_FOUND",bool(logic.game_info(ui.app.get("game_dir",""))),flush=True)
        root.update_idletasks()
        x,y=root.winfo_rootx(),root.winfo_rooty()
        w,h=root.winfo_width(),root.winfo_height()
        if w < 100 or h < 100:
            raise RuntimeError("Launcher is not visible")
        ImageGrab.grab(bbox=(x,y,x+w,y+h)).save(output)
        print("SCREENSHOT",output,output.stat().st_size,flush=True)
        root.destroy()
    root.after(850,lambda:ui.open_page(page))
    root.after(2450,capture)
    root.after(9500,lambda: root.destroy() if root.winfo_exists() else None)
    root.mainloop()

if __name__=="__main__":
    main()
