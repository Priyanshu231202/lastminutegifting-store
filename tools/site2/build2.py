#!/usr/bin/env python3
"""Compile Tailwind, hash CSS/JS, inject into pages, add next-day-kits, write .htaccess."""
import glob, hashlib, os, re, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); TW = os.path.join(HERE, 'tw')
ND = '/home/claude/nextday/build/out'
tpl = open('/home/claude/nextday/template.html').read()
cfg = re.search(r'tailwind\.config = (\{.*?\n\})\n', tpl, re.S).group(1)
style = open('/home/claude/nextday/build/src/input.css').read().split('@tailwind utilities;', 1)[1]
EXTRA = r'''
[data-layer][hidden], [hidden].grid, [hidden].flex { display: none !important; }
html.locked, html.locked body { overflow: hidden; }
.no-scrollbar { scrollbar-width: none; } .no-scrollbar::-webkit-scrollbar { display: none; }
.chip { display: inline-flex; align-items: center; gap: .4rem; height: 2.5rem; padding: 0 1rem; border-radius: 9999px; border: 2px solid rgb(var(--line)); background: rgb(var(--card)); font-weight: 600; font-size: .875rem; white-space: nowrap; flex-shrink: 0; transition: border-color .15s, background .15s, color .15s; }
.chip:hover { border-color: rgb(var(--ink)); }
.chip-sm { display: inline-flex; align-items: center; height: 1.75rem; padding: 0 .65rem; border-radius: 9999px; border: 1.5px solid rgb(var(--line)); background: rgb(var(--card)); font-size: .75rem; font-weight: 600; white-space: nowrap; }
a.chip-sm:hover, button.chip-sm:hover { border-color: rgb(var(--ink)); }
.chip[aria-pressed="true"], .chip[aria-current="page"], .chip-sm[aria-pressed="true"] { background: rgb(var(--ink)); color: rgb(var(--paper)); border-color: rgb(var(--ink)); }
.badge { display: inline-flex; align-items: center; gap: .25rem; height: 1.5rem; padding: 0 .6rem; border-radius: 9999px; border: 1.5px solid rgb(var(--ink)); font-size: .7rem; font-weight: 700; letter-spacing: .02em; text-transform: uppercase; white-space: nowrap; }
.field { display: block; width: 100%; height: 3rem; padding: 0 1rem; border-radius: 1rem; border: 2px solid rgb(var(--line)); background: rgb(var(--card)); color: rgb(var(--ink)); font-size: 16px; transition: border-color .15s; }
.field:focus { outline: none; border-color: rgb(var(--coral)); }
.field[aria-invalid="true"] { border-color: #e11d48; }
select.field { appearance: none; background-image: linear-gradient(45deg, transparent 50%, rgb(var(--muted)) 50%), linear-gradient(135deg, rgb(var(--muted)) 50%, transparent 50%); background-position: calc(100% - 20px) 50%, calc(100% - 15px) 50%; background-size: 5px 5px; background-repeat: no-repeat; padding-right: 2.5rem; }
textarea.field { height: auto; padding: .75rem 1rem; }
.dot { width: .625rem; transition: width .25s, background .25s; }
.dot[aria-current="true"] { width: 1.75rem; background: rgb(var(--coral)); }
.pop { animation: pop .4s ease; }
@keyframes pop { 0% { transform: scale(1); } 40% { transform: scale(1.35) rotate(-8deg); } 100% { transform: scale(1); } }
.will-reveal { opacity: 0; transform: translateY(18px); transition: opacity .6s ease, transform .6s ease; }
.will-reveal.in { opacity: 1; transform: none; }
.prose-lmg h2 { font-family: "Bricolage Grotesque", ui-sans-serif, system-ui, sans-serif; font-weight: 800; font-size: 1.5rem; margin-top: .75rem; }
.prose-lmg h3 { font-weight: 700; font-size: 1.15rem; }
.prose-lmg ul { list-style: disc; padding-left: 1.25rem; display: grid; gap: .35rem; }
.prose-lmg ol { list-style: decimal; padding-left: 1.25rem; display: grid; gap: .35rem; }
.prose-lmg a { color: rgb(var(--coral)); text-decoration: underline; text-underline-offset: 3px; }
.plus { transition: transform .2s; }
body[data-pdp] nav[aria-label="Quick links"] { display: none; }
.snap-x > * { scroll-snap-align: start; }
@media (prefers-reduced-motion: reduce) { .will-reveal { opacity: 1; transform: none; transition: none; } .pop { animation: none; } }
'''
open(os.path.join(TW, 'input.css'), 'w').write('@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' + style + EXTRA)
open(os.path.join(TW, 'tailwind.config.js'), 'w').write(
    'module.exports = Object.assign({ content: ["../out/**/*.html", "../src/app.js", "../gen2.py"] }, ' + cfg + ');\n')
subprocess.run(['npx', 'tailwindcss', '-i', 'input.css', '-o', 'out.css', '--minify'], cwd=TW, check=True, capture_output=True)
for f in glob.glob(os.path.join(OUT, 'assets', '*')): os.remove(f)
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
def put(src, ext):
    b = open(src, 'rb').read(); name = f'/assets/{"styles" if ext == "css" else "app"}.{hashlib.md5(b).hexdigest()[:8]}.{ext}'
    open(OUT + name, 'wb').write(b); return name
css = put(os.path.join(TW, 'out.css'), 'css')
js_src = os.path.join(TW, 'app.min.js')
r = subprocess.run(['npx', '--yes', 'esbuild@0.24.0', os.path.join(HERE, 'src/app.js'), '--minify', '--target=es2017', f'--outfile={js_src}'], cwd=TW, capture_output=True)
if r.returncode: print('esbuild unavailable, using unminified JS'); shutil.copy(os.path.join(HERE, 'src/app.js'), js_src)
js = put(js_src, 'js')
n = 0
for f in glob.glob(os.path.join(OUT, '**', '*.html'), recursive=True):
    if '/next-day-kits/' in f: continue
    t = open(f).read()
    t2 = re.sub(r'/assets/styles\.[0-9a-f]{8}\.css', css, re.sub(r'/assets/app\.[0-9a-f]{8}\.js', js, t.replace('{{CSS}}', css).replace('{{JS}}', js)))
    if t2 != t or css in t: open(f, 'w').write(t2); n += 1
# next-day kits page
shutil.rmtree(os.path.join(OUT, 'next-day-kits'), ignore_errors=True)
shutil.copytree(os.path.join(ND, 'next-day-kits'), os.path.join(OUT, 'next-day-kits'))
shutil.copytree(os.path.join(ND, 'uploads', 'next-day'), os.path.join(OUT, 'uploads', 'next-day'), dirs_exist_ok=True)
open(os.path.join(OUT, '.htaccess'), 'w').write(r'''# lastminutegifting.store — static site
DirectoryIndex index.html
ErrorDocument 404 /404.html
Options -MultiViews -Indexes
AddDefaultCharset utf-8
AddType image/webp .webp
AddType image/svg+xml .svg
AddType application/json .json

<IfModule mod_rewrite.c>
RewriteEngine On
# /page/index.html -> /page/
RewriteCond %{THE_REQUEST} \s/+(.*/)?index\.html[\s?] [NC]
RewriteRule ^ /%1 [R=301,L,NE]
# old app routes
RewriteRule ^(checkout|thank-you|account|login|wishlist)/?$ /cart/ [R=301,L]
RewriteRule ^collections/?$ /collections/all/ [R=301,L]
RewriteRule ^products/?$ /collections/all/ [R=301,L]
# always end with a slash
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !\.[A-Za-z0-9]+$
RewriteCond %{REQUEST_URI} !/$
RewriteRule ^ %{REQUEST_URI}/ [R=301,L]
</IfModule>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript text/javascript application/json image/svg+xml text/xml application/xml text/plain
</IfModule>

<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
<FilesMatch "\.(html|json|xml|txt)$">
Header set Cache-Control "no-cache"
</FilesMatch>
<FilesMatch "\.[0-9a-f]{8}\.(css|js|webp)$">
Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>
<FilesMatch "\.(webp|jpg|jpeg|png|svg|ico)$">
Header set Cache-Control "public, max-age=2592000"
</FilesMatch>
</IfModule>
''')
print('css', css, os.path.getsize(OUT + css) // 1024, 'KB | js', js, os.path.getsize(OUT + js) // 1024, 'KB | pages injected', n)
