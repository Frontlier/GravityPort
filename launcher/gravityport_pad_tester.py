# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only SDL3 controller inspector in a separate native Tkinter window.

No PS4 game files are read or modified. The inspector opens gamepads through SDL3,
not through the Gravity Rush runtime; it works with real or virtual gamepads.
"""
from __future__ import annotations
import ctypes as C
from pathlib import Path
import json
import os
import sys

FLAG_GAMEPAD = 0x00002000
BTN = ("A/Cruz", "B/Círculo", "X/Quadrado", "Y/Triângulo", "View",
       "Home", "Menu", "L3", "R3", "LB", "RB", "↑", "↓", "←", "→")
AXES = ("LX","LY","RX","RY","LT","RT")
BASE="#091623";PANEL="#14283c";FIELD="#1b354b";ACCENT="#65e6cf"
TEXT="#edfaff";MUTED="#a9c4d1";BORDER="#315368"

def locate_sdl():
    candidates = [
        Path(sys.executable).resolve().parent / "SDL3.dll",
        Path(sys.executable).resolve().parent / "bin" / "SDL3.dll",
        Path(os.environ.get("MSYS2_ROOT", "C:/msys64")) / "clang64" / "bin" / "SDL3.dll",
        Path("C:/msys64/clang64/bin/SDL3.dll")
    ]
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        if folder:
            candidates.append(Path(folder) / "SDL3.dll")
    for f in candidates:
        if f.is_file():
            return f
    raise FileNotFoundError("SDL3.dll não encontrada. Verifique a instalação das bibliotecas.")

class ControllerProbe:
    def __init__(self, dll=None):
        self.dll=dll or C.CDLL(str(locate_sdl()))
        s=self.dll
        s.SDL_Init.argtypes=[C.c_uint32]; s.SDL_Init.restype=C.c_bool
        s.SDL_GetGamepads.argtypes=[C.POINTER(C.c_int)]; s.SDL_GetGamepads.restype=C.POINTER(C.c_uint32)
        s.SDL_free.argtypes=[C.c_void_p]; s.SDL_free.restype=None
        s.SDL_OpenGamepad.argtypes=[C.c_uint32]; s.SDL_OpenGamepad.restype=C.c_void_p
        s.SDL_CloseGamepad.argtypes=[C.c_void_p]; s.SDL_CloseGamepad.restype=None
        s.SDL_GetGamepadName.argtypes=[C.c_void_p]; s.SDL_GetGamepadName.restype=C.c_char_p
        s.SDL_GetGamepadButton.argtypes=[C.c_void_p,C.c_int]; s.SDL_GetGamepadButton.restype=C.c_bool
        s.SDL_GetGamepadAxis.argtypes=[C.c_void_p,C.c_int]; s.SDL_GetGamepadAxis.restype=C.c_int16
        s.SDL_GamepadHasSensor.argtypes=[C.c_void_p,C.c_int]; s.SDL_GamepadHasSensor.restype=C.c_bool
        s.SDL_GetNumGamepadTouchpads.argtypes=[C.c_void_p];s.SDL_GetNumGamepadTouchpads.restype=C.c_int
        s.SDL_PumpEvents.argtypes=[];s.SDL_PumpEvents.restype=None
        s.SDL_UpdateGamepads.argtypes=[];s.SDL_UpdateGamepads.restype=None
        s.SDL_QuitSubSystem.argtypes=[C.c_uint32];s.SDL_QuitSubSystem.restype=None
        if not s.SDL_Init(FLAG_GAMEPAD):
            raise RuntimeError("Falha ao inicializar SDL3 Gamepad")
        self.pad=None
        self.instance=None
    def poll(self):
        s=self.dll
        s.SDL_PumpEvents();s.SDL_UpdateGamepads()
        count=C.c_int(0)
        ids=s.SDL_GetGamepads(C.byref(count))
        present=[]
        if ids:
            present=[int(ids[i]) for i in range(count.value)]
            s.SDL_free(C.cast(ids,C.c_void_p))
        if self.pad and self.instance not in present:
            s.SDL_CloseGamepad(self.pad)
            self.pad=None;self.instance=None
        if not self.pad and present:
            self.instance=present[0]
            self.pad=s.SDL_OpenGamepad(self.instance)
            if not self.pad:self.instance=None
        if not self.pad:
            return {"connected":False,"count":len(present),"name":"Nenhum controle detectado",
                    "buttons":[], "axes":{k:0.0 for k in AXES},
                    "gyro":False,"accelerometer":False,"touchpads":0}
        name=s.SDL_GetGamepadName(self.pad) or b"Controle SDL3"
        name=name.decode("utf-8","replace")
        buttons=[name for i,name in enumerate(BTN) if s.SDL_GetGamepadButton(self.pad,i)]
        axes={}
        for i,axis in enumerate(AXES):
            raw=int(s.SDL_GetGamepadAxis(self.pad,i))
            axes[axis]=round(max(0,raw)/32767 if i>=4 else max(-1.0,raw/32767),3)
        return {"connected":True,"count":len(present),"name":name,"buttons":buttons,"axes":axes,
                "gyro":bool(s.SDL_GamepadHasSensor(self.pad,2)),
                "accelerometer":bool(s.SDL_GamepadHasSensor(self.pad,1)),
                "touchpads":max(0,int(s.SDL_GetNumGamepadTouchpads(self.pad)))}
    def close(self):
        if self.pad:
            self.dll.SDL_CloseGamepad(self.pad);self.pad=None
        self.dll.SDL_QuitSubSystem(FLAG_GAMEPAD)

class TesterWindow:
    def __init__(self,root,probe):
        import tkinter as tk
        self.tk=tk;self.root=root;self.probe=probe
        root.title("GravityPort | Teste de Controle SDL3")
        root.configure(bg=BASE)
        root.geometry("900x560")
        root.minsize(840,540)
        header=tk.Frame(root,bg=BASE);header.pack(fill="x",padx=30,pady=(22,14))
        tk.Label(header,text="GRAVITYPORT  /  DEVICE LAB",bg=BASE,fg=ACCENT,
                 font=("Segoe UI",10,"bold")).pack(anchor="w")
        tk.Label(header,text="Teste de controle em tempo real",bg=BASE,fg=TEXT,
                 font=("Segoe UI",23,"bold")).pack(anchor="w")
        self.state=tk.Label(header,text="Procurando dispositivo SDL3...",bg=BASE,fg=MUTED,
                            font=("Segoe UI",11))
        self.state.pack(anchor="w",pady=(3,0))
        middle=tk.Frame(root,bg=BASE)
        middle.pack(fill="both",expand=True,padx=30,pady=(0,8))
        self.pad_canvas=tk.Canvas(middle,width=495,height=292,bg=PANEL,highlightthickness=1,
                                  highlightbackground=BORDER)
        self.pad_canvas.pack(side="left",fill="both",expand=True,padx=(0,15))
        right=tk.Frame(middle,bg=PANEL,highlightthickness=1,highlightbackground=BORDER,width=270)
        right.pack(side="right",fill="y")
        right.pack_propagate(False)
        tk.Label(right,text="BOTÕES PRESSIONADOS",fg=MUTED,bg=PANEL,
                 font=("Segoe UI",10,"bold")).pack(anchor="w",padx=17,pady=(16,4))
        self.buttons=tk.Label(right,text="Nenhum",fg=TEXT,bg=PANEL,justify="left",
                              font=("Segoe UI",13),wraplength=236)
        self.buttons.pack(anchor="w",padx=17,pady=(4,12))
        tk.Label(right,text="SENSORES & TOUCHPAD",fg=MUTED,bg=PANEL,
                 font=("Segoe UI",10,"bold")).pack(anchor="w",padx=17,pady=(11,4))
        self.sensors=tk.Label(right,text="—",fg=TEXT,bg=PANEL,justify="left",font=("Segoe UI",11))
        self.sensors.pack(anchor="w",padx=17,pady=(0,16))
        self.axes_view=tk.Label(right,text="",fg=MUTED,bg=PANEL,justify="left",
                                font=("Consolas",11))
        self.axes_view.pack(anchor="w",padx=17,pady=(7,15))
        footer=tk.Frame(root,bg=BASE);footer.pack(fill="x",padx=30,pady=(0,22))
        tk.Label(footer,text="Somente leitura • não altera mapeamento ou dados do jogo",
                 fg=MUTED,bg=BASE,font=("Segoe UI",10)).pack(side="left")
        tk.Button(footer,text="Fechar",command=root.destroy,bg=ACCENT,fg="#0c2c32",border=0,
                  padx=23,pady=9,font=("Segoe UI",11,"bold"),cursor="hand2").pack(side="right")
        self.draw({"connected":False,"buttons":[],"axes":{k:0 for k in AXES}})
        root.protocol("WM_DELETE_WINDOW",root.destroy)
        root.after(40,self.tick)
    def draw(self,s):
        c=self.pad_canvas
        c.delete("all")
        w=495;h=292
        c.create_oval(58,22,434,282,fill="",outline="#1b5b62",width=1)
        c.create_polygon(139,70,350,70,410,116,454,231,429,248,355,194,
                         139,194,67,248,42,231,86,116,
                         fill="#24374b",outline="#60788c",width=3,smooth=True)
        def circle(x,y,label,key=None,base=FIELD):
            active=key in s["buttons"] if key else False
            c.create_oval(x-22,y-22,x+22,y+22,fill=ACCENT if active else base,
                          outline=ACCENT if active else "#6b8ba1",width=2)
            c.create_text(x,y,text=label,fill="#062c34" if active else TEXT,
                          font=("Segoe UI",11,"bold"))
        circle(350,116,"Y","Y/Triângulo")
        circle(385,148,"B","B/Círculo")
        circle(315,148,"X","X/Quadrado")
        circle(350,180,"A","A/Cruz")
        circle(111,123,"↑","↑")
        circle(111,167,"↓","↓")
        circle(86,145,"←","←")
        circle(136,145,"→","→")
        def stick(x,y,axisx,axisy,click):
            ax=float(s["axes"].get(axisx,0));ay=float(s["axes"].get(axisy,0))
            circle(x,y,"",click)
            c.create_oval(x+ax*14-11,y+ay*14-11,x+ax*14+11,y+ay*14+11,
                          fill=ACCENT if click in s["buttons"] else "#91aab9",outline="")
        stick(180,164,"LX","LY","L3")
        stick(284,202,"RX","RY","R3")
        for key,x,y in [("LB",115,74),("RB",379,74)]:
            c.create_rectangle(x-29,y-15,x+29,y+5,fill=ACCENT if key in s["buttons"] else FIELD,
                               outline=BORDER)
            c.create_text(x,y-5,text=key,fill="#07282d" if key in s["buttons"] else TEXT,
                          font=("Segoe UI",10,"bold"))
        c.create_text(246,110,text="GP",fill=ACCENT,font=("Segoe UI",15,"bold"))
        c.create_text(246,147,text="SDL3",fill=MUTED,font=("Segoe UI",9,"bold"))
        c.create_text(124,266,text="LT  "+str(round(float(s["axes"].get("LT",0))*100))+"%",
                      fill=TEXT,font=("Consolas",10))
        c.create_text(365,266,text="RT  "+str(round(float(s["axes"].get("RT",0))*100))+"%",
                      fill=TEXT,font=("Consolas",10))
    def tick(self):
        try:
            s=self.probe.poll()
            self.state.configure(text=(s["name"] if s["connected"] else
                "Nenhum controle encontrado · conecte e pressione um botão"))
            self.buttons.configure(text="  ·  ".join(s["buttons"]) if s["buttons"] else "Nenhum")
            self.sensors.configure(text=("Giroscópio: "+("SIM" if s["gyro"] else "NÃO")+
                "\nAcelerômetro: "+("SIM" if s["accelerometer"] else "NÃO")+
                "\nTouchpads: "+str(s["touchpads"])))
            self.axes_view.configure(text="\n".join(f"{a}: {s['axes'].get(a,0):+.2f}" for a in AXES))
            self.draw(s)
        except Exception as error:
            self.state.configure(text="Falha na leitura SDL3: "+str(error))
        if self.root.winfo_exists():
            self.root.after(50,self.tick)

def main():
    probe=ControllerProbe()
    if "--probe" in sys.argv:
        print(json.dumps(probe.poll(),ensure_ascii=False))
        probe.close()
        return
    import tkinter as tk
    root=tk.Tk()
    TesterWindow(root,probe)
    if "--smoke" in sys.argv:
        try:
            root.attributes("-topmost", True)
            root.lift()
        except tk.TclError:
            pass
        from PIL import ImageGrab
        output=Path(__file__).resolve().parents[1]/"out"/"gravityport-pad-tester.png"
        output.parent.mkdir(parents=True,exist_ok=True)
        def capture():
            root.update_idletasks()
            x,y=root.winfo_rootx(),root.winfo_rooty()
            ImageGrab.grab(bbox=(x,y,x+root.winfo_width(),y+root.winfo_height())).save(output)
            print("PAD_TESTER_SCREENSHOT",output,output.stat().st_size,flush=True)
            root.destroy()
        root.after(1450,capture)
    try:
        root.mainloop()
    finally:
        probe.close()

if __name__=="__main__":
    main()
