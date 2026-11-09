"""Render both sides of every checkpoint and route wrap; reject large scene cuts."""
from pathlib import Path
from PIL import Image,ImageDraw
from lupa import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]

def renderer(path):
    lua=LuaRuntime(encoding=None);image=Image.new('RGB',(128,48));draw=ImageDraw.Draw(image)
    def read(name,offset=0,count=None):
        b=(path/'assets'/name.decode()).read_bytes();return b[offset:offset+count] if count is not None else b[offset:]
    def rect(x,y,w,h,color):
        if w>0 and h>0:draw.rectangle((x,y,x+w-1,y+h-1),fill=color)
    def line(x,y,a,b,color):draw.line((x,y,a,b),fill=color)
    # Pillow takes RGB tuples, whereas the Lua renderer returns 24-bit colors.
    def rgb(c):return (c>>16&255,c>>8&255,c&255)
    g=lua.globals();g[b'read_asset']=read
    g[b'rect']=lambda x,y,w,h,c:rect(x,y,w,h,rgb(c))
    g[b'line']=lambda x,y,a,b,c:line(x,y,a,b,rgb(c))
    g[b'clear']=lambda c:draw.rectangle((0,0,127,47),fill=rgb(c))
    g[b'point']=lambda x,y,c:draw.point((x,y),fill=rgb(c)) if 0<=x<128 and 0<=y<48 else None
    lua.execute(b'fs={read=read_asset}; c={}; function c:clear(a) clear(a) end;function c:rect(...) rect(...) end;function c:line(...) line(...) end;function c:pixel(...) point(...) end')
    source=(path/'art.lua').read_bytes();g[b'art']=lua.execute(source)
    def render(distance,night,time=0):
        scene=int(distance//600)%9+1
        lua.execute(f'art.background(c,{{distance={distance},night={night},time={time},scene={scene}}})'.encode())
        return image.copy()
    return render
def metrics(a,b):
    before=list(a.getdata());after=list(b.getdata());changed=unexplained=0
    for y in range(48):
        for x in range(127):
            i=y*128+x
            if after[i]!=before[i]:
                changed+=1
                # One-pixel leftward scrolling, or a stationary background layer.
                if after[i]!=before[i+1]:unexplained+=1
    return changed,unexplained
render=renderer(ROOT);largest_change=largest_residual=0
for night in (0,.5,1):
    for boundary in range(600,10801,600):
        changed,residual=metrics(render(boundary-.01,night),render(boundary+.01,night))
        largest_change=max(largest_change,changed);largest_residual=max(largest_residual,residual)
        assert residual<100,(boundary,night,residual)
print(f'PASS: 54 checkpoint/wrap comparisons; residual beyond stationary/1-pixel scrolling <= {largest_residual}/6096 pixels')
