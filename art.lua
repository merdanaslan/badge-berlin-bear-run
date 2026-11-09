-- Draw the world using small indexed asset reads; the Lua heap is only 48 KB.
-- Packed assets are authored in tools/; see README.md for the project layout.
local A = {}
local spriteIndex = assert(fs.read("sprites.idx"))
-- Nine 6-byte scene records plus the count byte; names are streamed separately.
local route = assert(fs.read("route.bin", 0, 55))
local p = {} -- current day/night palette

function A.name(i)
  local offset, size = route:byte(i * 6, i * 6 + 1)
  return fs.read("route.bin", offset, size)
end

local function palette(offset, out)
  local data = assert(fs.read("colors.bin", offset, 48))
  for i = 0, 15 do
    local r, green, b = data:byte(i * 3 + 1, i * 3 + 3)
    out[i] = r * 65536 + green * 256 + b
  end
end

-- Twenty-one 48-byte scene palettes precede the fixed bear/car palette.
local colors = {}
palette(1008, colors)
local phase = -1

local function glyph(c, id, x, y)
  -- Each index record contains little-endian 16-bit offset and length.
  local a, b, n, m = assert(fs.read("scenes.idx", id * 4 - 4, 4)):byte(1, 4)
  local data = assert(fs.read("art.bin", a + b * 256, n + m * 256))
  for i = 1, #data, 5 do
    local code, a, b, w, h = data:byte(i, i + 4)
    -- Low nibble = palette index; coordinates are biased by 64.
    if code < 32 then
      c:rect(x + a - 64, y + b - 64, w - 64, h - 64, p[code % 16])
    else
      c:line(x + a - 64, y + b - 64, x + w - 64, y + h - 64, p[code % 16])
    end
  end
end

local function sprite(c, id, x, y)
  local w, h, a, b, n, m = spriteIndex:byte(id * 6 - 5, id * 6)
  local pixels = assert(fs.read("sprites.bin", a + b * 256, n + m * 256))
  local col, row = 0, 0
  for i = 1, #pixels do
    local v = pixels:byte(i)
    local run, ink = v // 16, v % 16 -- zero ink is transparent
    if ink > 0 then
      -- Sprite 14 is the Germany wordmark, tinted with the scene's gold ink.
      c:rect(x + col, y + row, run, 1, id == 14 and p[13] or colors[ink])
    end
    col = col + run
    if col == w then col, row = 0, row + 1 end
  end
end

function A.background(c, g)
  local q = math.floor(g.night * 20)
  if q ~= phase then
    palette(q * 48, p)
    phase = q
  end
  c:clear(p[1])
  c:rect(0, 13, 128, 15, p[14])
  c:rect(0, 28, 128, 16, p[15])
  if q < 10 then
    glyph(c, 13, 106, 1) -- sun
  else
    glyph(c, 12, 106, 1) -- moon and stars
    for i = 0, 5 do c:pixel((i * 37 + 9) % 128, 2 + i % 3 * 4, p[10]) end
  end
  for i = 0, 1 do
    glyph(c, 11, (i * 87 + 8 - math.floor(g.distance / 35)) % 176 - 26, 4 + i * 7)
  end
  for i = 0, 6 do
    local x = (i * 23 - math.floor(g.distance / 65)) % 152 - 12
    c:rect(x, 35 - i % 3 * 2, 18, 6 + i % 3 * 2, p[3])
    c:line(x, 35 - i % 3 * 2, x + 17, 35 - i % 3 * 2, p[4])
  end

  -- Neighbouring landmarks share one strip; checkpoints only change captions.
  local cell, pan = math.floor(g.distance / 600), math.floor(g.distance * .2)
  for n = cell - 1, cell + 1 do
    local x = 28 + n * 120 - pan
    if n >= 0 and x > -100 and x < 132 then
      local id, s, dx, dy = route:byte(n % 9 * 6 + 2, n % 9 * 6 + 5)
      if id == 3 then -- bridge; clipped U-Bahn frames are glyphs 18..81
        local frame = math.floor(g.time * 20) % 80
        if frame < 64 then glyph(c, 18 + frame, x, 16) end
      end
      glyph(c, id, x, 0) -- draw towers over the train
      if s > 0 then sprite(c, s, x + dx - 64, dy) end
    end
  end
  c:rect(0, 42, 128, 2, p[7]); c:line(0, 42, 127, 42, p[5])
  c:rect(0, 44, 128, 4, p[8]); c:line(0, 44, 127, 44, p[13])
  for i = 0, 17 do
    local x = (i * 13 - math.floor(g.distance)) % 143 - 7
    c:line(x, 46 + i % 2, x + 4 + i % 3, 46 + i % 2, p[9])
  end
  return p
end

function A.bear(c, g, hit, idle)
  -- Frames 1..8 run, 9 idle, 10 jump, 11 crouch, 12 crash.
  local id = idle and 9 or 1 + math.floor(g.time * (12 + g.speed * .05)) % 8
  if hit then id = 12 elseif g.y < 0 then id = 10 elseif g.crouch then id = 11 end
  sprite(c, id, 18, math.floor(18 + g.y))
  if g.crouch and g.y == 0 and not hit then
    local step = math.floor(g.time * 10) % 2
    c:rect(24 + step, 43, 2, 2, colors[2])
    c:rect(31 - step, 43, 2, 2, colors[3])
  end
end

function A.hazards(c, g)
  for _, o in ipairs(g.obstacles) do
    if o.active then
      -- Kinds 1..3 use bollard/cone/barrier glyphs 10/9/8; 4 is a pigeon.
      glyph(c, o.kind == 4 and 6 + math.floor(g.time * 9) % 2 or 11 - o.kind,
        math.floor(o.x), o.y + 2)
    end
  end
end
return A
