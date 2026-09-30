# lastminutegifting.store

Live site: https://lastminutegifting.store (cPanel hosting).

## What's here

- `public_html/` — the exact files that go into cPanel's `public_html`. Upload the contents (including the hidden `.htaccess`) and extract over the existing files; don't empty the folder first.
- `tools/` — the scripts used to produce the SEO layer on top of the React (Vite) build:
  - `gen.py` — rebuilds every prerendered page (titles, share tags, structured data, crawler content), `sitemap.xml`, `robots.txt`, `404.html`, `_app.html`, the 1200×630 share images, the mobile layout CSS fix and the patched app script.
  - `dump.mjs`, `pages.mjs` — export products, categories, settings and info-page text from a build into `data.json` for `gen.py`.
  - `htaccess` — the server rules (trailing-slash addresses, app-only routes, real 404s, caching).
  - `banner.html` — source of the home share banner (`og-banner.jpg`).

## Rebuilding after a new Vite build

```bash
node tools/dump.mjs /path/to/dist        # writes data.json
node tools/pages.mjs                     # adds info-page text (reads dist's index-*.js)
python3 tools/gen.py /path/to/dist public_html
```

`gen.py` also patches `useEffect(() => window.scrollTo(0, 0), [pathname])` in the app bundle. Better: fix it in the source as `useEffect(() => { window.scrollTo(0, 0) }, [pathname])`, and on mobile use `minmax(0,1fr)` instead of `1fr` in grids and `width:auto` on `.hero`.
