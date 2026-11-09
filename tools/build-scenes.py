"""Bake shaded landmarks into compact commands; no runtime art authoring."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)
glyphs=[]
cmd=[]
def r(x,y,w,h,c):
    assert w>0 and h>0
    cmd.append(bytes((16+c,x+64,y+64,w+64,h+64)))
def l(x,y,a,b,c):cmd.append(bytes((32+c,x+64,y+64,a+64,b+64)))
def dot(x,y,c):r(x,y,1,1,c)
def disk(x,y,rad,c):
    for dy in range(-rad,rad+1):
        w=int((rad*rad-dy*dy)**.5);r(x-w,y+dy,w*2+1,1,c)
def done():
    assert len(cmd)<256,len(cmd)
    glyphs.append(bytes((len(cmd),))+b''.join(cmd));cmd.clear()

# 1: sandstone gate, six shaded columns, cornices and Quadriga silhouette.
r(0,39,64,2,3);r(2,37,60,2,4);l(2,37,61,37,5)
r(2,15,60,5,3);r(4,13,56,3,4);l(4,13,59,13,5)
r(7,11,50,2,4);l(7,11,56,11,5);r(23,8,18,3,4)
for i in range(6):
    x=6+i*9
    r(x,20,5,17,3);r(x,20,3,17,4);l(x,21,x,36,5)
    r(x-1,19,7,2,5);r(x-1,36,7,1,5)
for i in range(4):
    l(26+i*3,5,27+i*3,7,3);dot(26+i*3,4,3)
l(32,2,32,8,3);l(29,4,35,4,3);dot(31,1,13);dot(33,1,13)
for x in range(9,56,7):dot(x,15,5);l(x,18,x+3,18,7)
done()

# 2: Fernsehturm sphere, spire and tapered supports above Berlin rooftops.
for x,w,h in ((0,12,8),(14,10,5),(27,9,9),(40,14,7),(56,9,10)):
    r(x,41-h,w,h,3);l(x,41-h,x+w-1,41-h,5)
    for wx in range(x+2,x+w-1,4):dot(wx,37,6);dot(wx,39,6)
l(32,0,32,32,3);l(33,2,33,30,5);r(31,6,3,2,4)
disk(32,17,6,3);disk(31,16,5,4);l(27,14,35,14,5)
l(27,18,37,18,7);l(29,21,35,21,5)
for y in range(23,41):
    w=1+(y-23)//7;r(32-w,y,w*2+1,1,3);dot(32-w,y,5)
done()

# 3: brick Oberbaum bridge, four arched spans, cylindrical twin towers.
r(0,26,84,14,3);r(0,27,84,11,4);l(0,25,83,25,5)
for x in range(0,84,4):r(x,23,1,3,3);dot(x,23,5)
for x in range(4,80,20):
    r(x,34,12,7,1);r(x+1,32,10,2,1);r(x+3,31,6,1,1)
    l(x,33,x,39,7);l(x+1,31,x+3,30,5);l(x+3,30,x+9,30,5)
for y in (28,35,38):
    for x in range((y%2)*3,84,7):l(x,y,min(x+3,83),y,7)
for x in (14,59):
    r(x,13,11,18,3);r(x+1,14,7,16,4);l(x+1,14,x+1,29,5)
    for y in range(10):
        w=1+2*(y//2);r(x+5-w//2,3+y,w,1,7);dot(x+5-w//2,3+y,5)
    r(x-1,12,13,2,3);l(x-1,12,x+11,12,5)
    r(x-1,28,13,2,3);l(x-1,28,x+11,28,5)
    r(x+4,17,3,6,7);dot(x+5,18,6)
    for yy in (16,24,26):l(x+2,yy,x+8,yy,5)
    dot(x+2,13,6);dot(x+8,13,6)
l(0,41,83,41,5);done()

# 4: warm brick Spree warehouse behind the exact website Aventador.
r(0,17,62,23,3);r(1,18,59,21,4);r(3,14,56,3,7)
l(0,17,61,17,5);l(3,14,58,14,5)
for y in (21,29):
    for x in range(4,60,7):
        r(x,y,4,5,3);r(x,y,2,4,6);l(x+1,y,x+1,y+3,7)
for y in (19,27,35,38):l(1,y,59,y,7)
l(0,40,61,40,5);done()

# 5: actual Superteam monogram on a shaded community sign.
r(2,12,56,27,7);r(3,13,54,24,7);l(3,13,56,13,5);l(3,13,3,36,5)
r(7,39,2,3,3);r(51,39,2,3,3)
rows=['...########..########.....','.##########..########.....',
'###########..########.....','###########..#############',
'###########..#############','###########..#############',
'###########..#############','.##########..#############',
'.##########..############.','..#########..###########..',
'###########..##########...','#########....########.....',
'##########...########.....','##########...########.....',
'###########..########.....','###########..########.....',
'###########..########.....','###########...#######.....',
'###########...#######.....','##########.....######.....',
'########........#####.....']
for y,row in enumerate(rows):
    for match in re.finditer('#+',row):r(16+match.start(),15+y,match.end()-match.start(),1,13)
done()

# 6/7: gold/orange birds with a contrasting outline in both wing positions.
# Warm fills separate hazards from the neutral skyline; hitboxes stay unchanged.
for flap in (0,1):
    l(9,4,13,2,2);l(9,5,13,3,2);l(10,4,12,3,13)
    r(3,2,7,5,2);r(3,3,7,3,13);r(4,5,5,1,12)
    disk(2,3,2,2);r(1,2,3,3,13);dot(1,2,7);dot(-1,4,12)
    if flap:
        l(5,3,8,8,2);l(6,3,11,7,2)
        l(5,4,8,7,12);l(6,4,10,6,13);dot(7,5,6)
    else:
        l(5,3,7,-3,2);l(6,3,10,-2,2)
        l(6,2,8,-2,12);l(7,2,9,-1,13);dot(7,0,6)
    done()
# 8: striped roadwork barricade with shaded edge and feet.
r(2,4,2,6,2);r(10,4,2,6,2);r(0,9,5,1,7);r(9,9,5,1,7)
r(0,0,14,5,2);r(1,1,12,3,6)
for x in (1,6,11):
    l(x,3,min(x+2,12),1,13);l(x+1,3,min(x+3,12),1,13)
dot(1,0,13);dot(12,0,13);done()
# 9: shaded cone and reflective band.
r(0,7,8,1,2)
for y in range(7):
    w=2+2*(y//2);x=4-w//2;r(x,y,w,1,12);dot(x,y,13)
r(2,4,4,1,6);l(0,7,6,7,7);done()
# 10: striped Berlin bollard, cap and side shading.
r(1,0,4,9,2);r(1,1,2,7,6);r(1,2,4,2,12);r(1,6,4,2,12)
dot(1,0,13);r(0,9,6,1,7);done()
# 11: rounded filled clouds with a shaded underside.
disk(9,5,4,11);disk(17,4,5,11);disk(24,6,3,11);r(3,6,27,3,11)
disk(8,4,3,10);disk(16,3,4,10);disk(23,5,3,10);r(3,5,25,2,10)
l(7,1,10,1,6);l(14,0,18,0,6);done()
# 12: shaded moon.
disk(6,6,5,10);disk(4,4,4,6);r(7,4,2,2,11);dot(4,8,11);done()

# 13: a round late-afternoon sun.
disk(6,6,5,5);disk(5,5,4,6);done()

# 14: separate Superteam Germany roadside sign; original wordmark is sprite 14.
r(0,15,96,25,7);l(0,15,95,15,5);l(0,15,0,39,5)
r(7,40,2,2,7);r(86,40,2,2,7);done()

# 15: Reichstag: broad classical facade, portico and ribbed glass dome.
r(0,38,90,3,3);r(2,37,86,1,5);r(4,21,82,16,4)
for x in (3,72):
    r(x,16,15,21,3);r(x+1,17,11,20,4);l(x,16,x+14,16,5)
    r(x+2,14,11,2,5);r(x+3,13,9,1,3)
    l(x+7,4,x+7,13,7)
    r(x+8,4,7,1,7);r(x+8,5,7,1,12);r(x+8,6,7,1,13)
for y in (24,31):
    for x in range(8,83,8):
        r(x,y,3,4,7);l(x,y,x,y+2,5)
l(4,21,85,21,5);l(4,29,85,29,3)
# Curved dome with blue glazing, pale metal ribs and a dark lantern.
for y,w in ((9,5),(10,9),(11,13),(12,17),(13,21),(14,23),(15,25),(16,27),(17,27),(18,27)):
    r(45-w//2,y,w,1,0)
l(45,9,45,18,6);l(42,10,39,18,5);l(48,10,51,18,5)
l(38,12,34,18,5);l(52,12,56,18,5)
l(35,15,55,15,5);r(31,19,29,2,3);l(31,19,59,19,5)
r(43,7,5,2,7);l(43,7,47,7,5)
# Pediment and six columns in front of the central entrance.
for y,w in ((21,5),(22,11),(23,17),(24,23),(25,29)):r(45-w//2,y,w,1,5)
l(32,25,58,25,3);r(33,26,25,11,7)
for x in (33,38,43,48,53,58):r(x,26,2,11,5);l(x+1,27,x+1,36,4)
r(28,37,36,1,5);r(25,39,42,1,5);done()

# 16: Victory Column: winged golden Victoria above a fluted stone column.
r(12,39,42,2,3);r(16,37,34,2,4);l(16,37,49,37,5)
r(21,31,24,6,3);r(22,32,21,5,4);l(22,32,42,32,5)
r(24,29,18,2,5);r(28,15,10,14,3);r(29,15,7,14,4)
for x in (29,32,35):l(x,16,x,28,5)
for y in (17,22,27):r(28,y,10,1,13)
r(26,13,14,2,5);r(28,12,10,1,3)
# Victoria's wings, head, gown, raised arm and laurel wreath.
l(32,6,26,1,13);l(32,7,25,3,13);l(32,8,26,5,13)
l(34,6,39,1,13);l(34,7,40,3,13);l(34,8,39,5,13)
r(32,4,3,3,13);dot(33,3,6);l(33,6,31,11,13);r(31,10,6,2,13)
l(34,6,38,7,13);l(38,7,40,4,13);l(40,4,40,1,13)
dot(39,0,13);dot(41,0,13);dot(38,1,13);dot(42,1,13);dot(39,2,13);dot(41,2,13)
l(33,7,33,10,6);l(32,13,32,28,6);done()

# 17: East Side Gallery: a long capped concrete wall with original mural art.
r(0,23,94,18,3);r(1,24,92,15,5);l(0,22,93,22,5)
r(0,40,94,1,7)
for x in range(1,94,6):l(x,24,x,38,4)
# Abstract sun/river mural, heart mural and dancing figures (original designs).
r(3,25,27,12,0);r(4,33,25,3,4);disk(10,28,3,13)
l(4,35,12,31,6);l(12,31,20,35,6);l(20,35,28,30,6)
r(32,25,27,12,6)
for y,x,w in ((27,37,6),(27,47,6),(28,36,18),(29,36,18),(30,37,16),(31,38,14),(32,39,12),(33,40,10),(34,42,6),(35,44,2)):
    r(x,y,w,1,12)
r(61,25,29,12,0);r(63,34,25,2,13)
for x,c in ((68,6),(81,13)):
    disk(x,28,1,c);l(x,30,x,33,c);l(x-4,30,x+4,31,c)
    l(x,33,x-3,36,c);l(x,33,x+3,36,c)
for x in range(0,94,6):dot(x,23,6)
done()

# 18..81: a clipped yellow U-Bahn crossing the upper bridge deck.
# Bake its motion offline so no clipping helpers/vehicle state consume Lua heap.
for frame in range(64):
    tx=-38+frame*2
    def tr(x,y,w,h,c):
        left=max(0,tx+x);right=min(84,tx+x+w)
        if right>left:r(left,y,right-left,h,c)
    for car in (0,19):
        tr(car,0,17,1,7);tr(car,1,17,6,13);tr(car+1,7,15,1,7)
        for wx in (1,5,12):
            tr(car+wx,2,3,3,7);tr(car+wx,2,2,2,0);tr(car+wx,2,1,1,6)
        tr(car+9,1,2,6,7);tr(car+9,2,1,3,0)
        tr(car+2,7,2,1,2);tr(car+13,7,2,1,2)
    tr(17,5,2,1,7);tr(35,5,1,1,6)
    done()

out=b''.join(glyphs)
(ASSETS/'art.bin').write_bytes(out)
print(f'{len(glyphs)} shaded glyphs, {sum((len(g)-1)//5 for g in glyphs)} commands, {len(out)} bytes -> art.bin')

index=bytearray();offset=0
for g in glyphs:
    n=len(g)-1;index.extend((offset+1 & 255,(offset+1)//256,n & 255,n//256));offset+=len(g)
(ASSETS/'scenes.idx').write_bytes(index)
