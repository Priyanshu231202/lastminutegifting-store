#!/usr/bin/env python3
"""Build the production /next-day-kits/ page: separate images, compiled Tailwind, deferred JS, hashed filenames."""
import glob, hashlib, io, json, os, re, shutil, subprocess
from PIL import Image, ImageChops

ROOT = '/home/claude/nextday'
OUT = os.path.join(ROOT, 'build', 'out')            # mirrors public_html
PAGE = os.path.join(OUT, 'next-day-kits')
IMGDIR = os.path.join(OUT, 'uploads', 'next-day')
CAT = '/home/claude/lmg/build/uploads/'
SIZE = 400

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(PAGE); os.makedirs(IMGDIR)


def square(path, fill_ratio=0.78, trim=True):
    im = Image.open(path).convert('RGB')
    if trim:
        box = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 14 else 0).getbbox()
        if box and (box[2] - box[0]) * (box[3] - box[1]) < 0.9 * im.size[0] * im.size[1]:
            im = im.crop(box)
    w, h = im.size
    if min(w, h) / max(w, h) > fill_ratio:
        s = min(w, h); im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    else:
        s = max(w, h); c = Image.new('RGB', (s, s), (255, 255, 255)); c.paste(im, ((s - w) // 2, (s - h) // 2)); im = c
    return im.resize((SIZE, SIZE), Image.LANCZOS)


def save(im, name):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=72, method=6)
    data = b.getvalue(); h = hashlib.md5(data).hexdigest()[:8]
    fn = f'{name}.{h}.webp'
    open(os.path.join(IMGDIR, fn), 'wb').write(data)
    return f'/uploads/next-day/{fn}'


# --- kit builder / hero images
KIT = {'key': 'catalogue/key-15.webp', 'bottle': 'catalogue/bot-001.webp', 'diary': 'catalogue/dg-01.webp', 'notebook': 'catalogue/nb-13.webp',
       'onyx': 'catalogue/nb-02.webp', 'card': 'catalogue/ch-01.webp', 'mug': 'catalogue/mug-011.webp', 'sling': 'catalogue/bag-305.webp',
       'hamper': 'diwali-gifting/1.webp', 'organiser': 'catalogue/dg-13.webp'}
IMG = {k: save(square(CAT + p), 'kit-' + k) for k, p in KIT.items()}

# --- event picks
products = {p['slug']: p for p in json.load(open('/home/claude/lmg/data.json'))['products']}
TRO = {'tro-medals': ('Medals with ribbons', 'catalogue/tro-medals.webp'), 'tro-cup': ('Trophy cups', 'catalogue/tro-cup.webp'),
       'tro-star': ('Star awards', 'catalogue/tro-star.webp'), 'tro-hero': ('Plaques & mementos', 'catalogue/tro-hero.webp')}
PICKS = {
    'university': ['bamboo-finish-diary-pen-set-dg-01', 'regal-notebook-n-36', 'premium-business-card-holder-w-07', 'tro-star', 'chevron-print-laptop-sleeve-bg-201', 'aura-bottle-bot-006'],
    'office': ['anti-theft-laptop-backpack-with-usb-bg-120', 'tan-leatherette-laptop-bag-bg-214', 'tan-organiser-diary-pen-set-dg-13', 'executive-card-holder-w-01', 'sip-master-tumbler-mug-002', 'executive-loop-keychain-k-20'],
    'govt': ['black-tan-organiser-gift-set-dg-35', 'tan-buckle-laptop-bag-bg-218', 'tro-hero', 'spice-and-tea-corporate-gift-box', 'atlas-notebook-n-43', 'classic-metal-card-holder-w-08'],
    'festival': ['colorful-diwali-treat-collection', 'saffron-celebration-gift-box', 'peacock-diya-decor-plate', 'almond-gift-pouch', 'floral-bottle-and-tumbler-set', 'mauve-ceramic-mug-pair'],
    'concert': ['bamboo-prime-keychain-k-10', 'eco-hook-keychain-k-30', 'chill-cup-mug-007', 'brown-flap-sling-bag-bg-302', 'bamboo-line-bottle-bot-002', 'cabin-travel-backpack-bg-105'],
    'live': ['thank-you-message-ceramic-mug', 'scented-candle-jar-gift-set', 'decorative-diya-platter', 'traditional-festive-snack-jar', 'lime-green-bento-lunch-box', 'home-loop-keychain-k-24'],
}
EV = {}
for cat, slugs in PICKS.items():
    arr = []
    for s in slugs:
        if s in TRO:
            n, p = TRO[s]; arr.append({'n': n, 'm': 1, 'i': save(square(CAT + p), 'ev-' + s)})
        else:
            p = products[s]; path = p['images'][0].replace('/uploads/', '').rsplit('.', 1)[0] + '.webp'
            arr.append({'n': p['name'], 'm': p.get('moq') or 1, 'i': save(square(CAT + path), 'ev-' + s)})
    EV[cat] = arr


def ufiles(grp):
    return sorted(f for f in glob.glob(f'/home/claude/evphotos/{grp}/**/*', recursive=True) if os.path.isfile(f))


S, C = ufiles('school'), ufiles('college')
SC = {'school': (S, [(0, 'Kids explorer gift box'), (4, 'Space stationery kit with tote'), (15, 'Space-theme gift hamper'), (11, 'Kids animal backpacks'), (9, 'Stationery gift box'), (2, "Children's Day printed mug"), (16, 'Return-gift treat cones'), (12, 'Class yearbooks & annual-day albums')]),
      'college': (C, [(0, 'Bottle, notebook & pen logo set'), (6, 'Laptop backpack with logo'), (12, 'Power bank with logo'), (1, 'Bamboo travel cable kit'), (10, 'Rechargeable clip-on LED lamp'), (11, 'Desk lamp with pen stand'), (13, 'Insulated lunch box set'), (19, 'Digital desk clock with logo')])}
for cat, (src, lst) in SC.items():
    EV[cat] = [{'n': n, 'm': 1, 'i': save(square(src[i]), f'ev-{cat}-{j}')} for j, (i, n) in enumerate(lst)]
EV = {k: EV[k] for k in ['school', 'college', 'university', 'office', 'govt', 'festival', 'concert', 'live']}

# --- split the template
t = open(os.path.join(ROOT, 'template.html'), encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', t, re.S).group(1)
script = re.findall(r'<script>(.*?)</script>', t, re.S)[-1]
markup = t[t.index('<div class="min-h-full">'):t.index('<script>\nconst IMG')]

# hero collage: real files, sized, first one prioritised
for k in ('diary', 'bottle', 'key', 'card'):
    markup = markup.replace('{{' + k + '}}', IMG[k])
markup = re.sub(r'(<img src="/uploads/next-day/kit-diary[^"]+")', r'\1 width="400" height="400" fetchpriority="high" decoding="async"', markup)
markup = re.sub(r'(<img src="/uploads/next-day/kit-(?:bottle|key|card)[^"]+")', r'\1 width="400" height="400" decoding="async"', markup)
assert '{{' not in markup

# JS: data as URLs, lazy images with dimensions
script = script.replace('const IMG = {{IMG_JSON}};', 'const IMG = ' + json.dumps(IMG) + ';')
script = script.replace('const EVPICKS = {{EVPICKS_JSON}};', 'const EVPICKS = ' + json.dumps(EV) + ';')
script = script.replace('<img src="${IMG[p.img]}" alt="" class="h-12 w-12', '<img src="${IMG[p.img]}" alt="" width="48" height="48" loading="lazy" decoding="async" class="h-12 w-12')
script = script.replace('<img src="${IMG[P[p].img]}" alt="" class="h-16 w-16', '<img src="${IMG[P[p].img]}" alt="" width="64" height="64" loading="lazy" decoding="async" class="h-16 w-16')
script = script.replace('<img src="${p.i}" alt="${p.n}" loading="lazy" class=', '<img src="${p.i}" alt="${p.n}" width="400" height="400" loading="lazy" decoding="async" class=')
assert '{{' not in script
js_hash = hashlib.md5(script.encode()).hexdigest()[:8]
open(os.path.join(PAGE, f'app.{js_hash}.js'), 'w').write(script)

# Tailwind: compile only the classes actually used (markup + JS strings)
cfg_src = re.search(r'tailwind\.config = (\{.*?\n\})\n', t, re.S).group(1)
os.makedirs('src', exist_ok=True)
open('src/page.html', 'w').write(markup + '<script>' + script + '</script>')
open('src/input.css', 'w').write('@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' + style)
open('tailwind.config.js', 'w').write('module.exports = Object.assign({ content: ["./src/page.html"] }, ' + cfg_src + ');\n')
subprocess.run(['npx', 'tailwindcss', '-i', 'src/input.css', '-o', 'src/out.css', '--minify'], check=True, capture_output=True)
css = open('src/out.css').read()
css_hash = hashlib.md5(css.encode()).hexdigest()[:8]
open(os.path.join(PAGE, f'styles.{css_hash}.css'), 'w').write(css)

desc = ("Next-day corporate gifting kits in Delhi NCR for offices, schools, colleges, universities, government events, festivals and concerts. "
        "In-house UV, UV DTF, screen, offset and sublimation printing. WhatsApp or call for pricing.")
url = 'https://lastminutegifting.store/next-day-kits/'
og = 'https://lastminutegifting.store/uploads/og-banner.jpg'
fonts = 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Instrument+Sans:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap'
ld = json.dumps({"@context": "https://schema.org", "@type": "Service", "name": "Next-day corporate gift kits", "serviceType": "Corporate gifting and custom printing",
                 "provider": {"@type": "OnlineStore", "name": "lastminutegifting", "url": "https://lastminutegifting.store/", "telephone": "+91-8588877032"},
                 "areaServed": {"@type": "City", "name": "Delhi"}, "url": url, "description": desc}, separators=(',', ':'))
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#16131f" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f6f4fb" media="(prefers-color-scheme: light)">
<title>Next-Day Corporate Gift Kits in Delhi | lastminutegifting</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:type" content="website">
<meta property="og:site_name" content="lastminutegifting">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="Event tomorrow? Kit's ready today. | lastminutegifting">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="image" href="{IMG['diary']}" fetchpriority="high">
<link rel="stylesheet" href="/next-day-kits/styles.{css_hash}.css">
<link rel="stylesheet" href="{fonts}" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="{fonts}"></noscript>
<script type="application/ld+json">{ld}</script>
<script defer src="/next-day-kits/app.{js_hash}.js"></script>
</head>
<body>
{markup}
</body>
</html>
'''
open(os.path.join(PAGE, 'index.html'), 'w').write(html)

tot = sum(os.path.getsize(f) for f in glob.glob(IMGDIR + '/*'))
print('html', os.path.getsize(os.path.join(PAGE, 'index.html')) // 1024, 'KB | css', len(css) // 1024, 'KB | js', len(script) // 1024,
      'KB | images', len(os.listdir(IMGDIR)), 'files,', tot // 1024, 'KB total')
