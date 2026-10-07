/* Product detail pages (Antonio Uomo section): photo gallery, size / length pickers and "Add to preview bag" (js/cart.js). Nothing is sent anywhere. */
(() => {
  "use strict";
  const root = document.getElementById("pdp");
  if (!root) return;
  const $ = (s, r = root) => r.querySelector(s), $$ = (s, r = root) => [...r.querySelectorAll(s)];
  const main = $("#pdpMain");

  $$(".pdp-thumb").forEach(b => b.addEventListener("click", () => {
    $$(".pdp-thumb").forEach(t => t.classList.toggle("is-active", t === b));
    main.src = b.dataset.src;
  }));

  $$(".pdp-opt").forEach(g => g.addEventListener("click", e => {
    const b = e.target.closest(".chip-btn"); if (!b) return;
    $$(".chip-btn", g).forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
    g.classList.remove("is-missing"); $(".pdp-msg").textContent = "";
  }));

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
