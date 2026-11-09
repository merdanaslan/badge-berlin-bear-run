"""Pack the route catalogue and small LED timelines for the memory-limited badge."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)
scenes=[
    (14,14,4,18,'SUPERTEAM GERMANY'),
    (3,0,0,0,'OBERBAUM BRIDGE'),
    (1,0,0,0,'BRANDENBURG GATE'),
    (15,0,0,0,'REICHSTAG'),
    (16,0,0,0,'VICTORY COLUMN'),
    (2,0,0,0,'BERLIN TV TOWER'),
    (17,0,0,0,'EAST SIDE GALLERY'),
    (4,13,-4,22,'SOLANA SUMMIT'),
    (5,0,0,0,'SUPERTEAM'),
]
names=bytearray();route=bytearray([len(scenes)])
for glyph,sprite,x,y,name in scenes:
    b=name.encode('ascii');route.extend((glyph,sprite,x+64,y,len(scenes)*6+1+len(names),len(b)));names.extend(b)
route.extend(names);assert len(route)<256
(ASSETS/'route.bin').write_bytes(route)
# 50ms ticks, LED zero means all eight; nonzero selects a single LED.
purple=(5,0,64,8,112);green=(5,0,10,90,45);crash=(16,0,100,45,5)
patterns=[[purple,green],[crash],[crash]+[(2,i,140,90,18) for i in range(1,9)],[(4,0,10,90,45)]]
leds=bytearray(4)
for i,steps in enumerate(patterns):
    leds[i]=len(leds)
    for step in steps:leds.extend(step)
    leds.append(0)
(ASSETS/'leds.bin').write_bytes(leds)
print(f'{len(scenes)} route scenes, {len(route)} bytes; 4 LED timelines, {len(leds)} bytes')
