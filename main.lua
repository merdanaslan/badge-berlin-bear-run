-- Badge entry point: input, screens, saved preferences, and LED effects.
local screen = ui.canvas(32, 74, 128, 48, {scale = 2})
local Game, Art = require("game"), require("art")
local g = Game.new()
local state = "title" -- title, run, pause, result
local best, lights = storage.get("best"), storage.get("leds")
if type(best) ~= "number" or best ~= best or best < 0
    or best > 999999 or best ~= math.floor(best) then
  best = 0
end
if type(lights) ~= "boolean" then lights = true end
local downUntil, record = 0, false

-- Patterns 1..4: start, crash, crash + record sweep, 100-point pulse.
-- A zero ID cancels. With no ID, advance one step when its deadline arrives.
-- Each packed step is [50ms ticks, LED index (0 = all), red, green, blue].
local effects = assert(fs.read("leds.bin"))
local effectPos, effectAt = 0, 0
local function effect(id)
  if id then
    led.off()
    effectPos = id > 0 and lights and effects:byte(id) + 1 or 0
    effectAt = 0
  end
  local now = sys.millis()
  if effectPos > 0 and now >= effectAt then
    local ticks, index, r, green, b = effects:byte(effectPos, effectPos + 4)
    led.off()
    if ticks == 0 then
      effectPos = 0
    else
      if index == 0 then led.fill(r, green, b) else led.set(index, r, green, b) end
      effectPos = effectPos + 5
      effectAt = now + ticks * 50
    end
  end
end

local lastBg, lastScore, lastScene = -1, -1, -1
local score = ui.label(12, 10, "", {size = 14, mono = true, w = 296, align = "right"})
local function label(y, size)
  return ui.label(0, y, "", {size = size, w = 320, align = "center"})
end
local title, sub, action, hint = label(35, 20), label(58, 12), label(182, 12), label(202, 12)

local function draw()
  local p = Art.background(screen, g)
  Art.bear(screen, g, state == "result", state == "title")
  Art.hazards(screen, g)
  if lastBg ~= p[1] then
    ui.bg(p[1])
    score:color(p[2]); title:color(p[2]); sub:color(p[2])
    action:color(p[2]); hint:color(p[2])
    lastBg = p[1]
  end
  if lastScore ~= g.score then
    score:text(string.format("HI %05d   %05d", best, g.score))
    lastScore = g.score
  end
  if state == "run" and lastScene ~= g.scene then
    action:text(g.scene == 1 and "" or Art.name(g.scene))
    lastScene = g.scene
  end
end

local function show()
  title:show(state ~= "run")
  sub:show(state ~= "run")
  if state == "title" then
    title:text("BERLIN BEAR RUN"); sub:text("SUPERTEAM GERMANY")
    action:text("SELECT / UP to start")
  elseif state == "pause" then
    title:text("PAUSED"); sub:text("SELECT to resume")
    action:text("RIGHT LEDs " .. (lights and "ON" or "OFF") .. "   CANCEL exit")
  elseif state == "result" then
    title:text("RUN IT BACK")
    sub:text(record and "NEW HIGH SCORE" or "BERLIN ISN'T GOING ANYWHERE")
    action:text("SELECT / UP to retry")
  else
    lastScene = -1
  end
  hint:text(state == "run" and "UP jump   DOWN duck   CANCEL pause" or "UP jump   DOWN duck")
  draw()
end

local function start()
  Game.reset(g)
  state, record, downUntil = "run", false, 0
  lastScore = -1
  effect(1)
  show()
end

function on_key(key, rep)
  -- Firmware exposes press/repeat, without key-up. Repeats renew a hold lease.
  if key == "down" and state == "run" then
    downUntil = sys.millis() + (rep and 150 or 460)
    Game.down(g, true)
    draw()
    return true
  end
  if rep then return true end
  if key == "back" then
    if state ~= "run" then sys.exit(); return true end
    Game.down(g, false)
    downUntil, state = 0, "pause"
    effect(0)
  elseif key == "select" then
    if state == "pause" then
      state = "run"
    elseif state ~= "run" then
      start()
      return true
    end
  elseif key == "up" then
    if state == "title" or state == "result" then
      start()
      return true
    elseif state == "run" then
      downUntil = 0
      Game.down(g, false)
      Game.jump(g)
    end
  elseif key == "right" and state ~= "run" then
    lights = not lights
    storage.set("leds", lights)
    effect(0)
  end
  show()
  return true
end

function on_tick(ms)
  if state == "run" then
    if downUntil > 0 and sys.millis() >= downUntil then
      downUntil = 0
      Game.down(g, false)
    end
    local previousHundred = g.score // 100
    Game.update(g, ms / 1000)
    if g.dead then
      state, downUntil = "result", 0
      record = g.score > best
      if record then
        best = g.score
        storage.set("best", best)
      end
      effect(record and 3 or 2)
      lastScore = -1
      show()
    else
      if g.score // 100 > previousHundred then effect(4) end
      draw()
    end
  end
  -- Keep result-screen celebrations running after gameplay stops.
  effect()
end

function on_exit() led.off() end
show()
