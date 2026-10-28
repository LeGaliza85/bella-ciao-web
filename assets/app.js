/* Bella Ciao — runtime: i18n, canales y render de carta. */
(function () {
  'use strict';
  window.addEventListener('error', function (e) {
    document.documentElement.setAttribute('data-bc-error', String(e.message) + ' @ ' + (e.lineno || '?'));
  });
  var D = window.BC.data, T = window.BC_T;
  var LANGS = ['ca', 'es', 'fr', 'en'];
  var state = { lang: 'es', channel: 'restaurant' };
  var SERIF = "'Fraunces', Georgia, serif";

  /* ------------------------------------------------------------ i18n */
  function t(es) {
    if (state.lang === 'es') return es;
    var e = T[es];
    return (e && e[state.lang]) || es;
  }
  var ORIG = new WeakMap();
  function translateDom() {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        var tag = p.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return NodeFilter.FILTER_REJECT;
        if (p.closest('[data-noi18n]')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      if (!ORIG.has(node)) ORIG.set(node, node.nodeValue);
      var orig = ORIG.get(node);
      if (!orig || !orig.trim()) return;
      var lead = orig.match(/^\s*/)[0], tail = orig.match(/\s*$/)[0];
      node.nodeValue = lead + t(orig.trim().replace(/\s+/g, ' ')) + tail;
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-attr');
      if (!el.dataset.origLabel) el.dataset.origLabel = el.getAttribute('aria-label') || '';
      var orig = el.dataset.origLabel;
      if (orig) el.setAttribute('aria-label', t(orig));
    });
  }

  /* ------------------------------------------------------- helpers */
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function slug(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }
  function row(it) {
    var r = el('div', 'menu-row');
    var line = el('div', 'menu-line');
    line.appendChild(el('div', 'menu-name', it.name[state.lang] || it.name.es));
    line.appendChild(el('div', 'menu-price', it.price));
    r.appendChild(line);
    var d = it.desc[state.lang] || it.desc.es;
    if (d) r.appendChild(el('div', 'menu-desc', d));
    return r;
  }
  function cols(items) {
    var wrap = el('div', 'menu-cols');
    var half = Math.ceil(items.length / 2);
    [items.slice(0, half), items.slice(half)].forEach(function (part) {
      var c = el('div', 'menu-col');
      part.forEach(function (it) { c.appendChild(row(it)); });
      wrap.appendChild(c);
    });
    return wrap;
  }
  function block(b, i) {
    var wrap = el('section', 'menu-block');
    wrap.id = b.id;
    var head = el('div', 'block-head');
    var left = el('div');
    left.appendChild(el('div', 'num', ('0' + (i + 1)).slice(-2)));
    left.appendChild(el('h3', '', b.title[state.lang] || b.title.es));
    if (b.note) left.appendChild(el('p', '', b.note[state.lang] || b.note.es));
    head.appendChild(left);
    var count = b.groups.reduce(function (a, g) { return a + g.items.length; }, 0);
    head.appendChild(el('div', 'count', count + ' ' + t('PLATOS')));
    wrap.appendChild(head);
    b.groups.forEach(function (g) {
      if (g.label) wrap.appendChild(el('div', 'menu-group-label', (g.label[state.lang] || g.label.es)));
      wrap.appendChild(cols(g.items));
    });
    return wrap;
  }

  /* --------------------------------------------------------- render */
  function renderCarta() {
    var host = document.getElementById('menu-body');
    if (!host) return;
    host.innerHTML = '';
    lastActive = null;
    D.channels[state.channel].blocks.forEach(function (b, i) { host.appendChild(block(b, i)); });
  }
  function renderPreview() {
    var host = document.getElementById('preview-panel');
    if (!host) return;
    host.innerHTML = '';
    var pizze = D.channels[state.channel].blocks[0];
    var items = [];
    pizze.groups.forEach(function (g) { items = items.concat(g.items); });
    items = items.slice(0, 6);
    var head = el('div', 'menu-panel-head');
    head.appendChild(el('h3', '', pizze.title[state.lang] || pizze.title.es));
    head.appendChild(el('p', '', (pizze.note[state.lang] || pizze.note.es) + ' · ' + t('Extras desde 1,50')));
    host.appendChild(head);
    host.appendChild(cols(items));
  }
  function scrollToY(y) {
    var start = window.pageYOffset;
    try { window.scrollTo({ top: y, behavior: 'smooth' }); } catch (e) { window.scrollTo({ top: y, behavior: 'instant' }); return; }
    setTimeout(function () {
      if (Math.abs(window.pageYOffset - start) < 8 && Math.abs(window.pageYOffset - y) > 8) {
        window.scrollTo({ top: y, behavior: 'instant' });
      }
    }, 420);
  }

  function headerH() { return document.querySelector('.site-header').offsetHeight; }
  function indexH() { var i = document.getElementById('menu-index'); return i ? i.offsetHeight : 0; }
  function offsetTop() { return headerH() + indexH() + 14; }

  function syncHeaderVar() {
    document.documentElement.style.setProperty('--header-h', headerH() + 'px');
    document.documentElement.style.scrollPaddingTop = offsetTop() + 'px';
  }

  function centerTab(tab) {
    var bar = document.getElementById('menu-index');
    if (!bar || bar.scrollWidth <= bar.clientWidth + 2) return;
    var target = Math.max(0, tab.offsetLeft - (bar.clientWidth - tab.offsetWidth) / 2);
    var start = bar.scrollLeft;
    try { bar.scrollTo({ left: target, behavior: 'smooth' }); } catch (e) { bar.scrollLeft = target; return; }
    setTimeout(function () {
      if (Math.abs(bar.scrollLeft - start) < 4 && Math.abs(bar.scrollLeft - target) > 4) bar.scrollLeft = target;
    }, 300);
  }

  var lastActive = null;
  var io = null;
  function watchBlocks() {
    if (!('IntersectionObserver' in window)) return;
    if (io) io.disconnect();
    io = new IntersectionObserver(function () { spy(); }, { rootMargin: '-120px 0px -55% 0px', threshold: 0 });
    document.querySelectorAll('#menu-body .menu-block').forEach(function (b) { io.observe(b); });
  }
  function renderIndex() {
    var host = document.getElementById('menu-index');
    if (!host) return;
    host.innerHTML = '';
    D.channels[state.channel].blocks.forEach(function (b, i) {
      var a = el('a', 'tab', (window.BC_SHORT[b.id] && window.BC_SHORT[b.id][state.lang]) || b.title[state.lang] || b.title.es);
      a.href = '#' + b.id;
      a.setAttribute('data-target', b.id);
      if (i === 0) { a.classList.add('is-active'); a.setAttribute('aria-current', 'true'); }
      a.addEventListener('click', function (e) {
        var target = document.getElementById(b.id);
        if (!target) return;
        e.preventDefault();
        var top = target.getBoundingClientRect().top + window.pageYOffset - offsetTop();
        scrollToY(top);
        history.replaceState(null, '', '#' + b.id);
      });
      host.appendChild(a);
    });
  }

  function spy() {
    var bar = document.getElementById('menu-index');
    if (!bar) return;
    var blocks = document.querySelectorAll('#menu-body .menu-block');
    if (!blocks.length) return;
    var line = offsetTop() + 8;
    var current = blocks[0];
    blocks.forEach(function (b) { if (b.getBoundingClientRect().top - line <= 0) current = b; });
    var active = null;
    bar.querySelectorAll('.tab').forEach(function (t) {
      var on = t.getAttribute('data-target') === current.id;
      t.classList.toggle('is-active', on);
      if (on) { active = t; t.setAttribute('aria-current', 'true'); } else { t.removeAttribute('aria-current'); }
    });
    if (active) { var id = active.getAttribute('data-target'); if (id !== lastActive) { lastActive = id; centerTab(active); } }
    bar.classList.toggle('is-stuck', bar.getBoundingClientRect().top <= headerH() + 1);
  }

  function applyHeader() {
    var title = document.getElementById('menu-title');
    var intro = document.getElementById('menu-intro');
    if (!title) return;
    var blocks = D.channels[state.channel].blocks;
    var n = blocks.reduce(function (a, b) { return a + b.groups.reduce(function (x, g) { return x + g.items.length; }, 0); }, 0);
    if (state.channel === 'delivery') {
      title.textContent = t('Carta delivery y take away');
      intro.textContent = t('Pedidos a domicilio y para llevar. Llámanos y te lo llevamos.') + ' ' + n + ' ' + t('platos') + ' · ' + blocks.length + ' ' + t('secciones') + '.';
    } else {
      title.textContent = t('Toda la carta, de un vistazo.');
      intro.textContent = n + ' ' + t('platos') + ' · ' + blocks.length + ' ' + t('secciones') + '. ' + t('Masa fermentada 48 horas, pasta fresca hecha cada mañana y proveedores italianos.');
    }
  }
  function paint() {
    document.documentElement.lang = state.lang;
    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === state.lang));
    });
    document.querySelectorAll('[data-channel]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-channel') === state.channel));
    });
    document.querySelectorAll('[data-call-label]').forEach(function (b) {
      b.textContent = t('Llamar');
    });
  }
  function renderAll() {
    paint();
    translateDom();
    applyHeader();
    renderCarta();
    renderIndex();
    renderPreview();
    syncHeaderVar();
    watchBlocks();
    spy();
  }

  /* ---------------------------------------------------------- estado */
  function save() {
    try {
      localStorage.setItem('bc.lang', state.lang);
      localStorage.setItem('bc.channel', state.channel);
      var u = new URL(location.href);
      u.searchParams.set('lang', state.lang);
      u.searchParams.set('canal', state.channel);
      history.replaceState(null, '', u);
    } catch (e) { /* file:// o modo privado */ }
  }
  function setLang(l) { if (LANGS.indexOf(l) < 0) return; state.lang = l; save(); renderAll(); }
  function setChannel(c) { if (c !== 'restaurant' && c !== 'delivery') return; state.channel = c; save(); renderAll(); }
  function load() {
    var p = new URLSearchParams(location.search);
    var l = p.get('lang'), c = p.get('canal');
    try { l = l || localStorage.getItem('bc.lang'); c = c || localStorage.getItem('bc.channel'); } catch (e) { }
    state.lang = LANGS.indexOf(l) >= 0 ? l : 'es';
    state.channel = (c === 'delivery' || c === 'restaurant') ? c : 'restaurant';
  }
  function bind() {
    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
    });
    document.querySelectorAll('[data-channel]').forEach(function (b) {
      b.addEventListener('click', function () { setChannel(b.getAttribute('data-channel')); });
    });
    // enlaces a secciones dentro de la misma página
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href').slice(1);
        var target = id && document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        var top = target.getBoundingClientRect().top + window.pageYOffset - offsetTop();
        scrollToY(top);
      });
    });
  }

  function init() {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    load();
    bind();
    renderAll();
    syncHeaderVar();
    var lastSpy = 0;
    window.addEventListener('scroll', function () {
      var now = Date.now();
      if (now - lastSpy < 90) return;
      lastSpy = now;
      spy();
    }, { passive: true });
    window.addEventListener('resize', function () { syncHeaderVar(); spy(); });
    // respaldo: algunos visores integrados no emiten scroll; sondeamos la posición
    var pollY = -1;
    if (document.getElementById('menu-index')) {
      setInterval(function () {
        if (window.scrollY === pollY) return;
        pollY = window.scrollY;
        spy();
      }, 320);
    }
    window.addEventListener('load', function () { syncHeaderVar(); spy(); });
    setTimeout(function () { syncHeaderVar(); spy(); }, 200);
    if (location.hash) {
      var jump = function () {
        var target = document.getElementById(location.hash.slice(1));
        if (!target) return;
        var y = target.getBoundingClientRect().top + window.pageYOffset - offsetTop();
        window.scrollTo({ top: y, behavior: 'instant' });
      };
      setTimeout(jump, 80);
      setTimeout(function () {
        var target = document.getElementById(location.hash.slice(1));
        if (!target) return;
        var want = target.getBoundingClientRect().top - offsetTop();
        if (Math.abs(want) > 6) jump();
      }, 450);
    }
    window.BC.spy = spy;
    window.BC.setLang = setLang;
    window.BC.setChannel = setChannel;
    window.BC.state = state;
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
