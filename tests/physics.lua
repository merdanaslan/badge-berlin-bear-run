-- Run as main.lua in a throwaway emulator app with game.lua bundled.
-- No mocks: exercise the same physics used by the game. One coroutine yield
-- per few frames keeps long scenarios inside the badge callback budget.
local G = require("game")
local function advance(g, seconds)
  for i = 1, math.ceil(seconds / 0.05) do
    G.update(g, 0.05)
    if i % 5 == 0 then coroutine.yield() end
  end
end
local function empty()
  local g = G.new()
  g.spawn = 1000000
  return g
end
local function hazard(g, kind, x, y, w, h)
  local o = g.obstacles[1]
  o.active, o.kind, o.x, o.y, o.w, o.h = true, kind, x, y, w, h
end
local function test(name, fn)
  fn()
  print("PASS " .. name)
end
local suite = coroutine.create(function()
  test("no double jump; stand from crouch", function()
    local g = empty()
    G.down(g, true); assert(g.crouch)
    G.jump(g); G.down(g, false); assert(not g.crouch and g.y < 0)
    G.update(g, 0.1)
    local y, vy = g.y, g.vy
    G.jump(g); assert(g.y == y and g.vy == vy)
    advance(g, 1)
    assert(g.y == 0 and not g.crouch)
  end)
  test("down repeats are idempotent; release stands", function()
    local g = empty()
    G.down(g, true); G.down(g, true); assert(g.crouch)
    G.down(g, false); assert(not g.crouch)
    G.jump(g); G.update(g, 0.1); G.down(g, true)
    assert(g.vy >= 75)
    advance(g, 0.2)
    assert(g.y == 0 and g.crouch)
    G.down(g, false); assert(not g.crouch)
  end)
  test("release before landing does not latch crouch", function()
    local g = empty()
    G.jump(g); G.update(g, 0.1); G.down(g, true); G.down(g, false)
    advance(g, 0.3)
    assert(g.y == 0 and not g.crouch)
  end)
  test("speed is challenging early; night fades independently of landmarks", function()
    local g = empty()
    advance(g, 10)
    assert(g.speed * 2 >= 190, "speed still too slow after ten seconds")
    advance(g, 9)
    assert(g.night == 0)
    advance(g, 1.5)
    assert(g.night > 0 and g.night < 1, "night should fade")
    advance(g, 1)
    assert(g.night == 1)
    advance(g, 3)
    assert(g.speed == G.MAX_SPEED)
    G.reset(g); assert(g.night == 0 and g.time == 0)
  end)
  test("mid pigeons hit standing; clear crouch", function()
    local g = empty()
    hazard(g, 4, G.X+20, G.GROUND-19, 12, 7)
    advance(g, 0.4); assert(g.dead)
    g = empty(); G.down(g, true)
    hazard(g, 4, G.X+20, G.GROUND-19, 12, 7)
    advance(g, 0.6); assert(not g.dead)
  end)
  test("high pigeon safe standing; low pigeon lethal", function()
    local g = empty()
    hazard(g, 4, G.X+20, G.GROUND-33, 12, 7)
    advance(g, 0.6); assert(not g.dead)
    g = empty(); G.down(g, true)
    hazard(g, 4, G.X+20, G.GROUND-8, 12, 7)
    advance(g, 0.4); assert(g.dead)
  end)
  test("all ground widths jumpable at every speed", function()
    for speed = G.START_SPEED, G.MAX_SPEED do
      for kind = 1, 3 do
        local w = kind == 3 and 14 or (kind == 2 and 8 or 6)
        local h = kind == 2 and 8 or 10
        local g = empty(); g.speed = speed
        -- Centre each obstacle's overlap window on the arc's apex.
        local x = G.X + 8 + speed * G.JUMP / G.GRAVITY - w / 2
        hazard(g, kind, x, G.GROUND-h, w, h)
        G.jump(g); advance(g, 1)
        assert(not g.dead, "unfair ground obstacle at speed " .. speed)
      end
    end
  end)
  test("substeps catch crossing a thin obstacle", function()
    local g = empty(); g.speed = G.MAX_SPEED
    hazard(g, 1, G.X+17, G.GROUND-10, 1, 10)
    G.update(g, 0.15); assert(g.dead)
  end)
  test("scene boundary preserves airborne player and obstacle", function()
    local g = empty(); g.distance = G.SCENE_DISTANCE-0.1
    hazard(g, 3, 140, G.GROUND-10, 14, 10)
    G.jump(g); G.update(g, 0.05)
    assert(g.scene == 2 and g.y < 0 and g.vy < 0)
    assert(g.obstacles[1].active and g.obstacles[1].x < 140)
    assert(g.score >= G.SCENE_DISTANCE/8 and g.speed > G.START_SPEED)
    g.distance = G.SCENE_DISTANCE*G.SCENES-0.1; G.update(g, 0.05)
    assert(g.scene == 1 and g.lap == 1)
  end)
  test("generated routes remain playable through the faster ramp", function()
    for seed = 1, 3 do
      math.randomseed(seed)
      local g, seen = G.new(), {}
      for frame = 1, 3000 do
        local next
        for _, o in ipairs(g.obstacles) do
          if o.active and o.x+o.w >= G.X+3 and (not next or o.x < next.x) then next = o end
        end
        local mid = next and next.kind == 4 and next.y == G.GROUND-19
        G.down(g, mid and next.x < G.X+g.speed*0.65 or false)
        if next and not mid and not (next.kind == 4 and next.y == G.GROUND-33)
            and next.x <= G.X+8+g.speed*G.JUMP/G.GRAVITY-next.w/2 then G.jump(g) end
        G.update(g, 1/30)
        assert(not g.dead, "route collision: seed "..seed.." frame "..frame)
        seen[g.scene] = true
        if frame%10 == 0 then coroutine.yield() end
      end
      for scene = 1, G.SCENES do assert(seen[scene]) end
      assert(g.lap >= 2 and g.speed == G.MAX_SPEED)
    end
  end)
  test("night fades back to day; game time freezes without updates", function()
    local g = empty(); g.time = 39.9
    G.update(g, 0.1); assert(g.night > 0.9)
    advance(g, 0.5); assert(g.night > 0 and g.night < 1)
    advance(g, 1); assert(g.night == 0)
    local t, d, n = g.time, g.distance, g.night
    G.update(g, 0); assert(g.time == t and g.distance == d and g.night == n)
  end)
  test("speed caps; distance score; reset reuses pool", function()
    local g = empty(); local first = g.obstacles[1]
    advance(g, 100)
    assert(g.speed == G.MAX_SPEED and g.score == math.floor(g.distance/8))
    G.reset(g)
    assert(g.score == 0 and not g.dead and g.speed == G.START_SPEED)
    assert(g.obstacles[1] == first and not first.active)
  end)
  print("ALL PHYSICS CHECKS PASSED")
end)
function on_tick()
  if coroutine.status(suite) == "dead" then return end
  local ok, err = coroutine.resume(suite)
  assert(ok, err)
end
