-- All positions are in canvas pixels (2 display pixels). No badge APIs here.
local G = {
  X = 22, GROUND = 42, JUMP = 94, GRAVITY = 280,
  START_SPEED = 70, MAX_SPEED = 132, ACCELERATION = 2.8,
  SCENE_DISTANCE = 600, SCENES = 9,
}

function G.new()
  local g = {obstacles = {}}
  for i = 1, 4 do g.obstacles[i] = {active = false} end
  G.reset(g)
  return g
end

function G.reset(g)
  g.distance, g.score, g.time = 0, 0, 0
  g.speed, g.y, g.vy = G.START_SPEED, 0, 0
  g.crouch, g.held, g.dead = false, false, false
  g.spawn, g.scene, g.lap, g.night = 0, 1, 0, 0
  for _, o in ipairs(g.obstacles) do o.active = false end
end

function G.jump(g)
  if g.y == 0 and not g.dead then
    g.crouch, g.vy = false, -G.JUMP
    -- Mark airborne immediately: two presses between ticks cannot double-jump.
    g.y = -0.001
  end
end

function G.down(g, held)
  if g.dead then return end
  g.held = held == true
  g.crouch = g.held and g.y == 0
  if g.held and g.y < 0 then
    g.vy = math.max(g.vy, 130)
  end
end

local function spawn(g)
  local slot
  for _, o in ipairs(g.obstacles) do
    if not o.active then slot = o; break end
  end
  if not slot then return end
  local kind = 1 -- bollard, cone, barrier, pigeon
  if g.score >= 20 then kind = math.random(1, 3) end
  if g.score >= 55 and math.random(1, 4) == 1 then kind = 4 end
  local w, h, y = 6, 10, G.GROUND - 10
  if kind == 2 then w, h, y = 8, 8, G.GROUND - 8 end
  if kind == 3 then w, h, y = 14, 10, G.GROUND - 10 end
  if kind == 4 then
    w, h, y = 12, 7, G.GROUND - 19 -- mid: hold down to duck
    if g.score >= 150 then
      local height = math.random(1, 3)
      if height == 1 then y = G.GROUND - 8 end -- low: jump
      if height == 3 then y = G.GROUND - 33 end -- high: stay grounded
    end
  end
  slot.active, slot.kind, slot.x = true, kind, 138
  slot.w, slot.h, slot.y = w, h, y
  -- Reserve a full jump + 0.28 s recovery at the predicted next speed.
  local recovery = 2 * G.JUMP / G.GRAVITY + 0.28
  local nextSpeed = math.min(G.MAX_SPEED, g.speed + G.ACCELERATION * recovery)
  g.spawn = w + nextSpeed * recovery + math.random(0, 14)
end

local function step(g, dt)
  g.time = g.time + dt
  local phase = g.time % 40
  if g.time < 20 then
    g.night = 0
  elseif phase < 20 then
    g.night = math.max(0, 1 - phase / 1.2)
  else
    g.night = math.min(1, (phase - 20) / 1.2)
  end
  g.speed = math.min(G.MAX_SPEED, g.speed + G.ACCELERATION * dt)
  local travel = g.speed * dt
  g.distance = g.distance + travel
  g.score = math.min(99999, math.floor(g.distance / 8))
  local route = math.floor(g.distance / G.SCENE_DISTANCE)
  g.scene, g.lap = route % G.SCENES + 1, math.floor(route / G.SCENES)
  if g.y < 0 then
    g.y = g.y + g.vy * dt + G.GRAVITY * dt * dt / 2
    g.vy = g.vy + G.GRAVITY * dt
    if g.y >= 0 then
      g.y, g.vy = 0, 0
      g.crouch = g.held
    end
  end
  g.spawn = g.spawn - travel
  if g.spawn <= 0 then spawn(g) end
  -- Insets forgive transparent ears/paws. Crouch really lowers the hitbox.
  local px, pw = G.X + 3, 10
  local ph = g.crouch and g.y == 0 and 7 or 15
  local py = G.GROUND + g.y - ph
  for _, o in ipairs(g.obstacles) do
    if o.active then
      o.x = o.x - travel
      if o.x + o.w < 0 then o.active = false end
      if o.active and px < o.x + o.w - 0.5 and px + pw > o.x + 0.5
          and py < o.y + o.h - 0.5 and py + ph > o.y + 0.5 then
        g.dead = true
        return
      end
    end
  end
end

function G.update(g, seconds)
  -- 120 Hz collision substeps prevent tunnelling at the 20 Hz host tick.
  -- Discard long stalls rather than killing the player after tab suspension.
  local left = math.min(seconds, 0.15)
  while left > 0 and not g.dead do
    local dt = math.min(left, 1 / 120)
    step(g, dt)
    left = left - dt
  end
end

return G
