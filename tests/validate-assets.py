"""Check packed assets, approved bear artwork, route order, and LED timelines."""
from pathlib import Path
from hashlib import sha256
import struct,json
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"
scenes=(ASSETS/'art.bin').read_bytes();idx=(ASSETS/'scenes.idx').read_bytes()
assert len(idx)==81*4
for i in range(81):
    start,n=struct.unpack_from('<HH',idx,i*4)
    assert scenes[start-1]*5==n and start+n<=len(scenes)
    for offset in range(start,start+n,5):
        op,x,y,a,b=scenes[offset:offset+5]
        assert op//16 in (1,2) and 0<=op%16<=15
        if op//16==1:assert a>64 and b>64

def sprites(path):
    data=(path/'sprites.bin').read_bytes();idx=(path/'sprites.idx').read_bytes();result=[]
    for i in range(len(idx)//6):
        w,h,start,n=struct.unpack_from('<BBHH',idx,i*6)
        assert start+n<=len(data)
        x=y=0;pixels=[]
        for run in data[start:start+n]:
            count,ink=divmod(run,16);assert count>0
            x+=count;assert x<=w
            pixels.extend([ink]*count)
            if x==w:x=0;y+=1
        assert (x,y)==(0,h)
        result.append((w,h,data[start:start+n],pixels))
    return result
current=sprites(ASSETS)
approved=json.loads((ROOT/'tests/fixtures/approved-art.json').read_text())
assert len(current)==14 and len(approved['bear'])==12
for frame,reference in zip(current[:12],approved['bear']):
    assert frame[:2]==(reference['width'],reference['height'])
    assert sha256(frame[2]).hexdigest()==reference['sha256'],'approved bear artwork changed'
assert current[12][:2]==(68,20)
assert current[13][:2]==(88,18)
assert set(current[13][3])=={0,13}
# The tiny R must have a left stem and lower-right leg, without a solid right stem.
wordmark=current[13][3]
assert all(wordmark[y*88+61]==13 for y in range(13,18))
assert all(wordmark[y*88+64]==0 for y in (13,15,16))
assert wordmark[16*88+63]==13 and wordmark[17*88+64]==13
assert len({tuple(f[3][24*18:]) for f in current[:8]})==8
assert sha256((ASSETS/'colors.bin').read_bytes()[-45:]).hexdigest()==approved['palette_sha256']
assert (ASSETS/'colors.bin').stat().st_size==1056
route=(ASSETS/'route.bin').read_bytes();assert route[0]==9
names=[]
for i in range(9):
    glyph,sprite,x,y,offset,n=route[i*6+1:i*6+7]
    assert 1<=glyph<=17 and sprite in (0,13,14)
    assert 55<=offset<offset+n<=len(route)
    names.append(route[offset:offset+n].decode('ascii'))
assert names[:2]==['SUPERTEAM GERMANY','OBERBAUM BRIDGE'] and len(set(names))==9
assert route[7:11]==bytes((3,0,64,0)), 'second scene must draw the U-Bahn bridge'
assert {'REICHSTAG','VICTORY COLUMN','EAST SIDE GALLERY'}<=set(names)
leds=(ASSETS/'leds.bin').read_bytes();durations=[]
for pos in leds[:4]:
    duration=0
    while leds[pos]:
        ticks,index,r,g,b=leds[pos:pos+5];assert 0<=index<=8
        duration+=ticks*50;pos+=5
    durations.append(duration)
assert durations==[500,800,1600,200]
print('PASS: 81 glyphs / 14 sprites / 9 scenes / 4 LED timelines; Germany then U-Bahn bridge; approved bear and palette unchanged')
