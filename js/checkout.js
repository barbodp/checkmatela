/* Checkout preview (checkout.html). Reads the bag from js/cart.js, validates the form as you type, calculates shipping / tax / totals,
   and finishes on a confirmation PREVIEW. Nothing is transmitted or stored: no payment is taken and details never leave the browser.
   Rates, tax and the demo promo code are placeholders (see RATES). */
(() => {
  "use strict";
  const bag = window.CheckmatelaBag;
  if (!bag) return;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const money = n => '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const RATES = { freeOver: bag.FREE_SHIP, standard: 18, express: 35, tax: 0.095, promo: { CHECKMATE10: 0.10 } };

  const form = $('#coForm'), grid = $('.co-grid'), empty = $('.co-empty'), done = $('#coDone');
  const state = { ship: 'standard', promo: null };

  /* ---------------- shipping + totals */
  const shipCost = (id, sub) => id === 'pickup' ? 0 : id === 'express' ? RATES.express : (sub >= RATES.freeOver ? 0 : RATES.standard);
  function shippingOptions(sub) {
    const opts = [
      ['standard', 'White-glove standard', '5–7 business days', shipCost('standard', sub)],
      ['express', 'Express', '2–3 business days', RATES.express],
      ['pickup', 'Pick up at the Los Angeles studio', 'By appointment, usually within 48 hours', 0],
    ];
    $('#shipOptions').innerHTML = opts.map(([id, name, eta, cost]) => `
      <label class="co-opt"><input type="radio" name="ship" value="${id}" ${state.ship === id ? 'checked' : ''}><span><b>${name}</b><small>${eta}</small></span><em>${cost ? money(cost) : 'Free'}</em></label>`).join('');
  }
  function totals() {
    const sub = bag.subtotal(), disc = state.promo ? Math.round(sub * RATES.promo[state.promo] * 100) / 100 : 0, ship = shipCost(state.ship, sub), taxable = sub - disc, tax = Math.round(taxable * RATES.tax * 100) / 100;
    return { sub, disc, ship, tax, total: sub - disc + ship + tax };
  }
  function renderSummary() {
    const items = bag.items();
    empty.hidden = items.length > 0; grid.hidden = items.length === 0;
    if (!items.length) return;
    $('#coItems').innerHTML = items.map(i => `
      <li data-key="${esc(i.key)}"><div class="co-thumb"><img src="${esc(i.img)}" alt=""><span>${i.qty}</span></div>
        <div class="co-item"><b>${esc(i.name)}</b><small>${esc(i.tag)}</small>${bag.optLabel(i.options) ? `<small>${esc(bag.optLabel(i.options))}</small>` : ''}
          <div class="co-qty"><button type="button" data-act="dec" aria-label="Decrease quantity of ${esc(i.name)}">−</button><span>${i.qty}</span><button type="button" data-act="inc" aria-label="Increase quantity of ${esc(i.name)}">+</button><button type="button" class="co-rm" data-act="rm">Remove</button></div></div>
        <b class="co-price">${money(i.price * i.qty)}</b></li>`).join('');
    shippingOptions(bag.subtotal());
    const t = totals();
    $('#tSub').textContent = money(t.sub); $('#tShip').textContent = t.ship ? money(t.ship) : 'Free'; $('#tTax').textContent = money(t.tax); $('#tTotal').textContent = money(t.total);
    $('.co-disc').hidden = !t.disc; $('#tDisc').textContent = '−' + money(t.disc);
  }
  $('#coItems').addEventListener('click', e => {
    const b = e.target.closest('[data-act]'); if (!b) return; const key = b.closest('li').dataset.key, line = bag.items().find(i => i.key === key);
    if (b.dataset.act === 'inc') bag.setQty(key, line.qty + 1); else if (b.dataset.act === 'dec') bag.setQty(key, line.qty - 1); else bag.remove(key);
  });
  $('#shipOptions').addEventListener('change', e => { if (e.target.name === 'ship') { state.ship = e.target.value; renderSummary(); } });
  bag.onChange(() => { if (done.hidden) renderSummary(); });

  /* ---------------- promo */
  $('#promoForm').addEventListener('submit', e => {
    e.preventDefault(); const code = $('#promo').value.trim().toUpperCase(), msg = $('#promoMsg');
    if (!code) { msg.textContent = 'Enter a code.'; msg.className = 'co-promo-msg is-bad'; return; }
    if (RATES.promo[code]) { state.promo = code; msg.textContent = `${code} applied — ${RATES.promo[code] * 100}% off (preview code).`; msg.className = 'co-promo-msg is-ok'; }
    else { state.promo = null; msg.textContent = "That code isn't valid."; msg.className = 'co-promo-msg is-bad'; }
    renderSummary();
  });

  /* ---------------- inline validation */
  const rules = {
    email: v => !v ? 'Enter your email address.' : !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v) ? 'That email address doesn’t look right.' : '',
    phone: v => v && v.replace(/\D/g, '').length < 10 ? 'Enter a 10-digit phone number.' : '',
    first: v => !v.trim() ? 'Enter a first name.' : '', last: v => !v.trim() ? 'Enter a last name.' : '',
    address: v => v.trim().length < 5 ? 'Enter your street address.' : '',
    city: v => !v.trim() ? 'Enter a city.' : '', state: v => !v ? 'Choose a state.' : '',
    zip: v => !/^\d{5}(-\d{4})?$/.test(v.trim()) ? 'Enter a 5-digit ZIP code.' : '',
  };
  const touched = new Set();
  function check(name) {
    const el = form.elements[name]; if (!el || !rules[name]) return true;
    const err = rules[name](el.value), box = $('#e-' + name), wrap = el.closest('.co-field');
    box.textContent = err; el.setAttribute('aria-invalid', err ? 'true' : 'false'); wrap.classList.toggle('is-bad', !!err); wrap.classList.toggle('is-ok', !err && !!el.value);
    return !err;
  }
  Object.keys(rules).forEach(n => { const el = form.elements[n]; if (!el) return; el.addEventListener('blur', () => { touched.add(n); check(n); }); el.addEventListener('input', () => { if (touched.has(n)) check(n); }); el.addEventListener('change', () => { touched.add(n); check(n); }); });
  form.elements.zip.addEventListener('input', e => { e.target.value = e.target.value.replace(/[^\d-]/g, ''); });

  form.addEventListener('submit', e => {
    e.preventDefault();
    if (!bag.count()) return;
    const bad = Object.keys(rules).filter(n => { touched.add(n); return !check(n); }), sum = $('#coSummary');
    if (bad.length) { sum.hidden = false; sum.textContent = `Please fix ${bad.length} field${bad.length > 1 ? 's' : ''} to continue.`; form.elements[bad[0]].focus(); return; }
    sum.hidden = true; showDone();
  });
  $('#editBag').addEventListener('click', e => { e.preventDefault(); bag.open(); });

  /* ---------------- confirmation preview */
  function showDone() {
    const t = totals(), items = bag.items(), f = form.elements, id = 'PREVIEW-' + Math.random().toString(36).slice(2, 8).toUpperCase();
    const shipName = { standard: 'White-glove standard (5–7 business days)', express: 'Express (2–3 business days)', pickup: 'Pick up at the Los Angeles studio' }[state.ship];
    grid.hidden = true; done.hidden = false;
    $('.co-steps li.is-on').classList.replace('is-on', 'is-done'); $$('.co-steps li')[2].classList.add('is-done'); $$('.co-steps li')[3].classList.add('is-on');
    done.innerHTML = `
      <div class="co-done__card">
        <span class="eyebrow">Confirmation preview</span>
        <h2>This is what your confirmation will look like.</h2>
        <p class="co-note"><b>No order was placed.</b> Nothing was charged and none of your details were sent or saved.</p>
        <p class="co-done__no">Preview reference <b>${id}</b></p>
        <div class="co-done__cols">
          <div><h3>Delivery</h3><p>${esc(f.first.value)} ${esc(f.last.value)}<br>${esc(f.address.value)}${f.apt.value ? ', ' + esc(f.apt.value) : ''}<br>${esc(f.city.value)}, ${esc(f.state.value)} ${esc(f.zip.value)}</p><p class="muted">${esc(f.email.value)}</p><h3>Shipping</h3><p>${shipName}</p></div>
          <div><h3>Your pieces</h3><ul class="co-done__list">${items.map(i => `<li><span>${i.qty} × ${esc(i.name)} <small>${esc(bag.optLabel(i.options))}</small></span><b>${money(i.price * i.qty)}</b></li>`).join('')}</ul>
            <dl class="co-totals"><div><dt>Subtotal</dt><dd>${money(t.sub)}</dd></div>${t.disc ? `<div><dt>Discount</dt><dd>−${money(t.disc)}</dd></div>` : ''}<div><dt>Shipping</dt><dd>${t.ship ? money(t.ship) : 'Free'}</dd></div><div><dt>Estimated tax</dt><dd>${money(t.tax)}</dd></div><div class="co-total"><dt>Total</dt><dd>${money(t.total)}</dd></div></dl></div>
        </div>
        <p class="co-done__actions"><button class="btn" type="button" id="doneBack">Back to checkout</button> <button class="btn dark-ghost" type="button" id="doneClear">Clear bag and start over</button> <a class="link" href="king.html">Keep shopping</a></p>
      </div>`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    $('#doneBack').onclick = () => { done.hidden = true; grid.hidden = false; $$('.co-steps li')[3].classList.remove('is-on'); $$('.co-steps li')[2].classList.remove('is-done'); $$('.co-steps li')[1].classList.replace('is-done', 'is-on'); renderSummary(); };
    $('#doneClear').onclick = () => { bag.clear(); location.href = 'index.html'; };
  }

  renderSummary();
})();
