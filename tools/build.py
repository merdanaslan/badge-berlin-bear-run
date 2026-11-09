"""Rebuild assets, run the checks, and create the importable badge ZIP."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true', help='Check existing assets/code without rebuilding the assets or ZIP.')
args = parser.parse_args()
os.chdir(ROOT)

def run(script):
    print(f'\n{script}', flush=True)
    subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)

if not args.check:
    for script in ('build-sprites.py', 'build-scenes.py', 'build-palettes.py', 'build-route-leds.py'):
        run('tools/' + script)

for script in ('validate-assets.py', 'scenery.py', 'contrast.py'):
    run('tests/' + script)

print('\nLua syntax, LED events, and physics', flush=True)
lua = LuaRuntime()
for name in ('main.lua', 'game.lua', 'art.lua'):
    lua.compile((ROOT / name).read_text(), name='@' + name)
lua.execute('dofile("tests/leds.lua")')
lua.execute('dofile("tests/physics.lua"); for i = 1, 10000 do on_tick() end')
assert lua.eval('require("game").SCENES') == (ROOT / 'assets/route.bin').read_bytes()[0]

if not args.check:
    run('tools/package.py')
print('\nAll desktop checks passed. Native emulator/device checks are separate.', flush=True)
