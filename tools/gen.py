#!/usr/bin/env python3
"""Rebuild the SEO layer of the lastminutegifting.store deploy bundle.

Reads the built app (index.html + data chunks exported to data.json) and rewrites
every prerendered page with JPEG share images, richer structured data and
crawlable fallback content, plus .htaccess, robots.txt, sitemap.xml, 404.html
and _app.html (shell for app-only routes).
"""
import html, json, os, re, shutil, sys, urllib.parse
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
BASE = 'https://lastminutegifting.store'
D = json.load(open('data.json', encoding='utf-8'))
P, CAT, OCC, S, PAGES = D['products'], D['catalog']['categories'], D['catalog']['occasions'], D['settings'], D['pages']
STORE = S['storeName']
HOME_TITLE = 'lastminutegifting | Same-Day Gifts Delivered Across Delhi'
WA = 'https://wa.me/' + S['whatsapp']
TEL = 'tel:' + re.sub(r'[^\d+]', '', S['phone'])
PHONE_TXT = S['phone'].replace('-', ' ')
SPECIAL = {
    'all': ('All Gifts', 'Every gift we stock, ready to deliver.'),
    'bestsellers': ('Bestsellers', 'What Delhi gifts the most.'),
    'new': ('New Arrivals', 'Fresh additions to the range.'),
    'same-day': ('Same-Day Delivery', 'Order till 8 PM, delivered in 2–4 hours across Delhi.'),
}
CAT_BY = {c['slug']: c for c in CAT}
OCC_BY = {o['slug']: o for o in OCC}
BY_SLUG = {p['slug']: p for p in P}

e = lambda s: html.escape(str(s), quote=True)
slugify = lambda s: re.sub(r'(^-|-$)', '', re.sub(r'[^a-z0-9]+', '-', str(s).lower()))


def inr_in(n):
    # Indian digit grouping, like toLocaleString('en-IN')
    n = int(round(float(n)))
    s = str(n)
    if len(s) <= 3:
        return '₹' + s
    head, tail = s[:-3], s[-3:]
    head = re.sub(r'(\d)(?=(\d\d)+$)', r'\1,', head)
    return '₹' + head + ',' + tail


def webp(path):
    if not path:
        return None
    return re.sub(r'\.[^.]+$', '.webp', path) if path.startswith('/uploads/') else path


def app_sort(items):
    # the app's default "featured" order: featured, then bestseller; stable otherwise
    return sorted(items, key=lambda p: (-int(bool(p.get('featured'))), -int(bool(p.get('bestseller')))))


def collection(slug):
    """Mirror the app's collection resolution: category, then occasion, then special."""
    if slug in CAT_BY:
        c = CAT_BY[slug]
        return c['name'], c['blurb'], [p for p in P if p['category'] == slug], 'category'
    if slug in OCC_BY:
        o = OCC_BY[slug]
        return f"{o['name']} Gifts", f"Hand-picked gifts for {o['name'].lower()}.", [p for p in P if slug in (p.get('occasions') or [])], 'occasion'
    if slug in SPECIAL:
        t, b = SPECIAL[slug]
        items = {'all': P, 'bestsellers': [p for p in P if p.get('bestseller')],
                 'new': sorted([p for p in P if p.get('newArrival')], key=lambda p: p['createdAt'], reverse=True),
                 'same-day': [p for p in P if p.get('sameDay')]}[slug]
        return t, b, items, 'special'
    return None


# ---------------------------------------------------------------- share images
OG_DIR = os.path.join(OUT, 'uploads', 'og')


def make_og(src_rel, dest_name):
    """1200x630 JPEG: whole product visible, on white (studio shots) or a blurred fill (lifestyle)."""
    dest = os.path.join(OG_DIR, dest_name)
    if os.path.exists(dest):
        return f'/uploads/og/{dest_name}'
    im = Image.open(os.path.join(SRC, src_rel.lstrip('/'))).convert('RGBA')
    flat = Image.new('RGBA', im.size, (255, 255, 255, 255))
    flat.alpha_composite(im)
    im = flat.convert('RGB')
    w, h = im.size
    border = [im.getpixel((x, 0)) for x in range(0, w, 4)] + [im.getpixel((x, h - 1)) for x in range(0, w, 4)] + \
             [im.getpixel((0, y)) for y in range(0, h, 4)] + [im.getpixel((w - 1, y)) for y in range(0, h, 4)]
    white_share = sum(1 for px in border if min(px) > 238) / len(border)
    diff = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 14 else 0)
    box = diff.getbbox() or (0, 0, w, h)
    W, H = 1200, 630
    if white_share > 0.9:
        canvas = Image.new('RGB', (W, H), (255, 255, 255))
        fg = im.crop(box)
        pad = 36
        fg.thumbnail((W - 2 * pad, H - 2 * pad), Image.LANCZOS)
    else:
        fg = im.crop(box)
        cover = fg.copy()
        scale = max(W / cover.width, H / cover.height)
        cover = cover.resize((int(cover.width * scale) + 1, int(cover.height * scale) + 1), Image.LANCZOS)
        cx, cy = (cover.width - W) // 2, (cover.height - H) // 2
        canvas = cover.crop((cx, cy, cx + W, cy + H)).filter(ImageFilter.GaussianBlur(36))
        canvas = Image.blend(canvas, Image.new('RGB', (W, H), (251, 248, 244)), 0.28)
        fg.thumbnail((W, H), Image.LANCZOS)
    canvas.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    os.makedirs(OG_DIR, exist_ok=True)
    canvas.save(dest, 'JPEG', quality=80, optimize=True, progressive=True)
    return f'/uploads/og/{dest_name}'


def product_og(p):
    img = webp((p.get('images') or [None])[0])
    if not img or not os.path.exists(os.path.join(SRC, img.lstrip('/'))):
        return '/uploads/og-banner.jpg'
    return make_og(img, p['slug'] + '.jpg')


# ---------------------------------------------------------------- page shell
shell = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
ASSETS = '\n    '.join(re.findall(r'<link rel="preconnect"[^>]*>|<link href="https://fonts[^>]*>|<script type="module"[^>]*></script>|<link rel="stylesheet"[^>]*>', shell))
assert '<script type="module"' in ASSETS and 'rel="stylesheet"' in ASSETS, 'could not find the app assets in index.html'

# App fix: newer Chrome returns a Promise from scrollTo; the app's effect returned it as a cleanup and React crashed on every page change
_ENTRY = re.search(r'src="/assets/(index-[^"]+)\.js"', shell).group(1)
_js = open(os.path.join(SRC, 'assets', _ENTRY + '.js'), encoding='utf-8').read()
_bad = '(0,_.useEffect)(()=>window.scrollTo(0,0),[e])'
assert _js.count(_bad) == 1, 'scroll effect not found'
FIXED_JS = _js.replace(_bad, '(0,_.useEffect)(()=>{window.scrollTo(0,0)},[e])')
FIXED_NAME = _ENTRY + '-fix1'
ASSETS = ASSETS.replace(f'/assets/{_ENTRY}.js', f'/assets/{FIXED_NAME}.js')

MOBILE_CSS = ("<style id=\"lmg-mobile-fix\">"
    "html,body{overflow-x:clip}"
    "img,video,iframe{max-width:100%}"
    ".grid>*,.pdp-grid>*,.coll-layout>*,.cart-layout>*,.bulk-page>*,.tro-hero>*,.cat-grid>*,.occ-grid>*,.trust-row>*,.footer-grid>*,.footer-perks>*,.form-grid>*,.tro-grid>*,.steps>*{min-width:0}"
    "@media (max-width:900px){"
    ".hero.container{width:auto;max-width:none}"
    ".grid{grid-template-columns:repeat(2,minmax(0,1fr))}"
    ".pdp-grid,.coll-layout,.cart-layout,.bulk-page,.tro-hero{grid-template-columns:minmax(0,1fr)}"
    ".pdp-actions{grid-template-columns:repeat(2,minmax(0,1fr))}"
    ".toolbar select{min-width:0;max-width:55%}"
    ".footer-perks,.footer-grid{grid-template-columns:repeat(2,minmax(0,1fr))}"
    "}"
    "@media (max-width:600px){.cat-grid,.occ-grid,.trust-row{grid-template-columns:repeat(2,minmax(0,1fr))}}"
    "h1,h2,h3,p,a,span,strong{overflow-wrap:anywhere}"
    "</style>")

RETITLE = ("<script>(function(){try{var H=" + json.dumps(HOME_TITLE) + ",S=' | lastminutegifting',t,n=0,f=location.href,m=0;"
           "function set(){if(!m&&location.href===f)return;m=1;clearTimeout(t);n=0;tick()}"
           "function tick(){t=setTimeout(function(){if(location.pathname==='/'){document.title=H;return}"
           "var h=document.querySelector('main h1'),x=h&&h.textContent.replace(/\\s+/g,' ').trim();"
           "if(x){document.title=x+S}else if(++n<20){tick()}},120)}"
           "function sl(u){try{var x=new URL(u,location.href);if(x.origin===location.origin&&!/\/$/.test(x.pathname)&&!/\.[a-z0-9]+$/i.test(x.pathname)){x.pathname+='/';return x.pathname+x.search+x.hash}}catch(e){}return u}['pushState','replaceState'].forEach(function(k){var o=history[k];history[k]=function(s,t,u){var r=o.call(this,s,t,u==null?u:sl(u));set();return r}});function fx(){var a=document.querySelectorAll('a[href]');for(var i=0;i<a.length;i++){var h=a[i].getAttribute('href');if(h.charAt(0)!=='/'||h.charAt(1)==='/')continue;var v=sl(h);if(v!==h)a[i].setAttribute('href',v)}}new MutationObserver(function(){clearTimeout(fx.t);fx.t=setTimeout(fx,50)}).observe(document.documentElement,{childList:true,subtree:true});"
           "addEventListener('popstate',set);if(document.documentElement.hasAttribute('data-retitle'))addEventListener('DOMContentLoaded',function(){m=1;set()})"
           "}catch(e){}})();</script>")


def page(path_url, title, desc, og_image, og_type='website', body='', jsonld=None, noindex=False, canonical=True, og_alt=None, retitle=False):
    url = BASE + path_url
    tags = [f'<meta name="description" content="{e(desc)}" />', f'<title>{e(title)}</title>']
    if noindex:
        tags.append('<meta name="robots" content="noindex" />')
    if canonical:
        tags.append(f'<link rel="canonical" href="{e(url)}" />')
    img = BASE + og_image
    tags += [
        f'<meta property="og:type" content="{og_type}" />',
        f'<meta property="og:site_name" content="{STORE}" />',
        '<meta property="og:locale" content="en_IN" />',
        f'<meta property="og:title" content="{e(title)}" />',
        f'<meta property="og:description" content="{e(desc)}" />',
    ]
    if canonical:
        tags.append(f'<meta property="og:url" content="{e(url)}" />')
    tags += [
        f'<meta property="og:image" content="{e(img)}" />',
        '<meta property="og:image:type" content="image/jpeg" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{e(og_alt or title)}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{e(title)}" />',
        f'<meta name="twitter:description" content="{e(desc)}" />',
        f'<meta name="twitter:image" content="{e(img)}" />',
    ]
    ld = ''
    if jsonld:
        blob = json.dumps(jsonld if len(jsonld) > 1 else jsonld[0], ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        ld = f'\n    <script type="application/ld+json">{blob}</script>'
    head_tags = '\n    '.join(tags)
    attr = ' data-retitle' if retitle else ''
    return f'''<!doctype html>
<html lang="en"{attr}>
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#1d1a26" />
    {head_tags}
    {RETITLE}
    {ASSETS}
    {MOBILE_CSS}{ld}
  </head>
  <body>
    <div id="root"><noscript>{body}</noscript></div>
  </body>
</html>
'''


def plink(p):
    return f'<a href="/products/{e(p["slug"])}/">{e(p["name"])}</a> - {inr_in(p["price"])}'


NAV = ('<header><p><a href="/">lastminutegifting</a> - ' + e(S['tagline']) + '</p>'
       '<nav aria-label="Shop"><ul>'
       + ''.join(f'<li><a href="/collections/{c["slug"]}/">{e(c["name"])}</a></li>' for c in CAT)
       + '<li><a href="/trophies/">Trophies &amp; Awards</a></li><li><a href="/collections/same-day/">Same-day delivery</a></li>'
       '<li><a href="/bulk-enquiry/">Bulk &amp; corporate orders</a></li></ul></nav></header>')
FOOTER = ('<footer><p>Check availability or order on WhatsApp: <a href="' + WA + '">' + e(PHONE_TXT) + '</a> · Call <a href="' + TEL + '">'
          + e(PHONE_TXT) + '</a> · Email <a href="mailto:' + e(S['email']) + '">' + e(S['email']) + '</a> · ' + e(S['address']) + '</p>'
          '<ul><li><a href="/pages/about/">About</a></li><li><a href="/pages/faq/">FAQ</a></li><li><a href="/pages/shipping/">Delivery policy</a></li>'
          '<li><a href="/pages/refunds/">Returns &amp; refunds</a></li><li><a href="/pages/terms/">Terms &amp; privacy</a></li></ul></footer>')


def wrap(main):
    return NAV + '<main>' + main + '</main>' + FOOTER


ORG = {'@type': 'OnlineStore', '@id': BASE + '/#store', 'name': STORE, 'url': BASE + '/', 'logo': BASE + '/uploads/logo.webp',
       'image': BASE + '/uploads/og-banner.jpg', 'description': S['tagline'] + '. Bulk and corporate gifting.',
       'telephone': S['phone'], 'email': S['email'],
       'address': {'@type': 'PostalAddress', 'addressLocality': 'New Delhi', 'addressRegion': 'Delhi', 'addressCountry': 'IN'},
       'areaServed': {'@type': 'City', 'name': 'Delhi'}}


def crumbs(*items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + u} for i, (n, u) in enumerate(items)]}


def read_existing(rel):
    """Keep the titles/descriptions already chosen for each prerendered page."""
    s = open(os.path.join(SRC, rel), encoding='utf-8').read()
    t = html.unescape(re.search(r'<title>(.*?)</title>', s).group(1))
    d = html.unescape(re.search(r'<meta name="description" content="(.*?)"', s).group(1))
    return t, d


# ---------------------------------------------------------------- build
if os.path.exists(OUT):
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
written, sitemap = [], []
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')


def write(rel, text):
    full = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(text)
    written.append(rel)


open(os.path.join(OUT, 'assets', FIXED_NAME + '.js'), 'w', encoding='utf-8').write(FIXED_JS)
written.append('assets/' + FIXED_NAME + '.js')

# banner
Image.open('og-banner.jpg').save(os.path.join(OUT, 'uploads', 'og-banner.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)

# home
t, d = read_existing('index.html')
best = [p for p in app_sort(P) if p.get('bestseller')][:12]
home_main = (f'<h1>{e(S["tagline"])}</h1><p>{e(d)}</p><p>{e(S["announcement"])}</p>'
             '<h2>Shop by category</h2><ul>' + ''.join(f'<li><a href="/collections/{c["slug"]}/">{e(c["name"])}</a>: {e(c["blurb"])}</li>' for c in CAT) + '</ul>'
             '<h2>Gifts for every moment</h2><ul>' + ''.join(f'<li><a href="/collections/{o["slug"]}/">{e(o["name"])}</a></li>' for o in OCC) + '</ul>'
             '<h2>Bestsellers</h2><ul>' + ''.join(f'<li>{plink(p)}</li>' for p in best) + '</ul>'
             f'<p><a href="{WA}">Message us on WhatsApp</a> to check availability and ask about bulk orders.</p>')
write('index.html', page('/', t, d, '/uploads/og-banner.jpg', body=wrap(home_main), og_alt='lastminutegifting - gifts delivered in 2–4 hours across Delhi',
                         jsonld=[{'@context': 'https://schema.org', **ORG},
                                 {'@context': 'https://schema.org', '@type': 'WebSite', 'name': STORE, 'url': BASE + '/', 'publisher': {'@id': BASE + '/#store'}}]))
sitemap.append(('/', today))

# products
for p in P:
    rel = f'products/{p["slug"]}/index.html'
    t, d = read_existing(rel)
    og = product_og(p)
    c = CAT_BY.get(p['category'])
    url = f'/products/{p["slug"]}/'
    imgs = [BASE + webp(i) for i in (p.get('images') or []) if webp(i)]
    offer = {'@type': 'Offer', 'url': BASE + url, 'priceCurrency': 'INR', 'price': f'{float(p["price"]):.2f}',
             'availability': 'https://schema.org/' + ('InStock' if p.get('inStock', True) else 'OutOfStock'),
             'itemCondition': 'https://schema.org/NewCondition', 'seller': {'@id': BASE + '/#store'}}
    if (p.get('moq') or 1) > 1:
        offer['eligibleQuantity'] = {'@type': 'QuantitativeValue', 'minValue': p['moq'], 'unitCode': 'C62'}
    prod = {'@context': 'https://schema.org', '@type': 'Product', 'name': p['name'], 'description': p.get('description') or d,
            'sku': p.get('sku'), 'image': imgs, 'url': BASE + url, 'category': c['name'] if c else p['category'], 'offers': offer}
    if not prod['sku']:
        del prod['sku']
    trail = [('Home', '/')] + ([(c['name'], f'/collections/{c["slug"]}/')] if c else []) + [(p['name'], url)]
    related = [q for q in P if q['id'] != p['id'] and (q['category'] == p['category'] or set(q.get('occasions') or []) & set(p.get('occasions') or []))]
    related = sorted(related, key=lambda q: -int(q['category'] == p['category']))[:8]
    price = inr_in(p['price']) + (f' (MRP {inr_in(p["mrp"])})' if (p.get('mrp') or 0) > p['price'] else '')
    parts = ['<p>' + ' › '.join(f'<a href="{u}">{e(n)}</a>' for n, u in trail[:-1]) + '</p>', f'<h1>{e(p["name"])}</h1>']
    if imgs:
        parts.append(f'<img src="{e(webp(p["images"][0]))}" alt="{e(p["name"])}" width="600" />')
    parts.append(f'<p>Price: {price}' + (f' · Minimum order {p["moq"]} pcs' if (p.get('moq') or 1) > 1 else '') + '</p>')
    if p.get('description'):
        parts.append(f'<p>{e(p["description"])}</p>')
    if p.get('features'):
        parts.append('<h2>Features</h2><ul>' + ''.join(f'<li>{e(x)}</li>' for x in p['features']) + '</ul>')
    if p.get('branding'):
        parts.append('<h2>Personalisation</h2><ul>' + ''.join(f'<li>{e(x)}</li>' for x in p['branding']) + '</ul>')
    if p.get('bulkNote'):
        parts.append(f'<p>{e(p["bulkNote"])}</p>')
    parts.append('<p>' + ('Delivered in 2–4 hours across Delhi.' if p.get('sameDay') else 'Delivered in 1–7 working days.') + '</p>')
    msg = f'Hi! Is {p["name"]} ({p.get("sku") or p["slug"]}) available? {BASE}{url}'
    parts.append(f'<p><a href="{WA}?text={e(urllib.parse.quote(msg))}">Ask on WhatsApp about this gift</a></p>')
    if related:
        parts.append('<h2>You may also like</h2><ul>' + ''.join(f'<li>{plink(q)}</li>' for q in related) + '</ul>')
    write(rel, page(url, t, d, og, og_type='product', body=wrap(''.join(parts)), og_alt=p['name'], jsonld=[prod, crumbs(*trail)]))
    sitemap.append((url, (p.get('createdAt') or today)[:10]))

# collections
for slug in sorted(os.listdir(os.path.join(SRC, 'collections'))):
    rel = f'collections/{slug}/index.html'
    if not os.path.exists(os.path.join(SRC, rel)):
        continue
    col = collection(slug)
    t, d = read_existing(rel)
    if not col:
        print('skip unknown collection', slug)
        continue
    name, blurb, items, kind = col
    items = items if slug == 'new' else app_sort(items)
    url = f'/collections/{slug}/'
    og = product_og(items[0]) if items else '/uploads/og-banner.jpg'
    parts = [f'<p><a href="/">Home</a></p><h1>{e(name)}</h1><p>{e(blurb)}</p>', f'<p>{len(items)} gifts</p>']
    if kind == 'category':
        subs = CAT_BY[slug]['subcategories']
        parts.append('<ul>' + ''.join(f'<li><a href="/collections/{slug}/?sub={slugify(s)}">{e(s)}</a></li>' for s in subs) + '</ul>')
    parts.append('<ul>' + ''.join(f'<li>{plink(p)}</li>' for p in items) + '</ul>')
    write(rel, page(url, t, d, og, body=wrap(''.join(parts)), og_alt=name, jsonld=[crumbs(('Home', '/'), (name, url))]))
    sitemap.append((url, today))

# info pages
for key, pg in PAGES.items():
    rel = f'pages/{key}/index.html'
    t, d = read_existing(rel)
    body = f'<h1>{e(pg["title"])}</h1>' + ''.join(f'<p>{e(x)}</p>' for x in pg.get('body') or [])
    if pg.get('qa'):
        body += ''.join(f'<h2>{e(q)}</h2><p>{e(a)}</p>' for q, a in pg['qa'])
    write(rel, page(f'/pages/{key}/', t, d, '/uploads/og-banner.jpg', body=wrap(body)))
    sitemap.append((f'/pages/{key}/', today))

# trophies + bulk enquiry keep their own copy, just framed
for key, img in (('trophies', '/uploads/catalogue/tro-hero.webp'), ('bulk-enquiry', None)):
    rel = f'{key}/index.html'
    src_html = open(os.path.join(SRC, rel), encoding='utf-8').read()
    t, d = read_existing(rel)
    inner = re.search(r'<noscript><main>(.*?)</main></noscript>', src_html, re.S).group(1)
    inner = re.sub(r'^<p><a href="/">lastminutegifting</a></p>', '', inner)
    og = make_og(img, 'trophies.jpg') if img and os.path.exists(os.path.join(SRC, img.lstrip('/'))) else '/uploads/og-banner.jpg'
    write(rel, page(f'/{key}/', t, d, og, body=wrap(inner)))
    sitemap.append((f'/{key}/', today))

# shell for pages that only exist in the app (gift list, checkout, thank-you, search)
write('_app.html', page('/', STORE, S['tagline'] + '.', '/uploads/og-banner.jpg', body=wrap('<h1>' + e(STORE) + '</h1><p>This page needs JavaScript.</p>'),
                        noindex=True, canonical=False, retitle=True))

# 404: the real app, so visitors keep the header, search and WhatsApp button
write('404.html', page('/', 'Page not found | lastminutegifting', 'This page could not be found.', '/uploads/og-banner.jpg',
                       body=wrap('<h1>Page not found</h1><p>We couldn’t find that page. <a href="/collections/all/">Browse all gifts</a> or <a href="/">go to the homepage</a>.</p>'),
                       noindex=True, canonical=False))

# sitemap
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, lm in sitemap:
    xml.append(f'  <url><loc>{e(BASE + u)}</loc><lastmod>{lm}</lastmod></url>')
xml.append('</urlset>')
write('sitemap.xml', '\n'.join(xml) + '\n')

write('robots.txt', f'''User-agent: *
Allow: /
Disallow: /admin
Disallow: /search
Disallow: /cart
Disallow: /checkout
Disallow: /thank-you

Sitemap: {BASE}/sitemap.xml
''')

shutil.copy('htaccess', os.path.join(OUT, '.htaccess'))
written.append('.htaccess')
print('pages written', len(written), 'sitemap urls', len(sitemap), 'og images', len(os.listdir(OG_DIR)))
json.dump(sorted(set(written)), open('written.json', 'w'))
