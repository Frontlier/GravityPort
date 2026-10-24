# SPDX-License-Identifier: GPL-2.0-or-later
"""Overview tab for the native (Tkinter) GravityPort launcher."""
from __future__ import annotations

from pathlib import Path
import math
import time

from gravityport_metrics import last_session

SURFACE = "#102438"
INNER = "#152b3d"
TEAL = "#65e6cf"
MUTED = "#a4b9c8"
TEXT = "#f2fcff"
LINE = "#294456"

def _metric(app, parent, label, value, hint, accent=False):
    tk=app.tk
    block=tk.Frame(parent,bg=INNER,highlightthickness=1,highlightbackground=LINE)
    block.pack(side="left",fill="both",expand=True,padx=(0,app.px(10)))
    tk.Label(block,text=label.upper(),fg=MUTED,bg=INNER,
             font=app.font(10,"bold"),anchor="w").pack(fill="x",padx=app.px(12),pady=(app.px(12),app.px(4)))
    tk.Label(block,text=value,fg=TEAL if accent else TEXT,bg=INNER,
             font=app.font(20,"bold"),anchor="w").pack(fill="x",padx=app.px(12))
    tk.Label(block,text=hint,fg=MUTED,bg=INNER,anchor="w",
             font=app.font(10)).pack(fill="x",padx=app.px(12),pady=(0,app.px(12)))
    return block

def _chart(app, holder, samples):
    tk=app.tk
    width,height=625,116
    cv=tk.Canvas(holder,height=app.px(height),bg=SURFACE,highlightthickness=0)
    cv.pack(fill="x",padx=app.px(14),pady=(0,app.px(9)))
    if len(samples)<2:
        cv.create_text(app.px(25),app.px(56),anchor="w",text="Sem medições suficientes no último log",
                       fill=MUTED,font=app.font(13))
        return
    left,right=app.px(16),app.px(608)
    top,bottom=app.px(15),app.px(94)
    low=max(0,math.floor((min(samples)-8)/10)*10)
    high=max(60,math.ceil((max(samples)+5)/10)*10)
    if high==low:high+=20
    for i in range(4):
        y=top+int((bottom-top)*i/3)
        cv.create_line(left,y,right,y,fill=LINE)
    pts=[]
    for i,val in enumerate(samples):
        x=left+(right-left)*i/(len(samples)-1)
        y=bottom-(bottom-top)*(val-low)/(high-low)
        pts.extend((x,y))
    cv.create_line(*pts,fill=TEAL,width=max(2,app.px(2)),smooth=False)
    cv.create_oval(pts[-2]-4,pts[-1]-4,pts[-2]+4,pts[-1]+4,fill=TEAL,outline=TEAL)
    cv.create_text(left,bottom+app.px(15),anchor="w",fill=MUTED,
                   text="INÍCIO DO TRECHO",font=app.font(9,"bold"))
    cv.create_text(right,bottom+app.px(15),anchor="e",fill=MUTED,
                   text="ÚLTIMO INTERVALO",font=app.font(9,"bold"))

def _last_save(app):
    try:
        folder=app.user_dir()/"savedata"
        if not folder.is_dir():
            return "Sem saves"
        newest=max((p.stat().st_mtime for p in folder.rglob("*")
                    if p.is_file() and p.suffix.lower()!=".png"),default=0)
        return time.strftime("%d/%m %H:%M",time.localtime(newest)) if newest else "Sem saves"
    except OSError:
        return "Indisponível"

def render_dashboard(app, body, foot):
    """All displayed data is read-only; actions reuse the existing native launcher."""
    tk=app.tk
    game=app.logic.game_info(app.app.get("game_dir", ""))
    # In a frozen EXE, DATA_DIR is the installation folder while the user's
    # saves and last_run.log may live elsewhere. Follow the selected user folder.
    data=last_session(app.user_dir())
    intro=tk.Frame(body,bg=SURFACE,highlightthickness=1,highlightbackground="#246373")
    intro.pack(fill="x",pady=(app.px(5),app.px(16)))
    row=tk.Frame(intro,bg=SURFACE)
    row.pack(fill="x",padx=app.px(19),pady=(app.px(16),0))
    tk.Label(row,text="GRAVITY RUSH REMASTERED",font=app.font(19,"bold"),
             fg=TEXT,bg=SURFACE,anchor="w").pack(side="left")
    ready=bool(game)
    tk.Label(row,text="● PRONTO" if ready else "● CONFIGURAR JOGO",fg=TEAL if ready else "#f1b677",
             bg=SURFACE,font=app.font(11,"bold")).pack(side="right")
    tk.Label(intro,text="PORT NATIVO  /  PS4 X86-64  /  VULKAN  /  CUSA01113",
             font=app.font(11,"bold"),fg=MUTED,bg=SURFACE,
             anchor="w").pack(fill="x",padx=app.px(19),pady=(0,app.px(14)))
    metrics=tk.Frame(body,bg="#101928")
    metrics.pack(fill="x",pady=(0,app.px(15)))
    _metric(app,metrics,"FPS no log",f"{data['fps']:.1f}" if data["fps"] is not None else "—",
            "última sessão",accent=True)
    _metric(app,metrics,"Frametime p99",
            f"{data['p99_ms']:.1f} ms" if data["p99_ms"] is not None else "—",
            "não é medição ao vivo")
    _metric(app,metrics,"Renderização",app.ini.get("render_resolution","native").upper(),
            app.ini.get("output_res","1920x1080"))
    _metric(app,metrics,"Save recente",_last_save(app),"último save registrado")
    chart=tk.Frame(body,bg=SURFACE,highlightthickness=1,highlightbackground=LINE)
    chart.pack(fill="x",pady=(0,app.px(15)))
    heading=tk.Frame(chart,bg=SURFACE)
    heading.pack(fill="x",padx=app.px(14),pady=(app.px(13),app.px(5)))
    tk.Label(heading,text="HISTÓRICO DE FLUIDEZ",fg=TEXT,bg=SURFACE,
             font=app.font(13,"bold")).pack(side="left")
    tk.Label(heading,text=f"{len(data['samples'])} medições  ·  última sessão",
             fg=MUTED,bg=SURFACE,font=app.font(10)).pack(side="right")
    _chart(app,chart,data["samples"])
    controls=tk.Frame(body,bg=SURFACE,highlightthickness=1,highlightbackground=LINE)
    controls.pack(fill="x",pady=(0,app.px(8)))
    pad=app.app.get("pad_style","xbox")
    title="Controle Xbox / XInput" if pad=="xbox" else "Controle PlayStation / SDL3"
    if data["controller"]:
        title=data["controller"].replace("XInput Controller #1","Xbox / XInput")
    tk.Label(controls,text=title,fg=TEXT,bg=SURFACE,
             font=app.font(14,"bold")).pack(anchor="w",padx=app.px(16),pady=(app.px(13),0))
    tk.Label(controls,text=("Giroscópio virtual: L3 + analógico direito"
                            if app.app.get("xinput_gyro_stick") else
                            "Giroscópio virtual desativado")
             +"   •   Touchpad: View + direcional direito",
             fg=MUTED,bg=SURFACE,font=app.font(11)).pack(anchor="w",padx=app.px(16),pady=(app.px(2),app.px(13)))
    tk.Label(body,text="Dados baseados nos logs da última execução, não são FPS ao vivo.",
             fg=MUTED,bg="#101928",font=app.font(10)).pack(anchor="w",pady=(0,app.px(6)))
    app.footer(foot,[("Controls",lambda:app.open_page("controls"),False),
                     ("Play",app.launch,True)])
