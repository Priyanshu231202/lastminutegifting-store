#!/usr/bin/env python3
"""Draw stand-in hamper photos for every box and item combination.

These are only so the builder works before the real photos are shot. Each file
uses the same name a real photo will use, so dropping real photos in later
replaces them one by one.

    python3 tools/hamper/make_samples.py public_html
"""
import itertools, json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'public_html')
S = 900
DATA = json.load(open(os.path.join(HERE, 'hampers.json')))
STYLE = {  # base colour, rim colour, lining colour
    'kraft': ((196, 152, 100), (150, 108, 64), (232, 212, 182)),
    'royal': ((92, 30, 110), (214, 170, 72), (128, 52, 146)),
}
FONT = None
for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
    if os.path.exists(f): FONT = ImageFont.truetype(f, 22); break
FONT = FONT or ImageFont.load_default()


def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    out = Image.new('RGBA', im.size); out.paste(im, (0, 0), m); return out


def slots(n):
    """Item tile boxes (x, y, size) inside the tray area 150..750."""
    if n == 1: return [(300, 300, 300)]
    if n == 2: return [(175, 330, 260), (465, 330, 260)]
    if n == 3: return [(175, 200, 260), (465, 200, 260), (320, 480, 260)]
    return [(175, 190, 260), (465, 190, 260), (175, 470, 260), (465, 470, 260)]


def draw(box, ids):
    base, rim, lining = STYLE.get(box['id'], STYLE['kraft'])
    im = Image.new('RGB', (S, S), (246, 244, 251))
    sh = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((110, 140, 800, 830), 40, fill=(0, 0, 0, 90))
    im.paste(sh.filter(ImageFilter.GaussianBlur(24)), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((100, 110, 800, 810), 40, fill=rim)
    d.rounded_rectangle((128, 138, 772, 782), 28, fill=base)
    d.rounded_rectangle((150, 160, 750, 760), 20, fill=lining)
    if not ids:  # empty box: ribbon across
        d.rectangle((420, 110, 480, 810), fill=(214, 60, 60)); d.rectangle((100, 430, 800, 490), fill=(214, 60, 60))
        d.ellipse((380, 390, 520, 530), fill=(190, 40, 40))
    for (x, y, s), i in zip(slots(len(ids)), ids):
        t = Image.open(os.path.join(SITE, DATA['items'][i]['photo'].lstrip('/'))).convert('RGB').resize((s, s), Image.LANCZOS)
        ts = Image.new('RGBA', (S, S), (0, 0, 0, 0)); ImageDraw.Draw(ts).rounded_rectangle((x + 6, y + 10, x + s + 6, y + s + 10), 22, fill=(0, 0, 0, 70))
        ts = ts.filter(ImageFilter.GaussianBlur(10)); im.paste(ts, (0, 0), ts)
        t = rounded(t, 22); im.paste(t, (x, y), t)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((640, 846, 880, 884), 19, fill=(22, 19, 31)); d.text((760, 865), 'SAMPLE PHOTO', fill=(255, 210, 63), font=FONT, anchor='mm')
    return im


n = 0
for box in DATA['boxes']:
    out = os.path.join(SITE, DATA['photoDir'].lstrip('/'), box['id']); os.makedirs(out, exist_ok=True)
    combos = [()] + [c for k in range(1, box['max'] + 1) for c in itertools.combinations(sorted(box['items'], key=int), k)]
    for c in combos:
        name = '-'.join(c) if c else 'box'
        draw(box, list(c)).save(os.path.join(out, name + '.webp'), 'WEBP', quality=74, method=6); n += 1
print(n, 'sample photos written')
