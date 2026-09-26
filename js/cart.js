/* Shopping bag — shared by every page.
   Stores the bag in localStorage (this browser only; nothing is sent anywhere), drives the header bag button + badge, the slide-out
   bag drawer, and quick "Add to bag" controls on the Bishop / Rook product cards. Quick View (js/shop.js) and the checkout page
   (js/checkout.js) use the same API:  window.CheckmatelaBag = { add, remove, setQty, clear, items, count, subtotal, open, close, onChange, FREE_SHIP }.
   Prices/shipping rules are placeholders for the concept site. */
(() => {
  "use strict";
  const KEY = 'checkmatela.bag.v1', FREE_SHIP = 500;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const money = n => '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2 });
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const listeners = [];
  let items = [];

  const valid = i => i && typeof i.key === 'string' && typeof i.id === 'string' && typeof i.name === 'string' && Number(i.price) > 0 && Number.isInteger(i.qty) && i.qty > 0 && i.qty <= 99;
  const load = () => { try { const v = JSON.parse(localStorage.getItem(KEY) || '[]'); items = Array.isArray(v) ? v.filter(valid) : []; } catch (e) { items = []; } };
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) { /* keep in memory */ } changed(); };
  const changed = () => { render(); listeners.forEach(f => { try { f(items); } catch (e) { /* ignore */ } }); };
  const count = () => items.reduce((a, i) => a + i.qty, 0);
  const subtotal = () => items.reduce((a, i) => a + i.price * i.qty, 0);
  const optLabel = o => Object.entries(o || {}).filter(([, v]) => v).map(([k, v]) => (k === 'size' ? 'Size ' : '') + v).join(' · ');
  const keyOf = (id, opts) => id + '|' + Object.entries(opts || {}).sort().map(([k, v]) => k + '=' + v).join(';');

  function add(p, qty = 1) {
    const opts = p.options || {}, key = keyOf(p.id, opts), line = items.find(i => i.key === key);
    if (line) line.qty = Math.min(99, line.qty + qty);
    else items.push({ key, id: p.id, name: p.name, tag: p.tag || '', price: Number(p.price), img: p.img || '', options: opts, qty });
    save(); lastAdded = key;
  }
  const setQty = (key, q) => { const i = items.find(x => x.key === key); if (!i) return; if (q < 1) return remove(key); i.qty = Math.min(99, q); save(); };
  const remove = key => { items = items.filter(i => i.key !== key); save(); };
  const clear = () => { items = []; save(); };
  let lastAdded = null;

  /* ---------------------------------------------------------------- drawer */
  let drawer, overlay, lastFocus = null;
  function build() {
    overlay = document.createElement('div'); overlay.className = 'bag-overlay'; overlay.hidden = true;
    drawer = document.createElement('aside'); drawer.className = 'bag'; drawer.setAttribute('role', 'dialog'); drawer.setAttribute('aria-modal', 'true'); drawer.setAttribute('aria-label', 'Shopping bag'); drawer.setAttribute('aria-hidden', 'true');
    drawer.innerHTML = `
      <header class="bag__head"><h2>Your bag <span class="bag__n"></span></h2><button type="button" class="bag__x" aria-label="Close bag">×</button></header>
      <div class="bag__ship" aria-live="polite"></div>
      <ul class="bag__list"></ul>
      <div class="bag__empty" hidden><p>Your bag is empty.</p><p class="muted">Every piece is named for a chess opening — start with a King, or shop by piece.</p>
        <div class="bag__links"><a class="btn small" href="king.html">Shop King</a><a class="btn small dark-ghost" href="pawn.html">Shop Pawn</a></div></div>
      <footer class="bag__foot"><div class="bag__row"><span>Subtotal</span><b class="bag__sub"></b></div><p class="bag__note">Shipping and tax are calculated at checkout.</p>
        <a class="btn bag__checkout" href="checkout.html">Checkout</a><button type="button" class="bag__continue">Continue shopping</button></footer>`;
    document.body.append(overlay, drawer);
    overlay.addEventListener('click', close); $('.bag__x', drawer).addEventListener('click', close); $('.bag__continue', drawer).addEventListener('click', close);
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && drawer.classList.contains('is-open')) close(); });
    drawer.addEventListener('click', e => {
      const b = e.target.closest('[data-act]'); if (!b) return; const li = b.closest('[data-key]'), key = li && li.dataset.key, line = items.find(i => i.key === key);
      if (b.dataset.act === 'inc') setQty(key, line.qty + 1); else if (b.dataset.act === 'dec') setQty(key, line.qty - 1); else if (b.dataset.act === 'rm') remove(key);
    });
  }
  function open() {
    if (!drawer) return; lastFocus = document.activeElement; overlay.hidden = false; drawer.setAttribute('aria-hidden', 'false');
    setTimeout(() => { overlay.classList.add('is-on'); drawer.classList.add('is-open'); }, 20); document.body.classList.add('bag-open');
    setTimeout(() => { const t = $('.bag__x', drawer); if (t) t.focus(); }, 60);
  }
  function close() {
    if (!drawer) return; overlay.classList.remove('is-on'); drawer.classList.remove('is-open'); drawer.setAttribute('aria-hidden', 'true'); document.body.classList.remove('bag-open');
    setTimeout(() => { overlay.hidden = true; }, 300); if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function render() {
    const n = count();
    $$('.bag-count').forEach(b => { b.textContent = n > 99 ? '99+' : n; b.hidden = !n; });
    $$('button[aria-label^="Bag"]').forEach(b => b.setAttribute('aria-label', n ? `Bag, ${n} item${n > 1 ? 's' : ''}` : 'Bag'));
    if (!drawer) return;
    $('.bag__n', drawer).textContent = n ? `(${n})` : '';
    const list = $('.bag__list', drawer), empty = $('.bag__empty', drawer), foot = $('.bag__foot', drawer), ship = $('.bag__ship', drawer), sub = subtotal();
    empty.hidden = n > 0; foot.hidden = !n; list.hidden = !n; ship.hidden = !n;
    const left = FREE_SHIP - sub;
    ship.innerHTML = n ? (left > 0 ? `<span>You're <b>${money(left)}</b> away from free white-glove shipping</span>` : `<span><b>Free white-glove shipping</b> unlocked</span>`) + `<i class="bag__meter"><u style="width:${Math.min(100, sub / FREE_SHIP * 100)}%"></u></i>` : '';
    list.innerHTML = items.map(i => `
      <li class="bag__item${i.key === lastAdded ? ' is-new' : ''}" data-key="${esc(i.key)}">
        <img src="${esc(i.img)}" alt="" loading="lazy">
        <div class="bag__info"><b>${esc(i.name)}</b><span>${esc(i.tag)}</span>${optLabel(i.options) ? `<em>${esc(optLabel(i.options))}</em>` : ''}
          <div class="bag__qty"><button type="button" data-act="dec" aria-label="Decrease quantity">−</button><span aria-live="polite">${i.qty}</span><button type="button" data-act="inc" aria-label="Increase quantity">+</button></div></div>
        <div class="bag__side"><b>${money(i.price * i.qty)}</b><button type="button" class="bag__rm" data-act="rm">Remove</button></div>
      </li>`).join('');
    $('.bag__sub', drawer).textContent = money(sub);
    lastAdded = null;
  }

  /* ---------------------------------------------------------------- header button + static product cards */
  function wireHeader() {
    $$('button[aria-label^="Bag"]').forEach(b => {
      b.style.position = 'relative'; b.setAttribute('aria-haspopup', 'dialog');
      if (!$('.bag-count', b)) { const s = document.createElement('span'); s.className = 'bag-count'; s.hidden = true; b.appendChild(s); }
      b.addEventListener('click', open);
    });
  }
  function staticCards() {
    if ($('[data-shop]') || !/(bishop|rook)/.test(location.pathname)) return;
    const shoes = /rook/.test(location.pathname);
    $$('.product-card').forEach(card => {
      const name = ($('h4', card) || {}).textContent, tag = ($('.piece-tag', card) || {}).textContent, price = parseFloat((($('.product-card__price', card) || {}).textContent || '').replace(/[^0-9.]/g, '')), img = ($('img', card) || {}).getAttribute && $('img', card).getAttribute('src');
      if (!name || !price) return;
      const id = (shoes ? 'rook/' : 'bishop/') + name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      const q = document.createElement('div'); q.className = 'quick-add';
      q.innerHTML = (shoes ? `<label class="visually-hidden" for="qa-${id}">Size</label><select id="qa-${id}" class="quick-add__size"><option value="">Size</option>${[7, 8, 9, 10, 11, 12, 13].map(s => `<option>${s}</option>`).join('')}</select>` : '') + `<button type="button" class="btn small quick-add__btn">Add to bag</button><span class="quick-add__msg" role="status"></span>`;
      card.appendChild(q);
      q.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); });
      $('.quick-add__btn', q).addEventListener('click', () => {
        const sel = $('.quick-add__size', q), msg = $('.quick-add__msg', q);
        if (sel && !sel.value) { msg.textContent = 'Choose a size'; sel.focus(); return; }
        msg.textContent = ''; add({ id, name, tag, price, img, options: sel ? { size: sel.value } : {} }); open();
      });
    });
  }

  window.CheckmatelaBag = { add, remove, setQty, clear, items: () => items.slice(), count, subtotal, open, close, onChange: f => listeners.push(f), FREE_SHIP, money, optLabel };
  window.addEventListener('storage', e => { if (e.key === KEY) { load(); changed(); } });
  load();                                   // read the saved bag right away so other scripts (checkout) see it
  const start = () => { build(); wireHeader(); staticCards(); changed(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
