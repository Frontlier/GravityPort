# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate original decorative art for the native Tkinter launcher; no game assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageFont
import math
import random

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"launcher"/"gravityport-background.png"
W,H=1680,1050
im=Image.new("RGB",(W,H))
pix=im.load()
for y in range(H):
    for x in range(W):
        xf=x/W; yf=y/H
        radial=max(0.0,1-(((xf-.73)/.60)**2+((yf-.42)/.9)**2)**.55)
        horizon=max(0.0,(yf-.7)*1.35)
        pix[x,y]=(round(6+12*radial+8*horizon),
                  round(17+27*radial+5*horizon),
                  round(31+32*radial+6*horizon))
im=im.convert("RGBA")
glow=Image.new("RGBA",(W,H))
g=ImageDraw.Draw(glow)
g.ellipse((700,-230,1700,800), fill=(73,237,209,43))
g.ellipse((1040,300,1900,1200),fill=(44,131,215,38))
glow=glow.filter(ImageFilter.GaussianBlur(145))
im=Image.alpha_composite(im,glow)
d=ImageDraw.Draw(im,"RGBA")
random.seed(42)
# Engineering grid, faded toward the upper right.
for x in range(600,W,70):
    d.line([(x,0),(x,H)],fill=(123,220,216,9),width=1)
for y in range(0,H,70):
    d.line([(590,y),(W,y)],fill=(123,220,216,9),width=1)
# Orbital telemetry rings, compressed perspective.
center=(1260,510)
for size,alpha,width in [(600,35,2),(505,31,2),(415,35,2),(310,57,3)]:
    bounds=(center[0]-size,center[1]-size*.78,
            center[0]+size,center[1]+size*.78)
    d.arc(bounds,start=-120,end=215,fill=(129,251,224,alpha),width=width)
    d.arc(bounds,start=220,end=240,fill=(118,208,250,alpha+45),width=width+2)
# Sunken gravity core of light.
core=Image.new("RGBA",(W,H))
c=ImageDraw.Draw(core)
cx,cy=center
for radius in range(215,45,-4):
    strength=round(19*((215-radius)/170)**1.5)
    c.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=(58,229,209,strength),width=3)
c.ellipse((cx-64,cy-64,cx+64,cy+64),fill=(104,245,213,28),outline=(140,245,230,120),width=3)
core=core.filter(ImageFilter.GaussianBlur(4))
im=Image.alpha_composite(im,core)
d=ImageDraw.Draw(im,"RGBA")
# Architectural diagonals: abstract floating panels instead of game imagery.
for i in range(15):
    x=900+i*78; y=690+(i%4)*13
    d.polygon([(x,y),(x+73,y-55),(x+123,y-40),(x+49,y+17)],
              fill=(112,220,201,10+i%3*4),outline=(136,231,214,22))
for i in range(120):
    x=random.randint(660,W-30);y=random.randint(40,H-40)
    r=random.choice([1,1,2])
    d.ellipse((x-r,y-r,x+r,y+r),fill=(150,237,230,random.randint(30,120)))
# Technical headings and fixed labels intentionally placed away from center card.
fontbold=r"C:\Windows\Fonts\segoeuib.ttf"
fontreg=r"C:\Windows\Fonts\segoeui.ttf"
try:
    big=ImageFont.truetype(fontbold,77)
    sub=ImageFont.truetype(fontreg,22)
    small=ImageFont.truetype(fontbold,15)
except OSError:
    big=sub=small=ImageFont.load_default()
d.text((670,135),"GRAVITY",font=big,fill=(239,252,255,230),stroke_width=0)
d.text((674,216),"RUSH",font=big,fill=(132,242,211,248))
d.line((675,316,1005,316),fill=(110,225,206,160),width=3)
d.text((676,343),"THE WINDOWS NATIVE PORT",font=sub,fill=(173,210,223,210))
d.text((697,949),"PS4 / X86-64    •    VULKAN    •    GRAVITYPORT LAB",font=small,fill=(153,216,210,170))
OUT.parent.mkdir(parents=True,exist_ok=True)
im.convert("RGB").save(OUT,optimize=True)
ico=Image.new("RGBA",(256,256),(5,22,36,255))
idraw=ImageDraw.Draw(ico,"RGBA")
idraw.rounded_rectangle((13,13,243,243),radius=56,
                        fill=(22,70,86,255),outline=(100,235,209,245),width=9)
idraw.polygon([(128,31),(217,83),(217,173),(128,227),(39,173),(39,83)],
              outline=(148,255,230,225),width=6)
try:
    mark_font=ImageFont.truetype(fontbold,97)
except OSError:
    mark_font=ImageFont.load_default()
idraw.text((59,76),"GP",font=mark_font,fill=(142,255,229,255))
ico_file=OUT.with_name("gravityport.ico")
ico.save(ico_file,format="ICO",sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print("ASSET_READY",OUT,OUT.stat().st_size)
print("ICON_READY",ico_file,ico_file.stat().st_size)
