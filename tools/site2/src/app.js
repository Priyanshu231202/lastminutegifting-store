/* lastminutegifting — shared site script (no framework) */
(function () {
  'use strict';
  var WA = '918588877032';
  var PHONE = '+91 85888 77032';
  var CUTOFF_HOUR_IST = 14;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function wa(text) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(text); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* ---------- theme ---------- */
  var tb = $('#themeBtn');
  if (tb) tb.addEventListener('click', function () {
    var r = document.documentElement;
    var dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme = dark ? 'light' : 'dark'; store('lmg_theme', r.dataset.theme);
  });

  /* ---------- cut-off countdown ---------- */
  function tick() {
    var el = $('#countdown'); if (!el) return;
    var now = new Date(Date.now() + 5.5 * 3600e3);
    var cut = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), CUTOFF_HOUR_IST));
    var after = false;
    if (now >= cut) { cut.setUTCDate(cut.getUTCDate() + 1); after = true; }
    var s = Math.max(0, Math.floor((cut - now) / 1000));
    var p = function (n) { return String(n).padStart(2, '0'); };
    el.textContent = p(Math.floor(s / 3600)) + ':' + p(Math.floor(s % 3600 / 60)) + ':' + p(s % 60);
    var tail = $('#cutTail'); if (tail) tail.textContent = after ? 'for day-after delivery' : 'for next-day delivery';
  }
  tick(); setInterval(tick, 1000);

  /* ---------- drawer, search overlay, modals ---------- */
  function openLayer(id) { var el = $(id); if (!el) return; el.hidden = false; document.body.style.overflow = 'hidden'; var f = el.querySelector('[data-autofocus]'); if (f) setTimeout(function () { f.focus(); }, 30); }
  function closeLayer(el) { el.hidden = true; if (!$$('[data-layer]:not([hidden])').length) document.body.style.overflow = ''; }
  document.addEventListener('click', function (e) {
    var o = e.target.closest('[data-open]'); if (o) { e.preventDefault(); openLayer(o.getAttribute('data-open')); if (o.getAttribute('data-open') === '#search') loadIndex(); return; }
    var c = e.target.closest('[data-close]'); if (c) { e.preventDefault(); closeLayer(c.closest('[data-layer]')); return; }
    if (e.target.matches('[data-layer]')) closeLayer(e.target);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('[data-layer]:not([hidden])').forEach(closeLayer); });

  /* ---------- product index (search + quick view) ---------- */
  var INDEX = null, indexP = null;
  function loadIndex() { if (!indexP) indexP = fetch('/search-index.json').then(function (r) { return r.json(); }).then(function (d) { INDEX = d; return d; }); return indexP; }
  function cardMini(p) {
    return '<a href="/products/' + p.s + '/" class="flex items-center gap-3 p-2 rounded-2xl hover:bg-paper"><img src="' + p.t + '" alt="" width="56" height="56" loading="lazy" class="h-14 w-14 rounded-xl object-cover border border-line bg-white"><span class="min-w-0"><span class="block font-semibold leading-tight">' + esc(p.n) + '</span><span class="block text-xs text-muted">' + esc(p.c) + '</span></span></a>';
  }
  function searchIn(q, list) {
    var t = q.toLowerCase().split(/\s+/).filter(Boolean); if (!t.length) return [];
    return list.filter(function (p) { var h = (p.n + ' ' + p.c + ' ' + p.k).toLowerCase(); return t.every(function (w) { return h.indexOf(w) > -1; }); });
  }
  var si = $('#searchInput');
  if (si) si.addEventListener('input', function () {
    loadIndex().then(function (d) {
      var r = searchIn(si.value, d), box = $('#searchResults');
      box.innerHTML = si.value.trim() ? (r.length ? r.slice(0, 12).map(cardMini).join('') + (r.length > 12 ? '<a class="block text-center font-semibold text-coral py-3" href="/search/?q=' + encodeURIComponent(si.value) + '">See all ' + r.length + ' results →</a>' : '') : '<p class="p-4 text-muted">No match. <a class="text-coral font-semibold" href="' + wa('Hi! I am looking for: ' + si.value) + '" target="_blank" rel="noopener">Ask us on WhatsApp</a>, we probably have it.</p>') : '';
    });
  });
  var sp = $('#searchPage');
  if (sp) {
    var q = new URLSearchParams(location.search).get('q') || '';
    $('#searchPageInput').value = q;
    var run = function () {
      loadIndex().then(function (d) {
        var v = $('#searchPageInput').value, r = searchIn(v, d);
        $('#searchCount').textContent = v.trim() ? r.length + ' results for “' + v + '”' : 'Type to search 376 gifts';
        sp.innerHTML = r.slice(0, 60).map(function (p) { return '<li>' + cardMini(p) + '</li>'; }).join('');
      });
    };
    $('#searchPageInput').addEventListener('input', run); run();
  }

  /* ---------- enquiry list (cart) ---------- */
  function list() { return store('lmg_list') || []; }
  function saveList(l) { store('lmg_list', l); badge(); }
  function badge() { var n = list().reduce(function (s, i) { return s + 1; }, 0); $$('[data-list-count]').forEach(function (b) { b.textContent = n; b.hidden = !n; }); }
  badge();
  var toastT;
  function toast(msg, link) {
    var t = $('#toast'); if (!t) return;
    t.innerHTML = '<span>' + esc(msg) + '</span>' + (link ? '<a href="/cart/" class="font-semibold text-butter whitespace-nowrap">View list →</a>' : '');
    t.hidden = false; clearTimeout(toastT); toastT = setTimeout(function () { t.hidden = true; }, 2600);
  }
  function addItem(d, qty, branding) {
    var l = list(), f = l.filter(function (i) { return i.s === d.s; })[0];
    if (f) { f.q = (f.q || 1) + (qty || 1); if (branding) f.b = branding; } else l.push({ s: d.s, n: d.n, t: d.t, q: qty || Math.max(1, +d.m || 1), b: branding || '' });
    saveList(l); toast('Added to your enquiry list', true);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-add]'); if (!a) return;
    e.preventDefault();
    var qty = a.getAttribute('data-qty-from') ? +($(a.getAttribute('data-qty-from')).value || 1) : 0;
    var br = a.getAttribute('data-brand-from') ? $(a.getAttribute('data-brand-from')).value : '';
    addItem({ s: a.dataset.slug, n: a.dataset.name, t: a.dataset.thumb, m: a.dataset.moq }, qty, br);
    a.classList.add('pop'); setTimeout(function () { a.classList.remove('pop'); }, 400);
  });
  var cartBox = $('#cartItems');
  function renderCart() {
    if (!cartBox) return;
    var l = list();
    $('#cartEmpty').hidden = !!l.length; $('#cartFull').hidden = !l.length;
    cartBox.innerHTML = l.map(function (i, k) {
      return '<li class="flex gap-3 items-center p-3 rounded-2xl border-2 border-ink bg-card">' +
        '<img src="' + i.t + '" alt="" width="64" height="64" class="h-16 w-16 rounded-xl object-cover bg-white border border-line">' +
        '<div class="flex-1 min-w-0"><a href="/products/' + i.s + '/" class="font-semibold leading-tight block">' + esc(i.n) + '</a>' +
        (i.b ? '<span class="text-xs text-muted">' + esc(i.b) + '</span>' : '') +
        '<div class="mt-2 inline-flex items-center rounded-full border-2 border-line"><button type="button" class="h-8 w-9 font-bold" data-q="' + k + '" data-d="-1" aria-label="Fewer">−</button><span class="w-10 text-center font-mono tnum">' + i.q + '</span><button type="button" class="h-8 w-9 font-bold" data-q="' + k + '" data-d="1" aria-label="More">+</button></div></div>' +
        '<button type="button" class="h-9 w-9 rounded-full border-2 border-line text-muted" data-rm="' + k + '" aria-label="Remove">✕</button></li>';
    }).join('');
  }
  if (cartBox) {
    renderCart();
    cartBox.addEventListener('click', function (e) {
      var l = list(), q = e.target.closest('[data-q]'), r = e.target.closest('[data-rm]');
      if (q) { var i = l[+q.dataset.q]; i.q = Math.max(1, i.q + (+q.dataset.d)); saveList(l); renderCart(); }
      if (r) { l.splice(+r.dataset.rm, 1); saveList(l); renderCart(); }
    });
    var nb = $('#needBy'); if (nb && !nb.value) nb.value = new Date(Date.now() + 5.5 * 3600e3 + 864e5).toISOString().slice(0, 10);
    $('#cartForm').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target, name = f.name.value.trim(), phone = f.phone.value.replace(/\D/g, '');
      var err = $('#cartErr');
      if (name.length < 2 || !/^[6-9]\d{9}$/.test(phone.slice(-10))) { err.textContent = 'Please add your name and a 10-digit mobile number.'; err.hidden = false; return; }
      err.hidden = true;
      var msg = ['Hi! Gift enquiry from the website. Please share pricing.', 'Name: ' + name, 'Mobile: ' + phone, f.company.value && 'Company: ' + f.company.value, f.needBy.value && 'Needed by: ' + f.needBy.value, 'Items:']
        .concat(list().map(function (i) { return '- ' + i.n + ' × ' + i.q + (i.b ? ' (' + i.b + ')' : ''); }))
        .concat([f.message.value && 'Notes: ' + f.message.value]).filter(Boolean).join('\n');
      window.open(wa(msg), '_blank', 'noopener');
      $('#cartSent').hidden = false;
    });
    var cl = $('#clearList'); if (cl) cl.addEventListener('click', function () { saveList([]); renderCart(); });
  }

  /* ---------- quick view ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-quick]'); if (!b) return;
    e.preventDefault();
    loadIndex().then(function (d) {
      var p = d.filter(function (x) { return x.s === b.dataset.quick; })[0]; if (!p) return;
      var m = $('#quickBody');
      m.innerHTML = '<div class="grid sm:grid-cols-2 gap-5"><img src="' + p.t + '" alt="' + esc(p.n) + '" width="400" height="400" class="w-full aspect-square object-cover rounded-2xl border-2 border-ink bg-white">' +
        '<div class="min-w-0 grid gap-3 content-start"><p class="font-mono text-xs uppercase tracking-wider text-coral font-bold">' + esc(p.c) + '</p><h3 class="font-display font-extrabold text-2xl leading-tight">' + esc(p.n) + '</h3><p class="text-muted text-sm">' + esc(p.d) + '</p>' +
        (p.m > 1 ? '<p class="text-sm font-semibold">Minimum order ' + p.m + ' pcs</p>' : '') +
        '<div class="grid gap-2 mt-2"><button type="button" class="press sticker h-12 rounded-full bg-coral text-white font-semibold" data-add data-slug="' + p.s + '" data-name="' + esc(p.n) + '" data-thumb="' + p.t + '" data-moq="' + p.m + '">Add to enquiry list</button>' +
        '<a class="press sticker h-12 rounded-full bg-card font-semibold inline-flex items-center justify-center" target="_blank" rel="noopener" href="' + wa('Hi! Please share the price for: ' + p.n + ' (https://lastminutegifting.store/products/' + p.s + '/)') + '">Ask price on WhatsApp</a>' +
        '<a class="text-center font-semibold underline underline-offset-4" href="/products/' + p.s + '/">View full details</a></div></div></div>';
      openLayer('#quick');
    });
  });

  /* ---------- carousels ---------- */
  $$('[data-rail]').forEach(function (rail) {
    var wrap = rail.parentElement;
    $$('[data-rail-prev],[data-rail-next]', wrap.parentElement).forEach(function (btn) {
      btn.addEventListener('click', function () { rail.scrollBy({ left: (btn.hasAttribute('data-rail-next') ? 1 : -1) * rail.clientWidth * 0.85, behavior: reduce ? 'auto' : 'smooth' }); });
    });
  });
  var hero = $('#heroTrack');
  if (hero) {
    var slides = $$('[data-slide]', hero), dots = $$('[data-dot]'), cur = 0, timer;
    var go = function (i) { cur = (i + slides.length) % slides.length; hero.scrollTo({ left: slides[cur].offsetLeft - hero.offsetLeft, behavior: reduce ? 'auto' : 'smooth' }); };
    var mark = function () { var i = Math.round(hero.scrollLeft / hero.clientWidth); cur = i; dots.forEach(function (d, k) { d.setAttribute('aria-current', k === i ? 'true' : 'false'); }); };
    hero.addEventListener('scroll', function () { clearTimeout(hero._t); hero._t = setTimeout(mark, 80); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { go(k); restart(); }); });
    var restart = function () { clearInterval(timer); if (!reduce) timer = setInterval(function () { go(cur + 1); }, 5500); };
    hero.addEventListener('pointerdown', function () { clearInterval(timer); });
    restart(); mark();
  }

  /* ---------- upcoming occasions ---------- */
  var up = $('#upcoming');
  if (up) {
    var OCC = [
      { n: 'Diwali', dates: ['2026-11-08', '2027-10-29'], u: '/collections/diwali-gifting/', note: 'Hampers & corporate boxes' },
      { n: "Children's Day", md: '11-14', u: '/next-day-kits/#events', note: 'Stationery kits & return gifts' },
      { n: 'Christmas', md: '12-25', u: '/collections/gift-sets/', note: 'Gift boxes & mugs' },
      { n: 'New Year', md: '01-01', u: '/collections/notebooks/', note: 'Diaries & planners' },
      { n: 'Republic Day', md: '01-26', u: '/bulk-enquiry/', note: 'Badges & sweet boxes' },
      { n: "Women's Day", md: '03-08', u: '/collections/for-her/', note: 'Team gift sets' },
      { n: 'Independence Day', md: '08-15', u: '/bulk-enquiry/', note: 'Badges & programmes' },
      { n: "Teachers' Day", md: '09-05', u: '/collections/gift-sets/', note: 'Diary sets & mugs' }
    ];
    var now = new Date(Date.now() + 5.5 * 3600e3), today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
    var L = OCC.map(function (o) {
      var ts;
      if (o.dates) ts = o.dates.map(function (d) { return Date.parse(d + 'T00:00:00Z'); }).filter(function (x) { return x >= today; })[0];
      else { var md = o.md.split('-').map(Number); ts = Date.UTC(now.getUTCFullYear(), md[0] - 1, md[1]); if (ts < today) ts = Date.UTC(now.getUTCFullYear() + 1, md[0] - 1, md[1]); }
      return ts ? { o: o, ts: ts, d: Math.round((ts - today) / 864e5) } : null;
    }).filter(Boolean).sort(function (a, b) { return a.ts - b.ts; }).slice(0, 6);
    up.innerHTML = L.map(function (x, i) {
      var hot = i === 0;
      return '<a href="' + x.o.u + '" class="press snap-start shrink-0 w-[200px] rounded-3xl border-2 border-ink p-4 grid gap-1.5 ' + (hot ? 'bg-coral text-white' : 'bg-card') + '">' +
        '<span class="font-mono text-xs uppercase tracking-wider ' + (hot ? 'text-butter' : 'text-muted') + '">' + new Date(x.ts).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', timeZone: 'UTC' }) + '</span>' +
        '<span class="font-display font-extrabold text-xl leading-tight">' + x.o.n + '</span>' +
        '<span class="font-display font-extrabold text-4xl tnum leading-none">' + (x.d || 'Today') + '<span class="text-sm font-sans font-semibold"> ' + (x.d === 0 ? '' : x.d === 1 ? 'day left' : 'days left') + '</span></span>' +
        '<span class="text-sm ' + (hot ? 'text-white/85' : 'text-muted') + '">' + x.o.note + '</span></a>';
    }).join('');
  }

  /* ---------- collection filters ---------- */
  var grid = $('#productGrid');
  if (grid) {
    var cards = $$('[data-card]', grid), PAGE = 24, shown = PAGE, sub = 'all';
    var params = new URLSearchParams(location.search); if (params.get('sub')) sub = params.get('sub');
    var apply = function () {
      var vis = cards.filter(function (c) { return sub === 'all' || c.dataset.sub === sub; });
      cards.forEach(function (c) { c.hidden = true; });
      vis.forEach(function (c, i) { c.hidden = i >= shown; });
      var more = $('#loadMore'); if (more) { more.hidden = vis.length <= shown; more.textContent = 'Show more (' + (vis.length - shown) + ' left)'; }
      var cnt = $('#gridCount'); if (cnt) cnt.textContent = vis.length + ' gifts';
      $$('[data-sub-chip]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.subChip === sub ? 'true' : 'false'); });
    };
    $$('[data-sub-chip]').forEach(function (b) { b.addEventListener('click', function () { sub = b.dataset.subChip; shown = PAGE; apply(); var u = new URL(location.href); if (sub === 'all') u.searchParams.delete('sub'); else u.searchParams.set('sub', sub); history.replaceState(null, '', u); }); });
    var so = $('#sortBy');
    if (so) so.addEventListener('change', function () {
      var k = so.value;
      cards.sort(function (a, b) {
        if (k === 'name') return a.dataset.name.localeCompare(b.dataset.name);
        if (k === 'new') return (b.dataset.date || '').localeCompare(a.dataset.date || '');
        return (+a.dataset.order) - (+b.dataset.order);
      });
      cards.forEach(function (c) { grid.appendChild(c); }); shown = PAGE; apply();
    });
    var lm = $('#loadMore'); if (lm) lm.addEventListener('click', function () { shown += PAGE; apply(); });
    apply();
  }

  /* ---------- product page ---------- */
  $$('[data-step]').forEach(function (b) {
    b.addEventListener('click', function () { var i = $(b.dataset.target), min = +i.min || 1; i.value = Math.max(min, (+i.value || min) + (+b.dataset.step)); i.dispatchEvent(new Event('input')); });
  });
  var askP = $('#askProduct');
  if (askP) {
    var upd = function () {
      var q = $('#qty') ? $('#qty').value : '', br = $('#branding') ? $('#branding').value : '';
      var t = 'Hi! Please share the price for: ' + askP.dataset.name + (q ? '\nQuantity: ' + q : '') + (br ? '\nBranding: ' + br : '') + '\n' + location.href.split('#')[0];
      $$('[data-ask-product]').forEach(function (a) { a.href = wa(t); });
    };
    ['qty', 'branding'].forEach(function (id) { var el = $('#' + id); if (el) el.addEventListener('input', upd); });
    upd();
  }

  /* ---------- quote forms (bulk / trophies) ---------- */
  $$('form[data-wa-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var err = $('[data-err]', f), name = f.name.value.trim(), phone = f.phone.value.replace(/\D/g, '');
      if (name.length < 2 || !/^[6-9]\d{9}$/.test(phone.slice(-10))) { err.hidden = false; return; }
      err.hidden = true;
      var lines = [f.dataset.waForm];
      $$('[data-label]', f).forEach(function (el) {
        var v = el.type === 'checkbox' ? (el.checked ? 'Yes' : '') : el.value;
        if (el.type === 'checkbox' && !el.checked) return;
        if (v) lines.push(el.dataset.label + (el.type === 'checkbox' ? '' : ': ' + v));
      });
      window.open(wa(lines.join('\n')), '_blank', 'noopener');
      var ok = $('[data-ok]', f); if (ok) ok.hidden = false;
    });
  });

  /* ---------- copy number ---------- */
  document.addEventListener('click', function (e) {
    var c = e.target.closest('[data-copy]'); if (!c) return;
    var done = function () { var t = c.textContent; c.textContent = 'Copied'; setTimeout(function () { c.textContent = t; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(c.dataset.copy).then(done, done); else done();
  });

  /* ---------- promo popup (once a day, after interest) ---------- */
  var promo = $('#promo');
  if (promo && !document.body.hasAttribute('data-no-promo')) {
    var last = store('lmg_promo'), day = new Date().toISOString().slice(0, 10), fired = false;
    var fire = function () { if (fired || last === day) return; fired = true; store('lmg_promo', day); openLayer('#promo'); };
    if (last !== day) {
      setTimeout(fire, 22000);
      window.addEventListener('scroll', function onS() { if (scrollY > document.body.scrollHeight * 0.55) { window.removeEventListener('scroll', onS); fire(); } }, { passive: true });
    }
  }

  /* ---------- reveal on scroll (content stays visible without JS) ---------- */
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    $$('[data-reveal]').forEach(function (el) { el.classList.add('will-reveal'); io.observe(el); });
  }
})();
