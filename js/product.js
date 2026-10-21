/* Product detail pages (Antonio Uomo section): photo gallery, size / length pickers and "Add to preview bag" (js/cart.js). Nothing is sent anywhere. */
(() => {
  "use strict";
  const root = document.getElementById("pdp");
  if (!root) return;
  const $ = (s, r = root) => r.querySelector(s), $$ = (s, r = root) => [...r.querySelectorAll(s)];
  const main = $("#pdpMain"), frame = $("#pdpFrame");

  $$(".pdp-thumb").forEach(b => b.addEventListener("click", () => {
    $$(".pdp-thumb").forEach(t => t.classList.toggle("is-active", t === b));
    frame.style.setProperty("--r", (b.dataset.w / b.dataset.h).toFixed(4));   // the frame follows each photo's own shape, so it is always filled
    main.src = b.dataset.src;
  }));

  $$(".pdp-opt").forEach(g => g.addEventListener("click", e => {
    const b = e.target.closest(".chip-btn"); if (!b) return;
    $$(".chip-btn", g).forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
    g.classList.remove("is-missing"); $(".pdp-msg").textContent = "";
  }));

  /* Gioberti pages: #pdpVariants = {n: number of options, v: [[option values…, price, in stock 0/1], …]}. Sizes/colours with no in-stock
     combination are disabled, the price follows the selection, and a colour chip with data-img shows that colour's photo. */
  const vEl = document.getElementById("pdpVariants"), V = vEl ? JSON.parse(vEl.textContent) : null;
  const priceEl = $(".pdp-price"), fmt = n => "$" + (n % 1 ? n.toFixed(2) : n);
  function syncVariants() {
    if (!V) return;
    const groups = $$(".pdp-opt"), sel = groups.map(g => { const on = $(".chip-btn[aria-pressed=true]", g); return on ? on.dataset.v : null; });
    const fits = (r, skip) => r[V.n + 1] && sel.every((s, i) => i === skip || s === null || r[i] === s);
    groups.forEach((g, gi) => $$(".chip-btn", g).forEach(b => {
      const ok = V.v.some(r => fits(r, gi) && r[gi] === b.dataset.v);
      b.disabled = !ok;
      if (!ok && b.getAttribute("aria-pressed") === "true") { b.setAttribute("aria-pressed", "false"); sel[gi] = null; }
    }));
    const ps = V.v.filter(r => fits(r, -1)).map(r => r[V.n]);
    if (ps.length) { const lo = Math.min(...ps), hi = Math.max(...ps); priceEl.textContent = lo === hi ? fmt(lo) : "From " + fmt(lo); root.dataset.price = lo; }
  }
  $$(".pdp-opt").forEach(g => g.addEventListener("click", e => {
    const b = e.target.closest(".chip-btn"); if (!b || b.disabled) return;
    if (b.dataset.img) {
      main.src = b.dataset.img; frame.style.setProperty("--r", (b.dataset.w / b.dataset.h).toFixed(4));
      $$(".pdp-thumb").forEach(t => t.classList.toggle("is-active", t.dataset.src === b.dataset.img));
    }
    syncVariants();
  }));
  syncVariants();

  const dlg = $("#sizeChart"), opener = $("[data-open-chart]");
  if (dlg && opener) {
    opener.addEventListener("click", () => dlg.showModal());
    $(".shop-dialog__x", dlg).addEventListener("click", () => dlg.close());
    dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); });
    if (location.hash === "#size-chart") dlg.showModal();            // linked from the King Quick View
  }

  const msg = $(".pdp-msg");
  $(".pdp-add").addEventListener("click", () => {
    const opts = {}; let missing = null;
    $$(".pdp-opt").forEach(g => { const on = $(".chip-btn[aria-pressed=true]", g); if (on) opts[g.dataset.key] = on.dataset.v; else if (!missing) missing = g; });
    if (missing) { missing.classList.add("is-missing"); msg.textContent = "Choose a " + missing.dataset.key + " first."; const f = $(".chip-btn", missing); if (f) f.focus(); return; }
    const bag = window.CheckmatelaBag; if (!bag) return;
    bag.add({ id: root.dataset.id, name: root.dataset.name, tag: root.dataset.tag, price: Number(root.dataset.price), img: root.dataset.img, options: opts }, 1);
    msg.textContent = "";
    bag.open();
  });
})();
