/* Build-your-hamper: pick a box, pick items, show the photo of that exact combination.
   Photo for a combination: {photoDir}/{boxId}/{item numbers, sorted, joined by "-"}.webp
   e.g. /uploads/hamper/kraft/1-3.webp ; empty box: /uploads/hamper/kraft/box.webp */
(function () {
  'use strict';
  var WA = '918588877032';
  var $ = function (s) { return document.querySelector(s); };
  var root = $('#hb'); if (!root) return;
  var D, box = null, picked = [], front = $('#hbImgA'), back = $('#hbImgB'), want = '';

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function sorted(a) { return a.slice().sort(function (x, y) { return (+x - +y) || (x < y ? -1 : 1); }); }
  function key(ids) { return ids.length ? sorted(ids).join('-') : 'box'; }
  function photo(b, ids) { return D.photoDir + '/' + b.id + '/' + key(ids) + '.webp'; }
  function item(id) { return D.items[id] || { name: 'Item ' + id, photo: '' }; }

  fetch('/build-your-hamper/hampers.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
    D = d; D.photoDir = (D.photoDir || '/uploads/hamper').replace(/\/$/, '');
    renderBoxes();
    var q = new URLSearchParams(location.search), b = D.boxes.filter(function (x) { return x.id === q.get('box'); })[0];
    if (b) {
      var ids = (q.get('items') || '').split('-').filter(function (i) { return b.items.indexOf(i) > -1; });
      chooseBox(b, ids.slice(0, b.max), true);
    }
  }).catch(function () {
    $('#hbBoxes').innerHTML = '<p class="hb-hint">Could not load hampers. Please refresh, or <a href="https://wa.me/' + WA + '">WhatsApp us</a>.</p>';
  });

  /* ---------- step 1: boxes ---------- */
  function renderBoxes() {
    $('#hbBoxes').innerHTML = D.boxes.map(function (b) {
      return '<button type="button" class="hb-opt" data-box="' + esc(b.id) + '" aria-pressed="false">' +
        '<img src="' + esc(photo(b, [])) + '" alt="" width="400" height="400" loading="lazy" decoding="async">' +
        '<span class="hb-opt-name">' + esc(b.name) + '</span>' +
        '<span class="hb-opt-sub">' + (b.note ? esc(b.note) + ' · ' : '') + 'fits up to ' + b.max + ' item' + (b.max > 1 ? 's' : '') + '</span></button>';
    }).join('');
  }
  $('#hbBoxes').addEventListener('click', function (e) {
    var t = e.target.closest('[data-box]'); if (!t) return;
    var b = D.boxes.filter(function (x) { return x.id === t.dataset.box; })[0];
    if (b === box) return;
    // keep items that also fit the new box
    chooseBox(b, picked.filter(function (i) { return b.items.indexOf(i) > -1; }).slice(0, b.max));
    if (window.matchMedia('(max-width: 899px)').matches) $('#hbItemsStep').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  function chooseBox(b, ids, initial) {
    box = b; picked = ids || [];
    root.classList.add('has-box');
    document.querySelectorAll('[data-box]').forEach(function (el) { el.setAttribute('aria-pressed', String(el.dataset.box === b.id)); });
    $('#hbItemsStep').hidden = false;
    $('#hbItems').innerHTML = b.items.map(function (id) {
      var it = item(id);
      return '<button type="button" class="hb-opt" data-item="' + esc(id) + '" aria-pressed="false">' +
        '<img src="' + esc(it.photo) + '" alt="" width="400" height="400" loading="lazy" decoding="async">' +
        '<span class="hb-opt-name">' + esc(it.name) + '</span><span class="hb-tick" aria-hidden="true">✓</span></button>';
    }).join('');
    update(initial);
  }

  /* ---------- step 2: items ---------- */
  $('#hbItems').addEventListener('click', function (e) {
    var t = e.target.closest('[data-item]'); if (!t || t.disabled) return;
    toggle(t.dataset.item);
  });
  $('#hbChosen').addEventListener('click', function (e) {
    var t = e.target.closest('[data-rm]'); if (t) toggle(t.dataset.rm);
  });
  function toggle(id) {
    var k = picked.indexOf(id);
    if (k > -1) picked.splice(k, 1); else if (picked.length < box.max) picked.push(id); else return;
    update();
  }

  /* ---------- preview ---------- */
  function update(initial) {
    var full = picked.length >= box.max;
    document.querySelectorAll('[data-item]').forEach(function (el) {
      var on = picked.indexOf(el.dataset.item) > -1;
      el.setAttribute('aria-pressed', String(on));
      el.disabled = full && !on;
    });
    var c = $('#hbCount');
    c.textContent = picked.length + ' of ' + box.max + ' added';
    c.classList.toggle('is-full', full);
    $('#hbFull').hidden = !full || box.items.length <= box.max;

    $('#hbTitle').textContent = box.name + (picked.length ? ' with ' + picked.length + ' item' + (picked.length > 1 ? 's' : '') : '');
    $('#hbChosen').innerHTML = picked.map(function (id) {
      return '<li><button type="button" data-rm="' + esc(id) + '" aria-label="Remove ' + esc(item(id).name) + '">' + esc(item(id).name) + '<span aria-hidden="true">✕</span></button></li>';
    }).join('');
    show(photo(box, picked));

    var ok = picked.length > 0;
    $('#hbAdd').disabled = !ok;
    $('#hbWa').setAttribute('aria-disabled', String(!ok));
    $('#hbWa').href = ok ? 'https://wa.me/' + WA + '?text=' + encodeURIComponent(message()) : '#';
    $('#hbHint').textContent = ok ? 'Prices on request. We reply on WhatsApp within minutes.' : 'Pick at least one item for your box.';

    var bar = $('#hbBar'); bar.hidden = previewInView;
    $('#hbBarBox').textContent = box.name;
    $('#hbBarCount').textContent = picked.length + ' of ' + box.max + ' items';

    try { history.replaceState(null, '', location.pathname + '?box=' + encodeURIComponent(box.id) + (picked.length ? '&items=' + key(picked) : '')); } catch (e) {}
    preloadNext();
    if (!initial) {
      var fr = $('#hbFrame'); fr.classList.remove('hb-pop'); void fr.offsetWidth; fr.classList.add('hb-pop');
    }
  }

  // Cross-fade between two <img> layers; if the combination photo is missing, show the box with item thumbnails on top.
  function show(src, isFallback) {
    want = src;
    $('#hbEmpty').hidden = true;
    var img = new Image();
    img.onload = function () {
      if (want !== src) return;
      back.src = src; back.alt = $('#hbTitle').textContent;
      back.classList.add('on'); front.classList.remove('on');
      var t = front; front = back; back = t;
      $('#hbBarImg').src = src;
      var bi = $('#hbBarImg'); bi.classList.remove('hb-pop'); void bi.offsetWidth; bi.classList.add('hb-pop');
      fallback(isFallback && picked.length);
    };
    img.onerror = function () {
      if (want !== src) return;
      if (!isFallback) return show(photo(box, []), true);
      front.classList.remove('on'); fallback(true); // no box photo either
    };
    img.src = src;
  }
  function fallback(on) {
    $('#hbFallbackItems').innerHTML = on ? picked.map(function (id) { return '<img src="' + esc(item(id).photo) + '" alt="' + esc(item(id).name) + '" width="88" height="88">'; }).join('') : '';
    $('#hbFallback').hidden = !on;
  }
  // Warm the cache for every photo one tap away, so switching feels instant.
  function preloadNext() {
    box.items.forEach(function (id) {
      var k = picked.indexOf(id), next = picked.slice();
      if (k > -1) next.splice(k, 1); else if (next.length < box.max) next.push(id); else return;
      new Image().src = photo(box, next);
    });
  }

  // On phones the preview sits below the items, so a small bar with the live photo follows the shopper
  // and hides itself once the full preview is on screen.
  var previewInView = false;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) {
      previewInView = en[0].isIntersecting;
      if (box) $('#hbBar').hidden = previewInView;
    }, { threshold: 0.25 }).observe($('#hbPreview'));
  }

  /* ---------- quantity, note, order ---------- */
  function qty() { return Math.max(1, Math.min(9999, parseInt($('#hbQty').value, 10) || 1)); }
  root.addEventListener('click', function (e) {
    var b = e.target.closest('[data-qty]'); if (!b) return;
    $('#hbQty').value = Math.max(1, qty() + (+b.dataset.qty)); if (box) update(true);
  });
  $('#hbQty').addEventListener('change', function () { $('#hbQty').value = qty(); if (box) update(true); });
  $('#hbNote').addEventListener('input', function () { if (box && picked.length) $('#hbWa').href = 'https://wa.me/' + WA + '?text=' + encodeURIComponent(message()); });

  function code() { return (box.id + '-' + key(picked)).toUpperCase(); }
  function link() { return location.origin + location.pathname + '?box=' + encodeURIComponent(box.id) + '&items=' + key(picked); }
  function message() {
    var note = $('#hbNote').value.trim();
    return ['Hi! I built a hamper on the website. Please share the price.',
      'Box: ' + box.name,
      'Items:'].concat(sorted(picked).map(function (id) { return '- ' + item(id).name; }))
      .concat(['Quantity: ' + qty(), note && 'Note: ' + note, 'Hamper code: ' + code(), link()]).filter(Boolean).join('\n');
  }

  $('#hbAdd').addEventListener('click', function () {
    if (!box || !picked.length) return;
    var l = store('lmg_list') || [], s = 'hamper-' + box.id + '-' + key(picked), note = $('#hbNote').value.trim();
    var name = 'Custom hamper: ' + box.name + ' with ' + sorted(picked).map(function (id) { return item(id).name; }).join(', ');
    var f = l.filter(function (i) { return i.s === s; })[0];
    if (f) { f.q = (f.q || 1) + qty(); if (note) f.b = note; }
    else l.push({ s: s, n: name, t: (front.src || photo(box, [])).replace(location.origin, ''), q: qty(), b: note, u: link().replace(location.origin, '') });
    store('lmg_list', l);
    document.querySelectorAll('[data-list-count]').forEach(function (b) { b.textContent = l.length; b.hidden = !l.length; });
    var t = $('#toast');
    if (t) {
      t.innerHTML = '<span>Hamper added to your enquiry list</span><a href="/cart/" class="font-semibold text-butter whitespace-nowrap">View list →</a>';
      t.hidden = false; clearTimeout(t._h); t._h = setTimeout(function () { t.hidden = true; }, 2600);
    }
  });
})();
