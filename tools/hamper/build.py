#!/usr/bin/env python3
"""Build the /build-your-hamper/ page into public_html.

    python3 tools/hamper/build.py public_html

What it does
1. Converts your real photos in tools/hamper/photos/<box id>/ to web size and puts them in
   public_html/uploads/hamper/<box id>/. Name each photo after the items in it:
       box.jpg      the empty box
       1.jpg        box with item 1
       1-2.jpg      box with items 1 and 2   (order doesn't matter: 2-1.jpg is the same photo)
       2-4.jpg      box with items 2 and 4
   Any combination without a photo still works: the page shows the box with the item pictures on it.
2. Copies tools/hamper/hampers.json (boxes, item names, which items fit which box) to the site.
3. Writes the page, its CSS and JS, using the header and footer of an existing page.
4. Adds "Build a hamper" to the site menu and a button on the Diwali collections (only once).
"""
import datetime, glob, hashlib, json, os, re, shutil, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'public_html'))
PAGE = os.path.join(SITE, 'build-your-hamper')
DATA = json.load(open(os.path.join(HERE, 'hampers.json'), encoding='utf-8'))
PHOTO_DIR = os.path.join(SITE, DATA.get('photoDir', '/uploads/hamper').strip('/'))
os.makedirs(PAGE, exist_ok=True)

# ---- sanity-check the data file
ids = set(DATA['items'])
for b in DATA['boxes']:
    bad = [i for i in b['items'] if i not in ids]
    assert not bad, f"box {b['id']}: unknown item numbers {bad} (add them under \"items\")"
    assert re.fullmatch(r'[a-z0-9-]+', b['id']), f"box id {b['id']!r}: use lowercase letters, numbers and dashes"

# ---- 1. photos
SRC = os.path.join(HERE, 'photos')
n = 0
for f in sorted(glob.glob(os.path.join(SRC, '*', '*'))):
    stem, ext = os.path.splitext(os.path.basename(f))
    if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp'): continue
    box = os.path.basename(os.path.dirname(f))
    nums = re.findall(r'\d+', stem)
    name = 'box' if not nums else '-'.join(sorted(set(nums), key=int))
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    w, h = im.size; s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((900, 900), Image.LANCZOS)
    os.makedirs(os.path.join(PHOTO_DIR, box), exist_ok=True)
    im.save(os.path.join(PHOTO_DIR, box, name + '.webp'), 'WEBP', quality=78, method=6); n += 1
print('photos converted:', n)

# ---- 2. data
shutil.copy(os.path.join(HERE, 'hampers.json'), os.path.join(PAGE, 'hampers.json'))


# ---- 3. page
def hashed(src, ext):
    b = open(os.path.join(HERE, src), 'rb').read()
    for old in glob.glob(os.path.join(PAGE, f'hamper.*.{ext}')): os.remove(old)
    name = f'hamper.{hashlib.md5(b).hexdigest()[:8]}.{ext}'
    open(os.path.join(PAGE, name), 'wb').write(b)
    return '/build-your-hamper/' + name


css, js = hashed('hamper.css', 'css'), hashed('hamper.js', 'js')
shell = open(os.path.join(SITE, 'collections', 'diwali-gifting', 'index.html'), encoding='utf-8').read()
title = 'Build Your Own Diwali Hamper | lastminutegifting'
desc = 'Pick a box, choose the gifts that go inside and see your hamper before you order. Diwali hampers in Delhi NCR, pricing on WhatsApp.'
url = 'https://lastminutegifting.store/build-your-hamper/'
og = 'https://lastminutegifting.store/uploads/og-banner.jpg'
t = shell
t = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', t)
t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', t)
t = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', t)
t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', t)
t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', t)
t = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', t)
t = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*', r'\g<1>' + og, t)
t = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', t)
t = t.replace('<script defer src="/assets/', f'<link rel="stylesheet" href="{css}">\n<script defer src="{js}"></script>\n<script defer src="/assets/', 1)
body = open(os.path.join(HERE, 'body.html'), encoding='utf-8').read()
t = re.sub(r'<main id="main">.*?</main>', lambda m: '<main id="main">\n' + body + '</main>', t, flags=re.S)
t = t.replace(' bg-ink text-paper hover:bg-ink">', ' ">')  # no category highlighted in the menu
open(os.path.join(PAGE, 'index.html'), 'w', encoding='utf-8').write(t)

# ---- 4. links from the rest of the site
NAV_OLD = '<a href="/events/" class="shrink-0 px-3 py-2 rounded-full text-sm font-semibold hover:bg-card '
NAV_NEW = '<a href="/build-your-hamper/" class="shrink-0 px-3 py-2 rounded-full text-sm font-semibold hover:bg-card ">Build a hamper</a>'
DRAWER_OLD = '<a href="/events/" class="py-1.5">Gifts by event</a>'
DRAWER_NEW = '<a href="/build-your-hamper/" class="py-1.5">Build your own hamper</a>'
CTA = ('<a href="/build-your-hamper/" class="press sticker h-11 px-5 rounded-full bg-butter text-onpop font-semibold inline-flex items-center gap-2">'
       '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="3" y="8" width="18" height="13" rx="2"/><path d="M3 12h18M12 8v13M12 8S10 3 7.5 4 9 8 12 8zm0 0s2-5 4.5-4S15 8 12 8z"/></svg>'
       ' Build your own hamper</a>')
pages = 0
for f in glob.glob(os.path.join(SITE, '**', 'index.html'), recursive=True) + [os.path.join(SITE, '404.html')]:
    if '/next-day-kits/' in f or not os.path.exists(f): continue
    s = open(f, encoding='utf-8').read(); s0 = s
    if '/build-your-hamper/" class="shrink-0' not in s and NAV_OLD in s:
        s = s.replace(NAV_OLD, NAV_NEW + NAV_OLD, 1)
    if DRAWER_NEW not in s and DRAWER_OLD in s:
        s = s.replace(DRAWER_OLD, DRAWER_NEW + DRAWER_OLD, 1)
    if re.search(r'/collections/diwali[^/]*/index\.html$', f) and 'Build your own hamper</a>' not in s.split('<footer')[0]:
        s = re.sub(r'(<div class="mt-5 flex flex-wrap gap-2"><a href="https://wa\.me/.*?</a>)', lambda m: m.group(1) + CTA, s, count=1, flags=re.S)
    if s != s0: open(f, 'w', encoding='utf-8').write(s); pages += 1
print('menu/button added to', pages, 'pages')

# ---- sitemap
sm = os.path.join(SITE, 'sitemap.xml')
if os.path.exists(sm):
    x = open(sm, encoding='utf-8').read()
    if url not in x:
        x = x.replace('</urlset>', f'  <url><loc>{url}</loc><lastmod>{datetime.date.today()}</lastmod></url>\n</urlset>'); open(sm, 'w', encoding='utf-8').write(x)
print('page:', '/build-your-hamper/', '| css', css, '| js', js)
