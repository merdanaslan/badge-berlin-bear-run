-- Execute production main.lua with a controlled clock/game and LED spies.
-- These desktop tests check event timing, priority, and saved preferences.
local source=assert(io.open("main.lua")):read("*a")
local patterns=assert(io.open("assets/leds.bin","rb")):read("*a")
local function fixture(best,enabled)
  local now,pixels,saved=0,{}, {best=best or 999,leds=enabled~=false}
  local g={score=0,scene=1};local nextScore,nextDead
  local function off() for i=1,8 do pixels[i]="off" end end
  off()
  local G={new=function() return g end,reset=function()
    g.score,g.dead,g.scene=0,false,1;nextScore,nextDead=nil,nil
  end,update=function()
    if nextScore then g.score=nextScore end
    g.dead=nextDead
    nextScore,nextDead=nil,nil
  end,down=function() end,jump=function() end}
  local noop=function() end
  local label={text=noop,color=noop,show=noop}
  local A={background=function() return {0,1} end,
    bear=noop,hazards=noop,name=function() return "SCENE" end}
  local env=setmetatable({
    ui={canvas=function() return {} end,bg=noop,label=function() return label end},
    storage={get=function(k) return saved[k] end,set=function(k,v) saved[k]=v end},
    fs={read=function(n) assert(n=="leds.bin");return patterns end},
    sys={millis=function() return now end,exit=function() off() end},
    led={off=off,fill=function(r,g,b)
      for i=1,8 do pixels[i]=r..","..g..","..b end
    end,set=function(i,r,g,b) assert(i>=1 and i<=8);pixels[i]=r..","..g..","..b end},
    require=function(n) return n=="game" and G or A end,
  },{__index=_G})
  assert(load(source,"@main.lua","t",env))()
  return {
    key=function(k) env.on_key(k,false) end,
    tick=function(ms,score,dead)
      now=now+ms;nextScore,nextDead=score,dead;env.on_tick(ms)
    end,
    all=function(color) for i=1,8 do assert(pixels[i]==color,pixels[i].." ~= "..color) end end,
    one=function(index,color)
      for i=1,8 do assert(pixels[i]==(i==index and color or "off")) end
    end,
    exit=function() env.on_exit() end,saved=saved,
  }
end
local purple,green,amber,gold="64,8,112","10,90,45","100,45,5","140,90,18"
local f=fixture();f.key("select");f.all(purple)
f.tick(249);f.all(purple);f.tick(1);f.all(green)
f.tick(249);f.all(green);f.tick(1);f.all("off")
print("PASS start: 250ms purple + 250ms green, then off")
f.tick(1,12,true);f.all(amber);f.tick(799);f.all(amber);f.tick(1);f.all("off")
print("PASS ordinary crash: full 800ms amber, then off")
f=fixture(0);f.key("select");f.tick(1,12,true);f.all(amber)
assert(f.saved.best==12);f.tick(799);f.all(amber);f.tick(1);f.one(1,gold)
for i=2,8 do f.tick(100);f.one(i,gold) end
f.tick(99);f.one(8,gold);f.tick(1);f.all("off")
f.key("select");f.tick(1,12,true);f.tick(800);f.all("off")
print("PASS new record: 800ms crash + eight 100ms gold steps; tied score is not a record")
f=fixture();f.key("select");f.tick(250);f.tick(250);f.tick(1,99);f.all("off")
f.tick(1,100);f.all(green);f.tick(199,101);f.all(green);f.tick(1,102);f.all("off")
f.tick(1,200);f.all(green);f.tick(200);f.all("off")
print("PASS each 100-point boundary: one 200ms pulse, no retrigger within a bucket")
f=fixture(0);f.key("select");f.tick(1,100,true);f.all(amber)
f.key("select");f.all(purple);f.key("back");f.all("off")
f.tick(2000);f.all("off");f.key("select");f.tick(2000);f.all("off")
print("PASS crash overrides milestone; retry replaces celebration; pause cancels effect")
f=fixture(0,false);f.key("select");f.all("off");f.tick(1,100);f.all("off")
f.tick(1,101,true);f.all("off");f.tick(2000);f.all("off")
f.key("right");assert(f.saved.leds==true);f.key("select");f.all(purple)
f.key("back");f.key("right");assert(f.saved.leds==false);f.all("off")
f.exit();f.all("off")
print("PASS saved LEDs-off suppresses every effect; toggle and exit clear LEDs")
print("ALL LED EVENT CHECKS PASSED")
