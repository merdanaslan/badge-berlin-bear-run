"""Check native RGB565 text contrast at all 21 transition steps, using art.lua."""
from pathlib import Path
from lupa import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
lua=LuaRuntime(encoding=None)
def read(name,offset=0,count=None):
    b=(ROOT/'assets'/name.decode()).read_bytes();return b[offset:offset+count] if count is not None else b[offset:]
lua.globals()[b'read_asset']=read
lua.execute(b'fs={read=read_asset};art=require("art");c={};function c:clear() end; c.rect=c.clear;c.line=c.clear;c.pixel=c.clear;g={distance=1900,scene=4,night=0,time=0}')
def rgb565(v):
    r,g,b=v>>16&255,v>>8&255,v&255
    return ((r>>3)*255//31,(g>>2)*255//63,(b>>3)*255//31)
def luminance(v):
    a=[x/255 for x in rgb565(v)];a=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in a]
    return sum(x*y for x,y in zip(a,(.2126,.7152,.0722)))
lowest=100
for q in range(21):
    p=lua.execute(f'g.night={q}/20;return art.background(c,g)'.encode())
    a,b=sorted((luminance(p[1]),luminance(p[2])))
    ratio=(b+.05)/(a+.05);lowest=min(lowest,ratio)
    assert ratio>=4.5,(q,ratio)
print(f'PASS: text contrast >= {lowest:.2f}:1 through all 21 RGB565 palette steps')
