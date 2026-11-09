"""Package the game and its license; verify every ZIP member."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json

ROOT = Path(__file__).resolve().parents[1]
files = {name: ROOT / name for name in ('app.json', 'main.lua', 'game.lua', 'art.lua')}
files.update((name, ROOT / 'assets' / name) for name in (
    'art.bin', 'sprites.bin', 'scenes.idx', 'sprites.idx', 'colors.bin', 'route.bin', 'leds.bin'
))
license_text = (
    b'Code and documentation: MIT. Artwork and branding are excluded and retain their existing rights.\n\n'
    + (ROOT / 'LICENSE').read_bytes()
)
manifest = json.loads((ROOT / 'app.json').read_text())
assert manifest['id'] == 'berlin-bear-run' and len(manifest['name']) <= 20

# Flatten the generated assets for the badge's existing fs.read paths.
# Do not include source images, Python tools, tests, or the README.
package = ROOT / 'berlin-bear-run.zip'
with ZipFile(package, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for name, source in files.items():
        archive.write(source, name)
    archive.writestr('license.txt', license_text)
with ZipFile(package) as archive:
    assert archive.testzip() is None and archive.namelist() == list(files) + ['license.txt']
    for name, source in files.items():
        assert archive.read(name) == source.read_bytes()
    assert archive.read('license.txt') == license_text
print(f'PASS: {package.name}, {package.stat().st_size} bytes, {len(files) + 1} packaged files, byte-verified')
