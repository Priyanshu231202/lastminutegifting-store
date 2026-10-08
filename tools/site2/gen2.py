#!/usr/bin/env python3
"""lastminutegifting.store — full static site in the Next-Day Kits theme."""
import glob, hashlib, html, io, json, os, re, shutil, subprocess, sys, urllib.parse
from datetime import datetime, timezone
from PIL import Image

_FP = 'fetchpriority="high" '
_LZ = 'loading="lazy" '
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
OLD = '/home/claude/lastminutegifting-repo/public_html'      # current site (photos, og images, titles)
BASE = 'https://lastminutegifting.store'
D = json.load(open('/home/claude/lmg/data.json', encoding='utf-8'))
P, CAT, OCC, S, PAGES = D['products'], D['catalog']['categories'], D['catalog']['occasions'], D['settings'], D['pages']
WA_NUM = S['whatsapp']; PHONE = '+91 85888 77032'; TEL = 'tel:+918588877032'; EMAIL = S['email']
TODAY = datetime.now(timezone.utc).strftime('%Y-%m-%d')
e = lambda s: html.escape(str(s), quote=True)
slugify = lambda s: re.sub(r'(^-|-$)', '', re.sub(r'[^a-z0-9]+', '-', str(s).lower()))
wa = lambda t: f'https://wa.me/{WA_NUM}?text=' + urllib.parse.quote(t)
CAT_BY = {c['slug']: c for c in CAT}; OCC_BY = {o['slug']: o for o in OCC}
SPECIAL = {'all': ('All Gifts', 'Every gift we stock, ready to brand and deliver.'), 'bestsellers': ('Bestsellers', 'What Delhi gifts the most.'),
           'new': ('New Arrivals', 'Fresh additions to the range.'), 'same-day': ('Same-Day Delivery', 'Order before the cut-off, delivered across Delhi.')}
ORDER = {p['slug']: i for i, p in enumerate(sorted(P, key=lambda p: (-int(bool(p.get('featured'))), -int(bool(p.get('bestseller'))))))}

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

# ------------------------------------------------------------------ images
def webp_src(p):
    img = (p.get('images') or [None])[0]
    return os.path.join(OLD, re.sub(r'\.[^.]+$', '.webp', img).lstrip('/')) if img else None

from PIL import ImageChops
def square(im):
    """Trim baked-in white bars, then cover-crop photos / pad cut-outs on white to a square."""
    diff = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 22 else 0)
    box = diff.getbbox() or (0, 0) + im.size
    im2 = im.crop(box); w, h = im2.size
    edge = [im2.getpixel((x, y)) for x in range(0, w, max(1, w // 40)) for y in (0, h - 1)] + [im2.getpixel((x, y)) for y in range(0, h, max(1, h // 40)) for x in (0, w - 1)]
    whiteish = sum(1 for p in edge if min(p) > 225) / len(edge)
    if whiteish > 0.35:   # product cut-out on white: pad, never crop the product
        side = int(max(w, h) * 1.08); c = Image.new('RGB', (side, side), (255, 255, 255)); c.paste(im2, ((side - w) // 2, (side - h) // 2)); return c
    s = min(w, h); return im2.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))

THUMB, LARGE = {}, {}
os.makedirs(os.path.join(OUT, 'uploads/t')); os.makedirs(os.path.join(OUT, 'uploads/l'))
for p in P:
    src = webp_src(p)
    im = Image.open(src).convert('RGB')
    t = square(im).resize((480, 480), Image.LANCZOS)
    t.save(os.path.join(OUT, f'uploads/t/{p["slug"]}.webp'), 'WEBP', quality=70, method=6)
    l = im.copy(); l.thumbnail((960, 960), Image.LANCZOS)
    l.save(os.path.join(OUT, f'uploads/l/{p["slug"]}.webp'), 'WEBP', quality=76, method=6)
    THUMB[p['slug']] = f'/uploads/t/{p["slug"]}.webp'; LARGE[p['slug']] = (f'/uploads/l/{p["slug"]}.webp', l.size)
# share images, logo, trophies, next-day assets from the current site
for d in ('og', 'next-day'):
    shutil.copytree(os.path.join(OLD, 'uploads', d), os.path.join(OUT, 'uploads', d))
for f in ('og-banner.jpg', 'logo.webp'):
    shutil.copy(os.path.join(OLD, 'uploads', f), os.path.join(OUT, 'uploads', f))
os.makedirs(os.path.join(OUT, 'uploads/tro'))
for n in ('tro-hero', 'tro-cup', 'tro-medals', 'tro-star'):
    im = Image.open(os.path.join(OLD, f'uploads/catalogue/{n}.webp')).convert('RGB'); im.thumbnail((720, 720))
    im.save(os.path.join(OUT, f'uploads/tro/{n}.webp'), 'WEBP', quality=74)
shutil.copy(os.path.join(OLD, 'favicon.svg'), os.path.join(OUT, 'favicon.svg'))

def old_meta(rel):
    f = os.path.join(OLD, rel)
    if not os.path.exists(f):
        return None, None
    s = open(f, encoding='utf-8').read()
    t = re.search(r'<title>(.*?)</title>', s); d = re.search(r'<meta name="description" content="(.*?)"', s)
    return (html.unescape(t.group(1)) if t else None), (html.unescape(d.group(1)) if d else None)

# ------------------------------------------------------------------ shared chrome
NAV = [('Next-day kits', '/next-day-kits/'), ('Shop all', '/collections/all/')] + [(c['name'], f'/collections/{c["slug"]}/') for c in CAT] + [('Trophies', '/trophies/'), ('Bulk orders', '/bulk-enquiry/')]

ICON = {
    'search': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    'bag': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M6 7h12l-1 13H7L6 7z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>',
    'menu': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
    'moon': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    'home': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M3 11 12 4l9 7v9H5v-9"/></svg>',
    'grid': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></svg>',
    'bolt': '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/></svg>',
    'eye': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    'plus': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    'arrow': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    'left': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>',
    'right': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>',
    'wa': '<svg viewBox="0 0 32 32" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7a10.7 10.7 0 0 1-5.5-1.5l-.4-.2-3.9 1 1-3.8-.2-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5.9-1.7a.6.6 0 0 0 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.9.4 3.6 3.6 0 0 0-1.1 2.7 6.3 6.3 0 0 0 1.3 3.3 14.3 14.3 0 0 0 5.5 4.9c2 .9 2.8 1 3.8.8a3.3 3.3 0 0 0 2.2-1.5 2.7 2.7 0 0 0 .2-1.5c-.1-.2-.3-.3-.6-.4z"/></svg>',
    'phone': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
}


def header(active=''):
    links = ''.join(f'<a href="{u}" class="shrink-0 px-3 py-2 rounded-full text-sm font-semibold hover:bg-card {"bg-ink text-paper hover:bg-ink" if u == active else ""}">{e(n)}</a>' for n, u in NAV)
    return f'''<div class="bg-ink text-paper text-[12.5px] sm:text-sm">
  <div class="max-w-6xl mx-auto px-4 py-2 flex items-center justify-center gap-x-2 text-center">
    <span class="h-2 w-2 rounded-full bg-coral animate-pulse shrink-0"></span>
    <span>Order in <b id="countdown" class="font-mono text-butter tnum">--:--:--</b> <span id="cutTail">for next-day delivery</span> · Delhi NCR</span>
  </div>
</div>
<header class="sticky z-40 bg-paper/90 backdrop-blur border-b border-line" style="top: env(safe-area-inset-top, 0px)">
  <div class="max-w-6xl mx-auto px-4 h-16 flex items-center gap-2">
    <button type="button" class="lg:hidden h-10 w-10 grid place-items-center rounded-full hover:bg-card -ml-2" data-open="#drawer" aria-label="Open menu">{ICON['menu']}</button>
    <a href="/" class="font-display font-extrabold text-xl tracking-tight mr-auto" aria-label="lastminutegifting home">lastminute<span class="text-coral">gifting</span></a>
    <button type="button" data-open="#search" class="hidden sm:flex items-center gap-2 h-10 px-4 rounded-full border-2 border-line text-muted hover:border-ink w-56 text-sm">{ICON['search']}<span>Search 376 gifts</span></button>
    <button type="button" data-open="#search" class="sm:hidden h-10 w-10 grid place-items-center rounded-full hover:bg-card" aria-label="Search">{ICON['search']}</button>
    <button id="themeBtn" type="button" class="h-10 w-10 grid place-items-center rounded-full hover:bg-card" aria-label="Switch light or dark mode">{ICON['moon']}</button>
    <a href="/cart/" class="relative h-10 w-10 grid place-items-center rounded-full hover:bg-card" aria-label="Enquiry list">{ICON['bag']}<span data-list-count hidden class="absolute -top-0.5 -right-0.5 min-w-[20px] h-5 px-1 rounded-full bg-coral text-white text-[11px] font-bold grid place-items-center">0</span></a>
    <a href="/next-day-kits/" class="press sticker hidden md:inline-flex items-center gap-2 bg-coral text-white font-semibold px-4 h-10 rounded-full ml-1">Build my kit</a>
  </div>
  <nav class="hidden lg:block border-t border-line" aria-label="Shop">
    <div class="max-w-6xl mx-auto px-4 py-2 flex gap-1 overflow-x-auto">{links}</div>
  </nav>
</header>'''


def drawer():
    cats = ''.join(f'<li><a class="flex items-center gap-3 py-2" href="/collections/{c["slug"]}/"><img src="{THUMB[cat_cover(c["slug"])["slug"]]}" alt="" width="40" height="40" loading="lazy" class="h-10 w-10 rounded-xl object-cover border border-line">{e(c["name"])}</a></li>' for c in CAT)
    occ = ''.join(f'<a class="chip-sm" href="/collections/{o["slug"]}/">{e(o["name"])}</a>' for o in OCC)
    return f'''<div id="drawer" data-layer hidden class="fixed inset-0 z-50 bg-ink/50">
  <aside class="absolute inset-y-0 left-0 w-[88%] max-w-sm bg-paper overflow-y-auto p-5 grid content-start gap-5" style="padding-top: calc(20px + env(safe-area-inset-top, 0px))" aria-label="Menu">
    <div class="flex items-center justify-between"><a href="/" class="font-display font-extrabold text-xl">lastminute<span class="text-coral">gifting</span></a><button type="button" data-close class="h-10 w-10 rounded-full border-2 border-ink font-bold" aria-label="Close menu">✕</button></div>
    <a href="/next-day-kits/" class="press sticker rounded-2xl bg-coral text-white p-4 grid gap-1"><span class="font-mono text-[11px] uppercase tracking-wider text-butter">New</span><span class="font-display font-extrabold text-xl">Next-day corporate kits</span><span class="text-sm text-white/85">Branded, packed and delivered tomorrow</span></a>
    <div><p class="font-mono text-xs uppercase tracking-wider text-muted mb-1">Shop by category</p><ul class="font-semibold">{cats}<li><a class="flex items-center gap-3 py-2" href="/trophies/"><img src="/uploads/tro/tro-hero.webp" alt="" width="40" height="40" loading="lazy" class="h-10 w-10 rounded-xl object-cover border border-line">Trophies &amp; Awards</a></li></ul></div>
    <div><p class="font-mono text-xs uppercase tracking-wider text-muted mb-2">Shop by occasion</p><div class="flex flex-wrap gap-2">{occ}</div></div>
    <div class="grid gap-1 font-semibold"><a href="/collections/all/" class="py-1.5">All gifts</a><a href="/collections/bestsellers/" class="py-1.5">Bestsellers</a><a href="/collections/new/" class="py-1.5">New arrivals</a><a href="/bulk-enquiry/" class="py-1.5">Bulk &amp; corporate orders</a><a href="/pages/about/" class="py-1.5">About us</a><a href="/pages/faq/" class="py-1.5">FAQ</a></div>
    <div class="rounded-2xl border-2 border-ink p-4 grid gap-2"><p class="font-semibold">Pricing on WhatsApp or call</p><a href="{wa('Hi! I need help choosing a gift.')}" target="_blank" rel="noopener" class="h-11 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center justify-center gap-2">{ICON['wa']} WhatsApp us</a><a href="{TEL}" class="h-11 rounded-full border-2 border-ink font-semibold inline-flex items-center justify-center gap-2">{ICON['phone']} {PHONE}</a></div>
  </aside>
</div>'''


def overlays():
    return f'''<div id="search" data-layer hidden class="fixed inset-0 z-50 bg-ink/50 p-4 sm:p-10" style="padding-top: calc(16px + env(safe-area-inset-top, 0px))">
  <div class="max-w-xl mx-auto bg-paper rounded-3xl border-2 border-ink sticker overflow-hidden">
    <div class="flex items-center gap-2 p-3 border-b border-line">{ICON['search']}<input id="searchInput" data-autofocus type="search" autocomplete="off" placeholder="Bottles, diaries, bags, hampers…" class="flex-1 min-w-0 h-11 bg-transparent outline-none text-lg" aria-label="Search gifts"><button type="button" data-close class="h-9 px-3 rounded-full border-2 border-line font-semibold text-sm">Close</button></div>
    <div id="searchResults" class="max-h-[65vh] overflow-y-auto p-2"></div>
    <div class="p-3 border-t border-line flex flex-wrap gap-2 text-sm"><span class="text-muted">Popular:</span><a class="chip-sm" href="/collections/drinkware/">Bottles</a><a class="chip-sm" href="/collections/gift-sets/">Diary sets</a><a class="chip-sm" href="/collections/diwali-gifting/">Diwali hampers</a><a class="chip-sm" href="/collections/bags/">Laptop bags</a></div>
  </div>
</div>
<div id="quick" data-layer hidden class="fixed inset-0 z-50 bg-ink/50 grid place-items-end sm:place-items-center p-0 sm:p-6">
  <div class="relative w-full sm:max-w-2xl bg-paper rounded-t-3xl sm:rounded-3xl border-2 border-ink p-5 sm:p-6 max-h-[90vh] overflow-y-auto" style="padding-bottom: calc(20px + env(safe-area-inset-bottom, 0px))" role="dialog" aria-label="Quick view">
    <button type="button" data-close class="absolute top-3 right-3 h-10 w-10 rounded-full border-2 border-ink font-bold bg-paper z-10" aria-label="Close">✕</button>
    <div id="quickBody"></div>
  </div>
</div>
<div id="promo" data-layer hidden class="fixed inset-0 z-50 bg-ink/50 grid place-items-end sm:place-items-center p-0 sm:p-6">
  <div class="relative w-full sm:max-w-md bg-coral text-white rounded-t-3xl sm:rounded-3xl border-2 border-ink sticker p-6 overflow-hidden" style="padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px))" role="dialog" aria-label="Next-day kits offer">
    <button type="button" data-close class="absolute top-3 right-3 h-10 w-10 rounded-full bg-white/15 font-bold" aria-label="Close">✕</button>
    <span class="wobble inline-block sticker bg-butter text-onpop text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full">Event tomorrow?</span>
    <h2 class="font-display font-extrabold text-4xl leading-[0.95] mt-4">Kit's ready today.</h2>
    <p class="mt-3 text-white/90">Send your headcount and budget. We'll share stock-checked options with your logo in 30 minutes.</p>
    <div class="mt-5 grid gap-2">
      <a href="{wa('Hi! I need a corporate kit by tomorrow. Headcount: __, budget per person: __')}" target="_blank" rel="noopener" class="press sticker h-12 rounded-full bg-butter text-onpop font-semibold inline-flex items-center justify-center gap-2">{ICON['wa']} Get options on WhatsApp</a>
      <a href="/next-day-kits/" class="h-12 rounded-full border-2 border-white/60 font-semibold inline-flex items-center justify-center">Build my kit online</a>
    </div>
  </div>
</div>
<div id="toast" hidden role="status" class="fixed z-[60] left-1/2 -translate-x-1/2 bottom-24 md:bottom-8 bg-ink text-paper rounded-full px-5 py-3 flex items-center gap-4 text-sm shadow-xl w-max max-w-[92vw] whitespace-nowrap"></div>'''


def tabbar(active=''):
    def tab(u, label, icon, extra=''):
        on = 'text-coral' if u == active else ''
        return f'<a href="{u}" class="relative flex flex-col items-center gap-0.5 text-[11px] font-semibold {on}">{icon}{extra}<span>{label}</span></a>'
    return f'''<nav class="md:hidden fixed inset-x-0 bottom-0 z-40 bg-paper/95 backdrop-blur border-t border-line" style="padding-bottom: env(safe-area-inset-bottom, 0px)" aria-label="Quick links">
  <div class="grid grid-cols-5 items-end h-16 px-2">
    {tab('/', 'Home', ICON['home'])}
    {tab('/collections/all/', 'Shop', ICON['grid'])}
    <a href="/next-day-kits/" class="flex flex-col items-center gap-0.5 text-[11px] font-semibold -mt-6"><span class="sticker h-14 w-14 rounded-full bg-coral text-white grid place-items-center">{ICON['bolt']}</span><span>24h kits</span></a>
    {tab('/cart/', 'List', ICON['bag'], '<span data-list-count hidden class="absolute -top-1 right-[22%] min-w-[18px] h-[18px] px-1 rounded-full bg-coral text-white text-[10px] font-bold grid place-items-center">0</span>')}
    <a href="{wa('Hi! I need help with a gift order.')}" target="_blank" rel="noopener" class="flex flex-col items-center gap-0.5 text-[11px] font-semibold text-[#1da851]">{ICON['wa']}<span>WhatsApp</span></a>
  </div>
</nav>
<a href="{wa('Hi! I need help with a gift order.')}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp" class="press sticker hidden md:grid fixed z-40 right-6 bottom-6 h-14 w-14 place-items-center rounded-full bg-[#25D366] text-white">{ICON['wa'].replace('width="22" height="22"', 'width="28" height="28"')}</a>'''


def footer():
    cats = ''.join(f'<li><a href="/collections/{c["slug"]}/" class="hover:text-ink">{e(c["name"])}</a></li>' for c in CAT)
    return f'''<footer class="border-t border-line mt-10">
  <div class="max-w-6xl mx-auto px-4 py-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1fr] gap-8 text-sm">
    <div class="min-w-0">
      <p class="font-display font-extrabold text-2xl">lastminute<span class="text-coral">gifting</span></p>
      <p class="text-muted mt-2 max-w-[40ch]">Next-day corporate gifting in Delhi NCR, from the Thakur Enterprises family. Supplying gifting resellers across India since 2021.</p>
      <div class="mt-4 flex flex-wrap gap-2"><a href="{wa('Hi!')}" target="_blank" rel="noopener" class="h-10 px-4 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center gap-2">{ICON['wa']} WhatsApp</a><a href="{TEL}" class="h-10 px-4 rounded-full border-2 border-ink font-semibold inline-flex items-center gap-2">{ICON['phone']} Call</a></div>
    </div>
    <div><p class="font-semibold mb-2">Shop</p><ul class="grid gap-1.5 text-muted">{cats}<li><a href="/trophies/" class="hover:text-ink">Trophies &amp; Awards</a></li></ul></div>
    <div><p class="font-semibold mb-2">Help</p><ul class="grid gap-1.5 text-muted"><li><a href="/next-day-kits/" class="hover:text-ink">Next-day kits</a></li><li><a href="/bulk-enquiry/" class="hover:text-ink">Bulk &amp; corporate orders</a></li><li><a href="/pages/about/" class="hover:text-ink">About</a></li><li><a href="/pages/faq/" class="hover:text-ink">FAQ</a></li><li><a href="/pages/shipping/" class="hover:text-ink">Delivery policy</a></li><li><a href="/pages/refunds/" class="hover:text-ink">Returns &amp; refunds</a></li><li><a href="/pages/terms/" class="hover:text-ink">Terms &amp; privacy</a></li></ul></div>
    <div><p class="font-semibold mb-2">Talk to us</p><ul class="grid gap-1.5 text-muted"><li class="flex items-center gap-2"><span class="select-all font-mono">{PHONE}</span><button type="button" data-copy="{PHONE}" class="text-xs font-semibold text-coral">Copy</button></li><li class="break-all select-all">{e(EMAIL)}</li><li>New Delhi, India</li><li class="pt-2 text-xs">Thakur Traders · Thakur Enterprises · Harivansh Mahaprabhu · Shri Radhe Wall Clocks</li></ul></div>
  </div>
  <p class="text-center text-xs text-muted pb-24 md:pb-8">© {datetime.now().year} lastminutegifting · Prices on request</p>
</footer>'''


def page(path, title, desc, body, og='/uploads/og-banner.jpg', ld=None, active='', tab='', noindex=False, canonical=True, extra_head='', body_attr=''):
    url = BASE + path
    _esc = "<" + chr(92) + "/"
    lds = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", _esc) + '</script>' for x in (ld or []))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f6f4fb" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f0d16" media="(prefers-color-scheme: dark)">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
{f'<link rel="canonical" href="{e(url)}">' if canonical else ''}
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:type" content="website"><meta property="og:site_name" content="lastminutegifting"><meta property="og:locale" content="en_IN">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
{f'<meta property="og:url" content="{e(url)}">' if canonical else ''}
<meta property="og:image" content="{BASE}{og}"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}{og}">
<script>try{{var t=localStorage.getItem('lmg_theme');if(t)document.documentElement.dataset.theme=JSON.parse(t)}}catch(e){{}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{{{{CSS}}}}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Instrument+Sans:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap" media="print" onload="this.media='all'">
{extra_head}{lds}
<script defer src="{{{{JS}}}}"></script>
</head>
<body{body_attr}>
<a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[70] bg-ink text-paper px-4 py-2 rounded-full">Skip to content</a>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
{tabbar(tab)}
{drawer()}
{overlays()}
</body>
</html>
'''

# ------------------------------------------------------------------ components
def cat_cover(slug):
    items = [p for p in P if p['category'] == slug]
    return sorted(items, key=lambda p: ORDER[p['slug']])[0]


def badges(p):
    b = []
    if p.get('bestseller'): b.append('<span class="badge bg-ink text-paper">Bestseller</span>')
    if p.get('newArrival'): b.append('<span class="badge bg-lilac text-onpop">New</span>')
    if p.get('sameDay'): b.append('<span class="badge bg-butter text-onpop">⚡ Next-day</span>')
    return ''.join(b)


def card(p, rail=False, eager=False):
    c = CAT_BY.get(p['category'], {}).get('name', '')
    moq = (p.get('moq') or 1)
    size = 'w-[46%] sm:w-[31%] lg:w-[23%] shrink-0 snap-start' if rail else ''
    return f'''<article data-card data-sub="{slugify(p.get('subcategory', ''))}" data-order="{ORDER[p['slug']]}" data-name="{e(p['name'])}" data-date="{p.get('createdAt', '')[:10]}" class="pcard group min-w-0 {size}">
  <div class="relative rounded-3xl border-2 border-ink bg-card overflow-hidden h-full flex flex-col">
    <a href="/products/{p['slug']}/" class="block relative aspect-square bg-white overflow-hidden">
      <img src="{THUMB[p['slug']]}" alt="{e(p['name'])}" width="480" height="480" {'' if eager else 'loading="lazy" '}decoding="async" class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105">
      <span class="absolute left-2 top-2 flex flex-col items-start gap-1">{badges(p)}</span>
    </a>
    <button type="button" data-quick="{p['slug']}" class="absolute right-2 top-2 h-9 w-9 rounded-full bg-paper/90 border-2 border-ink grid place-items-center" aria-label="Quick view {e(p['name'])}">{ICON['eye']}</button>
    <div class="p-3 flex flex-col gap-1 flex-1">
      <p class="text-[11px] font-mono uppercase tracking-wider text-muted truncate">{e(p.get('subcategory') or c)}</p>
      <h3 class="font-semibold leading-tight text-[15px]"><a href="/products/{p['slug']}/" class="hover:underline underline-offset-2">{e(p['name'])}</a></h3>
      <p class="mt-auto pt-1 flex items-center justify-between gap-2 text-xs"><span class="font-bold text-coral">Ask price</span><span class="text-muted">{f'MOQ {moq}' if moq > 1 else 'In stock'}</span></p>
      <button type="button" data-add data-slug="{p['slug']}" data-name="{e(p['name'])}" data-thumb="{THUMB[p['slug']]}" data-moq="{moq}" class="press mt-2 h-10 rounded-full border-2 border-ink font-semibold text-sm inline-flex items-center justify-center gap-1.5 hover:bg-ink hover:text-paper">{ICON['plus']} Add to list</button>
    </div>
  </div>
</article>'''


def rail(title, kicker, items, link=None, link_label='See all', id_=''):
    cards = ''.join(card(p, rail=True) for p in items)
    more = f'<a href="{link}" class="font-semibold text-coral whitespace-nowrap inline-flex items-center gap-1">{link_label} {ICON["arrow"]}</a>' if link else ''
    return f'''<section class="max-w-6xl mx-auto px-4 py-10 md:py-14" {f'id="{id_}"' if id_ else ''} data-reveal>
  <div class="flex items-end justify-between gap-3 mb-5">
    <div class="min-w-0"><p class="font-mono text-xs uppercase tracking-[0.18em] text-coral font-bold">{kicker}</p><h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight mt-1">{title}</h2></div>
    <div class="flex items-center gap-2">{more}<button type="button" data-rail-prev class="hidden md:grid h-10 w-10 place-items-center rounded-full border-2 border-ink" aria-label="Scroll left">{ICON['left']}</button><button type="button" data-rail-next class="hidden md:grid h-10 w-10 place-items-center rounded-full border-2 border-ink" aria-label="Scroll right">{ICON['right']}</button></div>
  </div>
  <div class="relative"><div data-rail class="flex gap-3 md:gap-4 overflow-x-auto snap-x -mx-4 px-4 pb-3 scroll-px-4">{cards}</div></div>
</section>'''


def crumbs(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + u} for i, (n, u) in enumerate(items)]}


def crumb_html(items):
    parts = [f'<a href="{u}" class="hover:text-ink">{e(n)}</a>' for n, u in items[:-1]] + [f'<span class="text-ink">{e(items[-1][0])}</span>']
    return '<nav class="text-sm text-muted flex flex-wrap gap-x-2" aria-label="Breadcrumb">' + ' <span>/</span> '.join(parts) + '</nav>'


ORG = {'@context': 'https://schema.org', '@type': 'OnlineStore', '@id': BASE + '/#store', 'name': 'lastminutegifting', 'url': BASE + '/', 'logo': BASE + '/uploads/logo.webp',
       'telephone': S['phone'], 'email': EMAIL, 'address': {'@type': 'PostalAddress', 'addressLocality': 'New Delhi', 'addressRegion': 'Delhi', 'addressCountry': 'IN'},
       'areaServed': {'@type': 'City', 'name': 'Delhi'}, 'description': 'Next-day corporate gifting with in-house printing in Delhi NCR.'}

SITEMAP = []


def write(path, text, lastmod=TODAY, sitemap=True):
    rel = path.strip('/')
    f = os.path.join(OUT, rel, 'index.html') if rel else os.path.join(OUT, 'index.html')
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(text)
    if sitemap:
        SITEMAP.append((path, lastmod))


def collection_items(slug):
    if slug in CAT_BY: return [p for p in P if p['category'] == slug]
    if slug in OCC_BY: return [p for p in P if slug in (p.get('occasions') or [])]
    return {'all': P, 'bestsellers': [p for p in P if p.get('bestseller')], 'new': [p for p in P if p.get('newArrival')], 'same-day': [p for p in P if p.get('sameDay')]}[slug]


# ================================================================== HOME
best = sorted([p for p in P if p.get('bestseller')], key=lambda p: ORDER[p['slug']])
newp = sorted([p for p in P if p.get('newArrival')], key=lambda p: p['createdAt'], reverse=True)
diwali = sorted([p for p in P if p['category'] in ('diwali-gifting', 'diwali-corporate-gifting')], key=lambda p: ORDER[p['slug']])
corp = sorted([p for p in P if 'corporate' in (p.get('occasions') or [])], key=lambda p: ORDER[p['slug']])
by = {p['slug']: p for p in P}
H = lambda s: THUMB[s]

slides = [
    ('bg-coral text-white', 'text-butter', '24-hour corporate kits', "Event tomorrow?<br>Kit's ready today.", 'Tell us the occasion, headcount and budget. We brand it in-house and deliver next day across Delhi NCR.', '/next-day-kits/', 'Build my kit',
     ['bamboo-finish-diary-pen-set-dg-01', 'ecoweave-bottle-bot-001', 'golden-orbit-keychain-k-15', 'executive-card-holder-w-01']),
    ('bg-ink text-paper', 'text-butter', 'Diwali 2026', 'Diwali boxes that<br>land on time.', 'Hampers, copper drinkware and festive sets for teams and clients, with your logo and a printed card.', '/collections/diwali-gifting/', 'Shop Diwali gifting',
     ['royal-purple-diwali-treat-hamper', 'floral-bottle-and-cup-corporate-set', 'saffron-celebration-gift-box', 'colorful-diwali-treat-collection']),
    ('bg-lilac text-onpop', 'text-coral', 'Schools · colleges · offices', 'Kits for every<br>kind of event.', 'Joining kits, farewells, fests, convocations and conferences. From 5 kits to 500.', '/next-day-kits/#events', 'Explore event kits',
     ['anti-theft-laptop-backpack-with-usb-bg-120', 'tan-organiser-diary-pen-set-dg-13', 'urban-carry-tumbler-mug-001', 'aurum-notebook-n-31b']),
]
hero_slides = ''
for i, (bg, kc, k, h1, sub, u, cta, imgs) in enumerate(slides):
    pics = ''.join(f'<img src="{H(s)}" alt="{e(by[s]["name"])}" width="480" height="480" {_FP if i == 0 and j == 0 else ("" if i == 0 else _LZ)}decoding="async" class="w-full aspect-square object-cover rounded-2xl border-2 border-ink bg-white {["-rotate-3", "rotate-2 translate-y-4", "rotate-1", "-rotate-2 translate-y-4"][j]}">' for j, s in enumerate(imgs))
    tag = 'h1' if i == 0 else 'h2'
    hero_slides += f'''<div data-slide class="snap-center shrink-0 w-full">
  <div class="{bg} rounded-[2rem] border-2 border-ink sticker mx-0.5 overflow-hidden grid md:grid-cols-[1.1fr_1fr] gap-6 p-6 sm:p-10 items-center min-h-[460px]">
    <div class="min-w-0">
      <span class="inline-block sticker bg-butter text-onpop text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full -rotate-2">{k}</span>
      <{tag} class="font-display font-extrabold tracking-tight leading-[0.95] text-[clamp(2.3rem,7vw,4.6rem)] mt-4">{h1}</{tag}>
      <p class="mt-4 text-[17px] opacity-90 max-w-[42ch]">{sub}</p>
      <a href="{u}" class="press sticker mt-6 inline-flex items-center gap-2 bg-paper text-ink font-semibold px-6 h-12 rounded-full">{cta} {ICON['arrow']}</a>
    </div>
    <div class="grid grid-cols-2 gap-3 max-w-[380px] w-full mx-auto md:mx-0 md:ml-auto pb-4">{pics}</div>
  </div>
</div>'''
dots = ''.join(f'<button type="button" data-dot aria-label="Slide {i + 1}" class="dot h-2.5 rounded-full bg-ink/25"></button>' for i in range(len(slides)))

cat_tiles = ''.join(f'''<a href="/collections/{c['slug']}/" class="press snap-start shrink-0 w-[132px] sm:w-[150px] text-center group">
  <span class="block aspect-square rounded-[1.6rem] border-2 border-ink overflow-hidden bg-white sticker"><img src="{H(cat_cover(c['slug'])['slug'])}" alt="" width="480" height="480" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"></span>
  <span class="block mt-2 font-semibold text-sm leading-tight">{e(c['name'])}</span><span class="block text-xs text-muted">{len(collection_items(c['slug']))} gifts</span></a>''' for c in CAT)
cat_tiles += '''<a href="/trophies/" class="press snap-start shrink-0 w-[132px] sm:w-[150px] text-center group"><span class="block aspect-square rounded-[1.6rem] border-2 border-ink overflow-hidden bg-white sticker"><img src="/uploads/tro/tro-hero.webp" alt="" width="480" height="480" loading="lazy" class="w-full h-full object-cover"></span><span class="block mt-2 font-semibold text-sm leading-tight">Trophies &amp; Awards</span><span class="block text-xs text-muted">On request</span></a>'''

occ_colors = ['bg-butter text-onpop', 'bg-lilac text-onpop', 'bg-card', 'bg-coral text-white', 'bg-ink text-paper', 'bg-card']
occ_tiles = ''.join(f'''<a href="/collections/{o['slug']}/" class="press rounded-3xl border-2 border-ink p-4 flex flex-col justify-between gap-6 min-h-[120px] min-w-0 {occ_colors[i % len(occ_colors)]}">
  <span class="font-mono text-[11px] uppercase tracking-wider opacity-70">{len(collection_items(o['slug']))} gifts</span><span class="font-display font-extrabold text-xl leading-tight">{e(o['name'])}</span></a>''' for i, o in enumerate(OCC))

KITS = [('Joining kit', 'New joiner', ['bamboo-finish-diary-pen-set-dg-01', 'ecoweave-bottle-bot-001', 'golden-orbit-keychain-k-15']),
        ('Farewell kit', 'Farewell', ['tan-stitched-sling-bag-bg-305', 'classic-curve-bottle-bot-004', 'executive-card-holder-w-01']),
        ('Conference kit', 'Conference', ['onyx-notebook-n-10', 'bamboo-prime-keychain-k-10', 'aura-bottle-bot-006']),
        ('Festive kit', 'Office event', ['royal-purple-diwali-treat-hamper', 'bamboo-brew-mug-mug-011', 'tan-organiser-diary-pen-set-dg-13'])]
kit_cards = ''.join(f'''<a href="/next-day-kits/#builder" class="press snap-start shrink-0 w-[78%] sm:w-auto rounded-3xl border-2 border-ink bg-card p-5 grid gap-4 min-w-0">
  <div class="flex">{''.join(f'<img src="{H(s)}" alt="" width="64" height="64" loading="lazy" class="h-16 w-16 rounded-2xl object-cover border-2 border-card {"-ml-3" if j else ""}">' for j, s in enumerate(imgs))}</div>
  <div><p class="font-mono text-[11px] uppercase tracking-wider text-muted">{k}</p><h3 class="font-display font-extrabold text-2xl">{n}</h3></div>
  <span class="font-semibold text-coral inline-flex items-center gap-1 whitespace-nowrap shrink-0">Build this kit {ICON['arrow']}</span></a>''' for n, k, imgs in KITS)

LAB = [('UV', 'Full-colour logos on bottles, diaries and boxes. Cures instantly.', 'bg-coral text-white'), ('UV DTF', 'Crisp transfers that wrap around tumblers and pens.', 'bg-butter text-onpop'),
       ('Screen', 'Bold, washable prints on bags, totes and tees.', 'bg-lilac text-onpop'), ('Offset', 'Invites, cards, boxes and sleeves at volume.', 'bg-card'), ('Sublimation', 'Photo-quality mugs and polyester tees.', 'bg-ink text-paper')]
lab_tiles = ''.join(f'<div class="rounded-3xl border-2 border-ink p-5 grid gap-2 content-start min-w-0 {c}"><p class="font-display font-extrabold text-2xl">{n}</p><p class="text-sm opacity-85">{d}</p></div>' for n, d, c in LAB)

faq_items = [('What is the cut-off for next-day delivery?', 'Approve your artwork by 2 PM and we deliver next day by 11 AM across Delhi NCR. Later approvals move one day.'),
             ('How do I get pricing?', f'Add products to your enquiry list and send it on WhatsApp, or call {PHONE}. We check stock for your date and share the price with product, printing and delivery listed separately.'),
             ('Is there a minimum order?', 'Most products start from 1 piece. Logo branding and some keychains have a minimum, shown on each product as MOQ.'),
             ('Do you provide GST invoices?', "Yes, for every order. Schools, universities and government offices can send a purchase order and we'll invoice in the institution's name."),
             ('Can I see my logo before you print?', 'Yes. Send your logo on WhatsApp and we share a mock-up within 30 minutes. You can also preview it yourself in the mock-up studio on the next-day kits page.')]
faq_html = ''.join(f'<details class="group rounded-2xl border-2 border-ink bg-card p-5"><summary class="flex justify-between items-center gap-4 cursor-pointer font-semibold">{e(q)}<span class="plus text-2xl leading-none transition-transform">+</span></summary><p class="mt-3 text-muted">{e(a)}</p></details>' for q, a in faq_items)

home = f'''
<section class="max-w-6xl mx-auto px-4 pt-5">
  <div id="heroTrack" class="flex overflow-x-auto snap-x snap-mandatory no-scrollbar rounded-[2rem]" aria-roledescription="carousel">{hero_slides}</div>
  <div class="flex justify-center gap-2 mt-4">{dots}</div>
</section>

<div class="mt-8 border-y-2 border-ink bg-ink text-paper overflow-hidden" aria-hidden="true">
  <div class="marquee flex w-max gap-8 py-3 font-display font-bold text-lg whitespace-nowrap">{''.join(f'<span>{t} ✺</span>' for t in ['Next-day joining kits', 'Farewells', 'Conferences', 'Diwali hampers', 'School annual days', 'College fests', 'Convocations', 'Govt functions', 'Concerts', 'Client gifting'] * 2)}</div>
</div>

<section class="max-w-6xl mx-auto px-4 pt-10" data-reveal>
  <div class="flex items-end justify-between gap-3 mb-5"><h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight">Shop by category</h2><a href="/collections/all/" class="font-semibold text-coral inline-flex items-center gap-1 whitespace-nowrap shrink-0">All {len(P)} {ICON['arrow']}</a></div>
  <div class="flex gap-4 overflow-x-auto snap-x -mx-4 px-4 pb-3">{cat_tiles}</div>
</section>

<section class="max-w-6xl mx-auto px-4 pt-10" data-reveal>
  <div class="flex flex-wrap items-end justify-between gap-3"><h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight">Coming up. Plan before the rush.</h2><p class="text-sm text-muted">Days left, India time</p></div>
  <div id="upcoming" class="mt-5 -mx-4 px-4 flex gap-3 overflow-x-auto pb-2 snap-x"></div>
</section>

{rail('Bestsellers', 'Loved by Delhi', best[:14], '/collections/bestsellers/')}

<section class="bg-ink text-paper" data-reveal>
  <div class="max-w-6xl mx-auto px-4 py-14 md:py-20 grid grid-cols-1 lg:grid-cols-[1fr_1.3fr] gap-8 items-center">
    <div class="min-w-0">
      <p class="font-mono text-xs uppercase tracking-[0.18em] text-butter font-bold">24-hour kits</p>
      <h2 class="font-display font-extrabold text-4xl md:text-5xl tracking-tight mt-2">Brief at 10. Boxes at your door by 11 tomorrow.</h2>
      <p class="mt-4 text-paper/75 max-w-[44ch]">Pick a ready kit or build your own. Our print room is in-house, so there's no outside queue between your approval and the press.</p>
      <div class="mt-6 flex flex-wrap gap-3"><a href="/next-day-kits/" class="press sticker inline-flex items-center gap-2 bg-coral text-white font-semibold px-6 h-12 rounded-full">Build my kit {ICON['arrow']}</a><a href="/next-day-kits/#mockup" class="inline-flex items-center px-6 h-12 rounded-full border-2 border-paper/40 font-semibold">Try the logo mock-up</a></div>
    </div>
    <div class="flex gap-4 overflow-x-auto snap-x -mx-4 px-4 pb-2 sm:mx-0 sm:px-0 sm:grid sm:grid-cols-2 sm:overflow-visible text-ink">{kit_cards}</div>
  </div>
</section>

<section class="max-w-6xl mx-auto px-4 pt-14" data-reveal>
  <h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight">Gifts for every moment</h2>
  <div class="mt-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">{occ_tiles}</div>
</section>

{rail('Diwali, sorted', 'Festive season', diwali[:14], '/collections/diwali-gifting/', 'Shop Diwali')}

{rail('For clients & teams', 'Corporate favourites', corp[:14], '/collections/corporate/')}

<section class="max-w-6xl mx-auto px-4 py-10" data-reveal>
  <div class="flex flex-wrap items-end justify-between gap-3"><div><p class="font-mono text-xs uppercase tracking-[0.18em] text-coral font-bold">Print room on site</p><h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight mt-1">Five ways to put your logo on it</h2></div><a href="/next-day-kits/#printlab" class="font-semibold text-coral inline-flex items-center gap-1 whitespace-nowrap shrink-0">Which one suits you? {ICON['arrow']}</a></div>
  <div class="mt-6 grid grid-cols-2 lg:grid-cols-5 gap-3">{lab_tiles}</div>
</section>

{rail('Just landed', 'New arrivals', newp[:14], '/collections/new/')}

<section class="max-w-6xl mx-auto px-4 py-10" data-reveal>
  <h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight">How ordering works</h2>
  <ol class="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
    <li class="rounded-3xl border-2 border-ink bg-card p-5 grid gap-2"><span class="font-mono text-sm font-bold text-coral">Step 1</span><h3 class="font-display font-extrabold text-xl">Make a list</h3><p class="text-sm text-muted">Add gifts to your enquiry list, or build a kit.</p></li>
    <li class="rounded-3xl border-2 border-ink bg-card p-5 grid gap-2"><span class="font-mono text-sm font-bold text-coral">Step 2</span><h3 class="font-display font-extrabold text-xl">Send on WhatsApp</h3><p class="text-sm text-muted">One tap sends the list, quantities and your date.</p></li>
    <li class="rounded-3xl border-2 border-ink bg-card p-5 grid gap-2"><span class="font-mono text-sm font-bold text-coral">Step 3</span><h3 class="font-display font-extrabold text-xl">Approve price &amp; mock-up</h3><p class="text-sm text-muted">Stock-checked quote and logo preview in 30 minutes.</p></li>
    <li class="rounded-3xl border-2 border-ink bg-coral text-white p-5 grid gap-2"><span class="font-mono text-sm font-bold text-butter">Step 4</span><h3 class="font-display font-extrabold text-xl">Delivered</h3><p class="text-sm text-white/85">Packed and at your door, with a GST invoice.</p></li>
  </ol>
</section>

<section class="max-w-3xl mx-auto px-4 py-10" data-reveal>
  <h2 class="font-display font-extrabold text-3xl md:text-4xl tracking-tight">Questions</h2>
  <div class="mt-6 grid gap-3">{faq_html}</div>
  <p class="mt-4 text-sm"><a href="/pages/faq/" class="font-semibold text-coral">More answers →</a></p>
</section>

<section class="max-w-6xl mx-auto px-4 pb-6" data-reveal>
  <div class="rounded-[2rem] bg-coral text-white p-8 sm:p-12 grid grid-cols-1 md:grid-cols-[1.4fr_1fr] gap-6 items-center sticker">
    <div class="min-w-0"><h2 class="font-display font-extrabold text-4xl md:text-6xl tracking-tight leading-[0.95]">Tomorrow's sorted.</h2><p class="mt-3 text-white/90 max-w-[42ch]">Send your brief and get options with your logo in 30 minutes.</p></div>
    <div class="grid gap-3 min-w-0"><a href="{wa('Hi! I need gifts by tomorrow. Occasion: __, headcount: __, budget per person: __')}" target="_blank" rel="noopener" class="press sticker h-12 rounded-full bg-butter text-onpop font-semibold inline-flex items-center justify-center gap-2">{ICON['wa']} WhatsApp us</a><a href="{TEL}" class="h-12 rounded-full border-2 border-white/60 font-semibold inline-flex items-center justify-center gap-2">{ICON['phone']} {PHONE}</a></div>
  </div>
</section>
'''
t, d = old_meta('index.html')
write('/', page('/', t or 'lastminutegifting | Next-Day Corporate Gifts in Delhi', d or S['tagline'], home, ld=[ORG, {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'lastminutegifting', 'url': BASE + '/', 'potentialAction': {'@type': 'SearchAction', 'target': BASE + '/search/?q={q}', 'query-input': 'required name=q'}}], tab='/',
               extra_head=f'<link rel="preload" as="image" href="{H(slides[0][7][0])}" fetchpriority="high">'))

# ================================================================== COLLECTIONS
coll_slugs = sorted(os.listdir(os.path.join(OLD, 'collections')))
for slug in coll_slugs:
    if slug in CAT_BY: name, blurb, kind = CAT_BY[slug]['name'], CAT_BY[slug]['blurb'], 'category'
    elif slug in OCC_BY: name, blurb, kind = f"{OCC_BY[slug]['name']} Gifts", f"Hand-picked gifts for {OCC_BY[slug]['name'].lower()}.", 'occasion'
    elif slug in SPECIAL: name, blurb = SPECIAL[slug]; kind = 'special'
    else: continue
    items = collection_items(slug)
    items = sorted(items, key=lambda p: p['createdAt'], reverse=True) if slug == 'new' else sorted(items, key=lambda p: ORDER[p['slug']])
    chips = ''
    if kind == 'category':
        subs = CAT_BY[slug]['subcategories']
        chips = '<button type="button" data-sub-chip="all" aria-pressed="true" class="chip">All</button>' + ''.join(f'<button type="button" data-sub-chip="{slugify(s)}" aria-pressed="false" class="chip">{e(s)} <span class="opacity-60 text-xs">{sum(1 for p in items if p.get("subcategory") == s)}</span></button>' for s in subs)
    else:
        chips = ''.join(f'<a href="/collections/{c["slug"]}/" class="chip">{e(c["name"])}</a>' for c in CAT)
    others = ''.join(f'<a href="/collections/{o["slug"]}/" class="chip-sm">{e(o["name"])}</a>' for o in OCC if o['slug'] != slug)
    cover = items[0] if items else None
    body = f'''
<section class="max-w-6xl mx-auto px-4 pt-6">
  {crumb_html([('Home', '/'), (name, f'/collections/{slug}/')])}
  <div class="mt-4 rounded-[2rem] border-2 border-ink bg-card overflow-hidden grid grid-cols-1 md:grid-cols-[1.4fr_1fr] items-stretch">
    <div class="p-6 sm:p-8 min-w-0">
      <p class="font-mono text-xs uppercase tracking-[0.18em] text-coral font-bold">{'Category' if kind == 'category' else 'Collection'}</p>
      <h1 class="font-display font-extrabold text-4xl md:text-5xl tracking-tight mt-1">{e(name)}</h1>
      <p class="mt-3 text-muted max-w-[52ch]">{e(blurb)} Pricing on WhatsApp or a call, with your logo if you need it.</p>
      <div class="mt-5 flex flex-wrap gap-2"><a href="{wa(f'Hi! I need {name.lower()} for an event. Headcount: __, date: __')}" target="_blank" rel="noopener" class="press sticker h-11 px-5 rounded-full bg-coral text-white font-semibold inline-flex items-center gap-2">{ICON['wa']} Ask for options</a><a href="/next-day-kits/" class="h-11 px-5 rounded-full border-2 border-ink font-semibold inline-flex items-center">Need it tomorrow?</a></div>
    </div>
    {f'<div class="hidden md:grid grid-cols-2 gap-2 p-4 bg-paper">' + ''.join(f'<img src="{H(p["slug"])}" alt="" width="480" height="480" loading="lazy" class="w-full aspect-square object-cover rounded-2xl border border-line">' for p in items[:4]) + '</div>' if len(items) >= 4 else ''}
  </div>
</section>
<section class="max-w-6xl mx-auto px-4 pt-6">
  <div class="sticky z-30 bg-paper/95 backdrop-blur py-3 -mx-4 px-4 border-b border-line" style="top: calc(64px + env(safe-area-inset-top, 0px))">
    <div class="flex items-center gap-2"><div class="flex gap-2 overflow-x-auto no-scrollbar flex-1 min-w-0">{chips}</div>
    <select id="sortBy" class="h-10 rounded-full border-2 border-ink bg-paper px-3 font-semibold text-sm shrink-0" aria-label="Sort"><option value="featured">Featured</option><option value="new">Newest</option><option value="name">A–Z</option></select></div>
  </div>
  <p id="gridCount" class="mt-4 text-sm text-muted">{len(items)} gifts</p>
  <div id="productGrid" class="mt-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4">{''.join(card(p, eager=i < 2) for i, p in enumerate(items))}</div>
  <div class="mt-6 text-center"><button type="button" id="loadMore" hidden class="press sticker h-12 px-8 rounded-full bg-card font-semibold">Show more</button></div>
  <div class="mt-10"><p class="font-semibold mb-3">Shop by occasion</p><div class="flex flex-wrap gap-2">{others}</div></div>
</section>'''
    t, dsc = old_meta(f'collections/{slug}/index.html')
    og = f'/uploads/og/{cover["slug"]}.jpg' if cover and os.path.exists(os.path.join(OUT, f'uploads/og/{cover["slug"]}.jpg')) else '/uploads/og-banner.jpg'
    write(f'/collections/{slug}/', page(f'/collections/{slug}/', t or f'{name} | lastminutegifting', dsc or blurb, body, og=og, active=f'/collections/{slug}/', tab='/collections/all/' if slug == 'all' else '',
                                         ld=[crumbs([('Home', '/'), (name, f'/collections/{slug}/')])]))

# ================================================================== PRODUCTS
for p in P:
    c = CAT_BY.get(p['category'])
    url = f'/products/{p["slug"]}/'
    trail = [('Home', '/')] + ([(c['name'], f'/collections/{c["slug"]}/')] if c else []) + [(p['name'], url)]
    moq = p.get('moq') or 1
    related = [q for q in P if q['id'] != p['id'] and (q['category'] == p['category'] or set(q.get('occasions') or []) & set(p.get('occasions') or []))]
    related = sorted(related, key=lambda q: (-int(q['category'] == p['category']), ORDER[q['slug']]))[:12]
    large, (lw, lh) = LARGE[p['slug']]
    brand_opts = ''.join(f'<option>{e(b)}</option>' for b in (p.get('branding') or []))
    feats = ''.join(f'<li class="flex gap-2"><span class="text-coral">✓</span><span>{e(f)}</span></li>' for f in (p.get('features') or []))
    occs = ''.join(f'<a href="/collections/{o}/" class="chip-sm">{e(OCC_BY[o]["name"])}</a>' for o in (p.get('occasions') or []) if o in OCC_BY)
    wa_txt = f'Hi! Please share the price for: {p["name"]}\n{BASE}{url}'
    body = f'''
<section class="max-w-6xl mx-auto px-4 pt-6">
  {crumb_html(trail)}
  <div class="mt-4 grid grid-cols-1 lg:grid-cols-[1.05fr_1fr] gap-6 lg:gap-10 items-start">
    <div class="min-w-0 lg:sticky lg:top-24">
      <div class="relative rounded-[2rem] border-2 border-ink bg-white overflow-hidden sticker">
        <img src="{large}" alt="{e(p['name'])}" width="{lw}" height="{lh}" fetchpriority="high" decoding="async" class="w-full aspect-square object-contain">
        <span class="absolute left-3 top-3 flex flex-col items-start gap-1">{badges(p)}</span>
      </div>
      <div class="mt-3 grid grid-cols-3 gap-2 text-center text-xs font-semibold">
        <div class="rounded-2xl border-2 border-line p-2">⚡ Next-day<br><span class="text-muted font-normal">Delhi NCR</span></div>
        <div class="rounded-2xl border-2 border-line p-2">🖨 Logo print<br><span class="text-muted font-normal">in-house</span></div>
        <div class="rounded-2xl border-2 border-line p-2">🧾 GST invoice<br><span class="text-muted font-normal">every order</span></div>
      </div>
    </div>
    <div class="min-w-0">
      <p class="font-mono text-xs uppercase tracking-[0.18em] text-coral font-bold">{e(p.get('subcategory') or '')}</p>
      <h1 class="font-display font-extrabold text-3xl md:text-5xl tracking-tight mt-1 leading-[1.02]">{e(p['name'])}</h1>
      <p class="mt-2 text-sm text-muted font-mono">SKU {e(p.get('sku') or '')}{f' · {e(p["capacity"])}' if p.get('capacity') else ''}</p>
      <div class="mt-4 inline-flex items-center gap-2 rounded-full bg-butter text-onpop px-4 py-2 font-semibold text-sm">Price on request · {('Min. order ' + str(moq) + ' pcs') if moq > 1 else 'From 1 piece'}</div>
      <p class="mt-5 text-[17px] leading-relaxed">{e(p.get('description') or '')}</p>
      <div class="mt-6 grid gap-4 rounded-3xl border-2 border-ink bg-card p-5">
        {f'<label class="grid gap-2" for="branding"><span class="font-semibold">Personalise it</span><select id="branding" class="h-12 rounded-xl border-2 border-line bg-paper px-3 focus:border-ink outline-none"><option value="">No branding</option>{brand_opts}</select></label>' if brand_opts else ''}
        <div class="grid gap-2"><span class="font-semibold">Quantity</span><div class="flex items-center gap-2"><button type="button" data-step="-1" data-target="#qty" class="h-12 w-12 rounded-full border-2 border-ink text-xl font-bold" aria-label="Fewer">−</button><input id="qty" type="number" inputmode="numeric" min="{moq}" value="{max(moq, 1 if moq > 1 else 10)}" class="h-12 w-24 text-center rounded-xl border-2 border-line bg-paper font-mono text-lg tnum" aria-label="Quantity"><button type="button" data-step="1" data-target="#qty" class="h-12 w-12 rounded-full border-2 border-ink text-xl font-bold" aria-label="More">+</button></div></div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <a id="askProduct" data-ask-product data-name="{e(p['name'])}" href="{wa(wa_txt)}" target="_blank" rel="noopener" class="press sticker h-12 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center justify-center gap-2">{ICON['wa']} Ask price</a>
          <button type="button" data-add data-slug="{p['slug']}" data-name="{e(p['name'])}" data-thumb="{H(p['slug'])}" data-moq="{moq}" data-qty-from="#qty" {'data-brand-from="#branding"' if brand_opts else ''} class="press sticker h-12 rounded-full bg-coral text-white font-semibold inline-flex items-center justify-center gap-2">{ICON['plus']} Add to enquiry list</button>
        </div>
        <a href="{TEL}" class="text-center font-semibold underline underline-offset-4">Or call {PHONE}</a>
      </div>
      {f'<p class="mt-4 text-sm font-semibold">{e(p["bulkNote"])}</p>' if p.get('bulkNote') else ''}
      {f'<div class="mt-6"><h2 class="font-display font-extrabold text-xl">What you get</h2><ul class="mt-3 grid gap-2">{feats}</ul></div>' if feats else ''}
      {f'<div class="mt-6"><h2 class="font-display font-extrabold text-xl">Great for</h2><div class="mt-3 flex flex-wrap gap-2">{occs}</div></div>' if occs else ''}
      <details class="mt-6 rounded-2xl border-2 border-line p-4"><summary class="font-semibold cursor-pointer">Delivery &amp; returns</summary><p class="mt-2 text-sm text-muted">{'Next-day delivery across Delhi NCR when artwork is approved by 2 PM.' if p.get('sameDay') else 'Delivered in 1–7 working days depending on quantity and branding.'} Damaged or incorrect items are replaced free if reported within 24 hours. Personalised items can't be returned unless defective.</p></details>
    </div>
  </div>
</section>
{rail('You may also like', 'Related', related) if related else ''}
<div class="md:hidden fixed inset-x-0 bottom-0 z-40 px-3 pt-2 bg-gradient-to-t from-paper via-paper/90 to-transparent" style="padding-bottom: calc(10px + env(safe-area-inset-bottom, 0px))"><div class="flex gap-2 bg-paper/95 backdrop-blur rounded-full border-2 border-ink p-1.5 sticker"><a data-ask-product href="{wa(wa_txt)}" target="_blank" rel="noopener" class="flex-1 h-11 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center justify-center gap-1.5 text-sm">{ICON['wa']} Ask price</a><button type="button" data-add data-slug="{p['slug']}" data-name="{e(p['name'])}" data-thumb="{H(p['slug'])}" data-moq="{moq}" data-qty-from="#qty" {'data-brand-from="#branding"' if brand_opts else ''} class="flex-1 h-11 rounded-full bg-coral text-white font-semibold text-sm">Add to list</button></div></div>'''
    t, dsc = old_meta(f'products/{p["slug"]}/index.html')
    ld = [{'@context': 'https://schema.org', '@type': 'Product', 'name': p['name'], 'description': p.get('description') or '', 'sku': p.get('sku'), 'image': [BASE + large],
           'category': c['name'] if c else p['category'], 'url': BASE + url, 'brand': {'@type': 'Brand', 'name': 'lastminutegifting'}}, crumbs(trail)]
    og = f'/uploads/og/{p["slug"]}.jpg' if os.path.exists(os.path.join(OUT, f'uploads/og/{p["slug"]}.jpg')) else '/uploads/og-banner.jpg'
    write(url, page(url, t or f'{p["name"]} | lastminutegifting', dsc or p.get('description', ''), body, og=og, ld=ld, active=f'/collections/{p["category"]}/', body_attr=' data-no-promo data-pdp'), lastmod=(p.get('createdAt') or TODAY)[:10])

# ================================================================== CART / SEARCH
cart = f'''
<section class="max-w-3xl mx-auto px-4 pt-8">
  <p class="font-mono text-xs uppercase tracking-[0.18em] text-coral font-bold">Enquiry list</p>
  <h1 class="font-display font-extrabold text-4xl md:text-5xl tracking-tight mt-1">Your gift list</h1>
  <p class="mt-2 text-muted">Send it on WhatsApp and we'll reply with stock, pricing and delivery for your date.</p>
  <div id="cartEmpty" class="mt-8 rounded-3xl border-2 border-dashed border-ink p-8 text-center grid gap-4 justify-items-center">
    <span class="text-5xl">🎁</span><p class="font-display font-extrabold text-2xl">Nothing here yet</p><p class="text-muted">Tap “Add to list” on any gift, or let us build a kit for you.</p>
    <div class="flex flex-wrap justify-center gap-2"><a href="/collections/bestsellers/" class="press sticker h-12 px-6 rounded-full bg-coral text-white font-semibold inline-flex items-center">Browse bestsellers</a><a href="/next-day-kits/" class="h-12 px-6 rounded-full border-2 border-ink font-semibold inline-flex items-center">Build a kit</a></div>
  </div>
  <div id="cartFull" hidden class="mt-8 grid gap-6">
    <ul id="cartItems" class="grid gap-3"></ul>
    <button type="button" id="clearList" class="justify-self-start text-sm font-semibold text-muted underline underline-offset-4">Clear list</button>
    <form id="cartForm" class="rounded-3xl border-2 border-ink bg-card p-5 grid gap-4" novalidate>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label class="grid gap-1.5" for="c-name"><span class="font-semibold">Your name</span><input id="c-name" name="name" autocomplete="name" class="field" required></label>
        <label class="grid gap-1.5" for="c-phone"><span class="font-semibold">Mobile number</span><input id="c-phone" name="phone" inputmode="tel" autocomplete="tel" class="field" required></label>
        <label class="grid gap-1.5" for="c-company"><span class="font-semibold">Company <span class="text-muted font-normal">(optional)</span></span><input id="c-company" name="company" autocomplete="organization" class="field"></label>
        <label class="grid gap-1.5" for="needBy"><span class="font-semibold">Needed by</span><input id="needBy" name="needBy" type="date" class="field"></label>
      </div>
      <label class="grid gap-1.5" for="c-msg"><span class="font-semibold">Anything else? <span class="text-muted font-normal">(logo, message card, address)</span></span><textarea id="c-msg" name="message" rows="3" class="field py-3 h-auto"></textarea></label>
      <p id="cartErr" hidden class="text-coral font-semibold text-sm"></p>
      <button class="press sticker h-12 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center justify-center gap-2">{ICON['wa']} Send list on WhatsApp</button>
      <p id="cartSent" hidden class="text-sm font-semibold">WhatsApp opened with your list. Press send there to complete your enquiry.</p>
      <p class="text-sm text-muted text-center">Prefer a call? <a href="{TEL}" class="font-semibold text-ink">{PHONE}</a></p>
    </form>
  </div>
</section>'''
write('/cart/', page('/cart/', 'Your gift list | lastminutegifting', 'Your enquiry list.', cart, noindex=True, canonical=False, tab='/cart/', body_attr=' data-no-promo'), sitemap=False)

search = f'''
<section class="max-w-3xl mx-auto px-4 pt-8">
  <h1 class="font-display font-extrabold text-4xl tracking-tight">Search</h1>
  <input id="searchPageInput" type="search" placeholder="Search bottles, diaries, bags…" class="field mt-4 h-14 text-lg" aria-label="Search gifts">
  <p id="searchCount" class="mt-3 text-sm text-muted"></p>
  <ul id="searchPage" class="mt-3 grid gap-1"></ul>
</section>'''
write('/search/', page('/search/', 'Search | lastminutegifting', 'Search gifts.', search, noindex=True, canonical=False, body_attr=' data-no-promo'), sitemap=False)

# ================================================================== BULK + TROPHIES
def form(kind, title_line, extra_fields):
    return f'''<form data-wa-form="{e(title_line)}" class="rounded-3xl border-2 border-ink bg-card p-5 sm:p-6 grid gap-4 sticker" novalidate>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    <label class="grid gap-1.5" for="{kind}-name"><span class="font-semibold">Your name</span><input id="{kind}-name" name="name" data-label="Name" autocomplete="name" class="field"></label>
    <label class="grid gap-1.5" for="{kind}-phone"><span class="font-semibold">Mobile number</span><input id="{kind}-phone" name="phone" data-label="Mobile" inputmode="tel" autocomplete="tel" class="field"></label>
    <label class="grid gap-1.5" for="{kind}-org"><span class="font-semibold">Company / institution</span><input id="{kind}-org" data-label="Organisation" class="field"></label>
    <label class="grid gap-1.5" for="{kind}-qty"><span class="font-semibold">Quantity</span><input id="{kind}-qty" data-label="Quantity" inputmode="numeric" class="field"></label>
    <label class="grid gap-1.5" for="{kind}-date"><span class="font-semibold">Needed by</span><input id="{kind}-date" type="date" data-label="Needed by" class="field"></label>
    <label class="grid gap-1.5" for="{kind}-budget"><span class="font-semibold">Budget per piece <span class="text-muted font-normal">(optional)</span></span><input id="{kind}-budget" data-label="Budget per piece" class="field"></label>
  </div>
  {extra_fields}
  <label class="grid gap-1.5" for="{kind}-msg"><span class="font-semibold">Details</span><textarea id="{kind}-msg" rows="3" data-label="Details" class="field py-3 h-auto"></textarea></label>
  <p data-err hidden class="text-coral font-semibold text-sm">Please add your name and a 10-digit mobile number.</p>
  <button class="press sticker h-12 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center justify-center gap-2">{ICON['wa']} Send on WhatsApp</button>
  <p data-ok hidden class="text-sm font-semibold">WhatsApp opened with your details. Press send there.</p>
</form>'''

interests = ''.join(f'<label class="flex items-center gap-2 rounded-full border-2 border-line px-3 h-10 cursor-pointer has-[:checked]:bg-butter has-[:checked]:border-ink has-[:checked]:text-onpop" for="int-{i}"><input id="int-{i}" type="checkbox" data-label="Interested in {e(c["name"])}" class="h-4 w-4"><span class="text-sm font-semibold">{e(c["name"])}</span></label>' for i, c in enumerate(CAT))
bulk = f'''
<section class="max-w-6xl mx-auto px-4 pt-8 grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] gap-8 items-start">
  <div class="min-w-0">
    <span class="sticker inline-block bg-butter text-onpop text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full -rotate-2">Bulk &amp; corporate</span>
    <h1 class="font-display font-extrabold text-4xl md:text-6xl tracking-tight mt-4 leading-[0.95]">Gifts for the whole team, with your logo.</h1>
    <p class="mt-4 text-muted max-w-[46ch]">Share a few details and our team sends curated options, logo mock-ups and bulk pricing on WhatsApp.</p>
    <ul class="mt-6 grid gap-3">{''.join(f'<li class="flex gap-3 items-start"><span class="h-7 w-7 shrink-0 rounded-full bg-coral text-white grid place-items-center font-bold text-sm">✓</span><span class="font-semibold">{t}</span></li>' for t in ['Special pricing from 50 units', 'UV, UV DTF, screen, offset and sublimation in-house', 'Custom packaging and message cards', 'Delivery to one office or 500 homes', 'GST invoice and PO-friendly billing'])}</ul>
    <div class="mt-8 grid grid-cols-3 gap-2">{''.join(f'<img src="{H(s)}" alt="" width="480" height="480" loading="lazy" class="w-full aspect-square object-cover rounded-2xl border-2 border-ink">' for s in ['tan-organiser-diary-pen-set-dg-13', 'anti-theft-laptop-backpack-with-usb-bg-120', 'floral-bottle-and-cup-corporate-set'])}</div>
  </div>
  {form('bulk', 'Bulk and corporate gifting enquiry', f'<fieldset class="grid gap-2"><legend class="font-semibold mb-1">Interested in</legend><div class="flex flex-wrap gap-2">{interests}</div></fieldset>')}
</section>'''
t, dsc = old_meta('bulk-enquiry/index.html')
write('/bulk-enquiry/', page('/bulk-enquiry/', t or 'Bulk & Corporate Gifting | lastminutegifting', dsc or 'Bulk and corporate gifting enquiries.', bulk, active='/bulk-enquiry/'))

kinds = ''.join(f'<label class="flex items-center gap-2 rounded-full border-2 border-line px-3 h-10 cursor-pointer has-[:checked]:bg-butter has-[:checked]:border-ink has-[:checked]:text-onpop" for="tk-{i}"><input id="tk-{i}" type="checkbox" data-label="Type: {k}" class="h-4 w-4"><span class="text-sm font-semibold">{k}</span></label>' for i, k in enumerate(['Trophies', 'Medals', 'Plaques', 'Mementos', 'Certificates']))
tro_imgs = [('tro-cup', 'Trophy cups'), ('tro-medals', 'Medals'), ('tro-star', 'Star awards'), ('tro-hero', 'Plaques & mementos')]
trophies = f'''
<section class="max-w-6xl mx-auto px-4 pt-8 grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] gap-8 items-start">
  <div class="min-w-0">
    <span class="sticker inline-block bg-lilac text-onpop text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full rotate-1">Trophies · awards · medals</span>
    <h1 class="font-display font-extrabold text-4xl md:text-6xl tracking-tight mt-4 leading-[0.95]">Recognition that looks the part.</h1>
    <p class="mt-4 text-muted max-w-[46ch]">Trophies, plaques and medals for annual days, sales awards, sports events and milestones, with names and logos engraved or printed.</p>
    <div class="mt-6 grid grid-cols-2 gap-3">{''.join(f'<figure class="rounded-3xl border-2 border-ink bg-white overflow-hidden"><img src="/uploads/tro/{n}.webp" alt="{l}" loading="lazy" class="w-full aspect-square object-cover"><figcaption class="p-3 font-semibold text-sm bg-card">{l}</figcaption></figure>' for n, l in tro_imgs)}</div>
  </div>
  {form('tro', 'Trophies and awards enquiry', f'<fieldset class="grid gap-2"><legend class="font-semibold mb-1">What do you need?</legend><div class="flex flex-wrap gap-2">{kinds}</div></fieldset>')}
</section>'''
t, dsc = old_meta('trophies/index.html')
write('/trophies/', page('/trophies/', t or 'Trophies & Awards | lastminutegifting', dsc or 'Custom trophies and awards.', trophies, active='/trophies/', og='/uploads/og/trophies.jpg' if os.path.exists(os.path.join(OUT, 'uploads/og/trophies.jpg')) else '/uploads/og-banner.jpg'))

# ================================================================== INFO PAGES
for key, pg in PAGES.items():
    content = ''.join(f'<p>{e(x)}</p>' for x in pg.get('body') or [])
    if pg.get('qa'):
        content += ''.join(f'<details class="rounded-2xl border-2 border-ink bg-card p-5" open><summary class="font-semibold cursor-pointer">{e(q)}</summary><p class="mt-2 text-muted">{e(a)}</p></details>' for q, a in pg['qa'])
    if key == 'about':
        content += '<p>We are part of the Thakur Enterprises family: in-house notebooks and diaries, imported drinkware, our own bag craftsmen and Shri Radhe wall clocks. Since 2021 we have supplied gifting resellers across India, and now serve companies, schools and institutions directly.</p>'
    body = f'''<section class="max-w-3xl mx-auto px-4 pt-8">
  {crumb_html([('Home', '/'), (pg['title'], f'/pages/{key}/')])}
  <h1 class="font-display font-extrabold text-4xl md:text-5xl tracking-tight mt-4">{e(pg['title'])}</h1>
  <div class="prose-lmg mt-6 grid gap-4 text-[17px] leading-relaxed">{content}</div>
  <div class="mt-8 rounded-3xl border-2 border-ink bg-card p-5 flex flex-wrap items-center justify-between gap-3"><p class="font-semibold">Still have a question?</p><div class="flex gap-2"><a href="{wa('Hi! I have a question.')}" target="_blank" rel="noopener" class="h-11 px-5 rounded-full bg-[#25D366] text-white font-semibold inline-flex items-center gap-2">{ICON['wa']} WhatsApp</a><a href="{TEL}" class="h-11 px-5 rounded-full border-2 border-ink font-semibold inline-flex items-center">Call</a></div></div>
</section>'''
    t, dsc = old_meta(f'pages/{key}/index.html')
    write(f'/pages/{key}/', page(f'/pages/{key}/', t or f'{pg["title"]} | lastminutegifting', dsc or pg['title'], body))

# ================================================================== 404
nf = f'''<section class="max-w-3xl mx-auto px-4 pt-14 text-center grid gap-4 justify-items-center">
  <span class="wobble inline-block sticker bg-butter text-onpop font-display font-extrabold text-5xl px-6 py-3 rounded-3xl">404</span>
  <h1 class="font-display font-extrabold text-4xl md:text-5xl tracking-tight">This page went to deliver a gift.</h1>
  <p class="text-muted">…and hasn't come back. Let's find you something else.</p>
  <div class="flex flex-wrap justify-center gap-2"><a href="/" class="press sticker h-12 px-6 rounded-full bg-coral text-white font-semibold inline-flex items-center">Go home</a><a href="/collections/all/" class="h-12 px-6 rounded-full border-2 border-ink font-semibold inline-flex items-center">Browse all gifts</a></div>
</section>
{rail('Bestsellers', 'Popular right now', best[:10], '/collections/bestsellers/')}'''
open(os.path.join(OUT, '404.html'), 'w').write(page('/404', 'Page not found | lastminutegifting', 'Page not found.', nf, noindex=True, canonical=False, body_attr=' data-no-promo'))

# ================================================================== search index, sitemap, robots, htaccess
idx = [{'s': p['slug'], 'n': p['name'], 'c': p.get('subcategory') or CAT_BY.get(p['category'], {}).get('name', ''), 't': THUMB[p['slug']], 'm': p.get('moq') or 1,
        'd': (p.get('description') or '')[:180], 'k': ' '.join([p.get('sku') or '', p['category'], ' '.join(p.get('occasions') or [])])} for p in sorted(P, key=lambda p: ORDER[p['slug']])]
json.dump(idx, open(os.path.join(OUT, 'search-index.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
SITEMAP.append(('/next-day-kits/', TODAY))
open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                                   ''.join(f'  <url><loc>{BASE}{u}</loc><lastmod>{m}</lastmod></url>\n' for u, m in SITEMAP) + '</urlset>\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /cart/\nDisallow: /search/\n\nSitemap: {BASE}/sitemap.xml\n')
print('pages', len(SITEMAP) + 3)
