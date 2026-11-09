"""Prebake neutral day/night palettes; runtime loads only the current 48 bytes."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)
day=[0xF7F8FA,0x353941,0x8A8E95,0xB7BBC2,0xDDE0E5,0xF4E7CB,0x626A76,
     0xC3C7CE,0x949CA8,0xFFFFFF,0xD2D7DF,0xB55C31,0xE9B654,0xF1F3F6,0xEBEEF2]
night=[0x151921,0xE5E8ED,0x424956,0x636F7E,0x909CAA,0xE9C986,0x303845,
       0x292F3A,0x515D6E,0x8B96A4,0x485365,0xAD5731,0xE9B654,0x202733,0x2B3442]
sprites=[0x141415,0x2D2C2D,0x4A4741,0x4E3917,0x704F16,0x936818,
         0xB2801D,0xCF9D30,0xE7B538,0xF9CF65,0x9C8452,0xCBB77F,0x5D5742,0xB22919,0xFDE5A3]
def lum(v):
    r,g,b=(v>>16&255,v>>8&255,v&255)
    a=[(r>>3)*255/31,(g>>2)*255/63,(b>>3)*255/31]
    a=[x/255/12.92 if x/255<=.04045 else ((x/255+.055)/1.055)**2.4 for x in a]
    return sum(x*y for x,y in zip(a,(.2126,.7152,.0722)))
def contrast(a,b):
    a,b=sorted((lum(a),lum(b)));return (b+.05)/(a+.05)
values=[]
for q in range(21):
    palette=[]
    for a,b in zip(day,night):
        palette.append(sum((((a>>s&255)*(20-q)+(b>>s&255)*q)//20)<<s for s in (16,8,0)))
    preferred=day[1] if q<10 else night[1]
    palette[1]=next(c for c in (preferred,0x000000,0xFFFFFF) if contrast(palette[0],c)>=4.5)
    # Index zero is an extra glass/mural ink; transparent sprites still skip it.
    blue=sum((((0x3F8A9D>>s&255)*(20-q)+(0x76A7B7>>s&255)*q)//20)<<s for s in (16,8,0))
    values.extend([blue]+palette)
values+=[0]+sprites
(ASSETS/'colors.bin').write_bytes(b''.join(v.to_bytes(3,'big') for v in values))
print('21 neutral day/night palettes + unchanged sprite colors, 1056 bytes -> colors.bin')
