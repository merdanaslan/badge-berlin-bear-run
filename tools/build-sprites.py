"""Prepare the generated character sheet and original Summit car for RGB565 Lua.

Only crop, resize, palette quantization and lossless row-RLE are performed here.
The original generated sheet and prompt are preserved under assets/source/.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
COLORS = [0x141415,0x2D2C2D,0x4A4741,0x4E3917,0x704F16,
          0x936818,0xB2801D,0xCF9D30,0xE7B538,0xF9CF65,0x9C8452,
          0xCBB77F,0x5D5742,0xB22919,0xFDE5A3]
palette = [tuple((v >> s) & 255 for s in (16,8,0)) for v in COLORS]

def encode(im, monochrome=False):
    im = im.convert('RGBA')
    w,h = im.size
    out = bytearray()
    for y in range(h):
        row=[]
        for x in range(w):
            r,g,b,a=im.getpixel((x,y))
            ink=0 if a<110 else (13 if monochrome else 1+min(range(15),key=lambda i:sum((a-b)**2 for a,b in zip((r,g,b),palette[i]))))
            row.append(ink)
        if monochrome and 13<=y<18:
            # At 88x18, resampling fills the R's right edge. Restore its
            # left stem and descending right leg in the tiny GERMANY caption.
            glyph=("###.","#..#","###.","#.#.","#..#")[y-13]
            row[60:66]=[0]+[13 if pixel=="#" else 0 for pixel in glyph]+[0]
        x=0
        while x<w:
            n=1
            while x+n<w and n<15 and row[x+n]==row[x]: n+=1
            out.append(n*16+row[x]); x+=n
    return bytes((w,h,len(out)%256,len(out)//256))+out

sheet = Image.open(ASSETS/'source/bear-sheet.png').convert('RGBA')
sprites=[]
for i in range(12):
    cell=sheet.crop((i%4*362,i//4*362,i%4*362+362,i//4*362+362))
    if i==10:
        # A genuine squat pose at the lower, forgiving duck silhouette.
        crop=cell.crop((58,96,301,334)).resize((14,14),Image.Resampling.LANCZOS)
        im=Image.new('RGBA',(24,27)); im.alpha_composite(crop,(5,13))
    else:
        # A single shared crop/scale preserves the run's limb reach and body bob.
        im=cell.crop((36,16,326,342)).resize((24,27),Image.Resampling.LANCZOS)
    sprites.append(im)
car=Image.open(ASSETS/'source/summit-car.png').convert('RGBA')
car=car.crop(car.getbbox()).resize((68,20),Image.Resampling.LANCZOS)
sprites.append(car)
logo=Image.open(ASSETS/'source/germany-wordmark.png').convert('RGBA')
logo=logo.resize((88,18),Image.Resampling.LANCZOS)
sprites.append(logo)
records=[encode(s,i==13) for i,s in enumerate(sprites)]
data=b''.join(records)
(ASSETS/'sprites.bin').write_bytes(data)
print(f'14 sprites, {len(data)} bytes -> sprites.bin')

index=bytearray();offset=0
for encoded in records:
    w,h,a,b=encoded[:4];n=a+b*256
    index.extend((w,h,(offset+4) & 255,(offset+4)//256,a,b));offset+=len(encoded)
(ASSETS/'sprites.idx').write_bytes(index)
