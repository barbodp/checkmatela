/* Product detail pages (Antonio Uomo, Gioberti): photo gallery, option pickers (dropdowns; chip buttons still work) and "Add to preview bag" (js/cart.js). Nothing is sent anywhere. */
(() => {
  "use strict";
  const root = document.getElementById("pdp");
  if (!root) return;
  const $ = (s, r = root) => r.querySelector(s), $$ = (s, r = root) => [...r.querySelectorAll(s)];
  const main = $("#pdpMain"), frame = $("#pdpFrame"), msg = $(".pdp-msg"), add = $(".pdp-add");
  const groups = $$(".pdp-opt:not(.pdp-colour)");                 // the option dropdowns (the colour row of a one-colour page is just information)
  const colorGallery = $("[data-color-gallery]");
  const visiblePhotos = () => $$(".pdp-thumb").filter(t => !t.hidden);
  const galleryStatus = () => {
    if (!colorGallery) return;
    const photos = visiblePhotos(), index = photos.findIndex(t => t.dataset.src === main.getAttribute("src"));
    const current = photos[index];
    $("[data-gallery-status]").textContent = current ? `${current.dataset.colour} · ${index + 1} / ${photos.length}` : "";
    [$("[data-gallery-prev]"), $("[data-gallery-next]")].forEach(b => { b.disabled = photos.length < 2; });
  };

  const show = (src, w, h) => {
    main.src = src;
    if (colorGallery) root.dataset.img = src;
    if (w && h && !colorGallery) frame.style.setProperty("--r", (w / h).toFixed(4));
    $$(".pdp-thumb").forEach(t => {
      const active = t.dataset.src === src;
      t.classList.toggle("is-active", active);
      if (colorGallery) t.setAttribute("aria-pressed", String(active));
      if (active && t.dataset.label) main.alt = t.dataset.label;
    });
    galleryStatus();
  };
  /* the chosen colour (name + swatch photo) next to the Colour label, so the customer always sees which colour is on screen */
  const showChosen = g => {
    const c = $(".pdp-opt__chosen", g), s = $("select", g); if (!c || !s) return;
    const o = s.selectedOptions[0], im = $("img", c);
    $("span", c).textContent = o && o.value ? o.value : "";
    if (o && o.value && o.dataset.thumb) { im.src = o.dataset.thumb; im.hidden = false; } else im.hidden = true;
  };
  /* a combined listing (colour + sleeve): show the photo of the chosen colour in the chosen sleeve, when there is one */
  const matchPhoto = () => {
    const sl = groups.find(x => x.dataset.key === "sleeve"), cg = groups.find(x => $(".pdp-opt__chosen", x));
    if (!sl || !cg) return;
    const c = valueOf(cg), v = valueOf(sl);
    const t = c && v && $$(".pdp-thumb").find(b => b.dataset.colour === c && b.dataset.sleeve === v);
    if (t) show(t.dataset.src, t.dataset.w, t.dataset.h);
  };
  /* a gallery photo of one colour selects that colour */
  $$(".pdp-thumb").forEach(b => b.addEventListener("click", () => {
    show(b.dataset.src, b.dataset.w, b.dataset.h);
    const g = groups.find(x => $(".pdp-opt__chosen", x)), s = g && $("select", g);
    if (s && b.dataset.colour && s.value !== b.dataset.colour && [...s.options].some(o => o.value === b.dataset.colour)) {
      s.value = b.dataset.colour; g.classList.remove("is-missing"); showChosen(g); syncVariants();
    }
    const sl = groups.find(x => x.dataset.key === "sleeve"), ss = sl && $("select", sl);
    if (ss && b.dataset.sleeve && ss.value !== b.dataset.sleeve) {
      ss.value = b.dataset.sleeve; sl.classList.remove("is-missing"); syncVariants();
    }
  }));

  /* the chosen value of an option group: a <select> or a row of chip buttons */
  const valueOf = g => { const s = $("select", g); if (s) return s.value || null; const on = $(".chip-btn[aria-pressed=true]", g); return on ? on.dataset.v : null; };
  const filterColorGallery = () => {
    if (!colorGallery) return;
    const group = groups.find(g => g.dataset.key === "color"), color = group && valueOf(group);
    $$(".pdp-thumb").forEach(t => { t.hidden = t.dataset.colour !== color; });
    const first = visiblePhotos()[0];
    if (first) show(first.dataset.src, first.dataset.w, first.dataset.h);
    else { main.removeAttribute("src"); main.alt = "Choose a color to see its photos"; galleryStatus(); }
  };
  if (colorGallery) {
    const step = delta => {
      const photos = visiblePhotos();
      if (!photos.length) return;
      const current = photos.findIndex(t => t.dataset.src === main.getAttribute("src"));
      const next = photos[(current + delta + photos.length) % photos.length];
      show(next.dataset.src, next.dataset.w, next.dataset.h);
    };
    $("[data-gallery-prev]").addEventListener("click", () => step(-1));
    $("[data-gallery-next]").addEventListener("click", () => step(1));
    colorGallery.addEventListener("keydown", e => {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") { e.preventDefault(); step(e.key === "ArrowLeft" ? -1 : 1); }
    });
  }

  /* Gioberti pages: #pdpVariants = {n: number of options, v: [[option values…, price, in stock 0/1], …]}. Every value stays listed; one with
     no in-stock combination (given the other choice) reads "— sold out", the price follows the selection, and a sold-out combination can't be added. */
  const vEl = document.getElementById("pdpVariants"), V = vEl ? JSON.parse(vEl.textContent) : null;
  const priceEl = $(".pdp-price"), fmt = n => "$" + (n % 1 ? n.toFixed(2) : n);
  const allOut = V && !V.v.some(r => r[V.n + 1]);
  let comboOut = false;
  function syncVariants() {
    if (!V) return;
    const sel = groups.map(valueOf);
    const fits = (r, skip) => sel.every((s, i) => i === skip || s === null || r[i] === s);
    groups.forEach((g, gi) => {
      const s = $("select", g);
      if (s) [...s.options].forEach(o => { if (!o.value) return; const ok = V.v.some(r => r[V.n + 1] && fits(r, gi) && r[gi] === o.value); o.textContent = o.value + (ok ? "" : " — sold out"); });
      else $$(".chip-btn", g).forEach(b => { const ok = V.v.some(r => r[V.n + 1] && fits(r, gi) && r[gi] === b.dataset.v); b.classList.toggle("is-out", !ok); });
    });
    const rows = V.v.filter(r => fits(r, -1)), live = rows.filter(r => r[V.n + 1]), ps = (live.length ? live : rows).map(r => r[V.n]);
    if (ps.length) { const lo = Math.min(...ps), hi = Math.max(...ps); priceEl.firstChild.textContent = lo === hi ? fmt(lo) : "From " + fmt(lo); root.dataset.price = lo; }
    comboOut = allOut || (sel.every(s => s !== null) && !live.length);
    add.disabled = comboOut; add.textContent = comboOut ? "Sold out" : "Add to preview bag";
    msg.textContent = comboOut && !allOut ? "That combination is sold out. Try another colour or size." : "";
  }

  groups.forEach(g => {
    const s = $("select", g);
    if (s) s.addEventListener("change", () => {
      g.classList.remove("is-missing");
      const o = s.selectedOptions[0];
      if (o && o.dataset.img && !(colorGallery && g.dataset.key === "color")) show(o.dataset.img, o.dataset.w, o.dataset.h);
      showChosen(g); matchPhoto(); msg.textContent = ""; syncVariants();
      if (g.dataset.key === "color") filterColorGallery();
    });
    else g.addEventListener("click", e => {
      const b = e.target.closest(".chip-btn"); if (!b) return;
      $$(".chip-btn", g).forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
      g.classList.remove("is-missing"); msg.textContent = "";
      if (b.dataset.img) show(b.dataset.img, b.dataset.w, b.dataset.h);
      syncVariants();
    });
  });
  groups.forEach(showChosen);
  syncVariants();
  filterColorGallery();

  const dlg = $("#sizeChart"), opener = $("[data-open-chart]");
  if (dlg && opener) {
    opener.addEventListener("click", () => dlg.showModal());
    $(".shop-dialog__x", dlg).addEventListener("click", () => dlg.close());
    dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); });
    if (location.hash === "#size-chart") dlg.showModal();            // linked from the King Quick View
  }

  add.addEventListener("click", () => {
    if (comboOut) return;
    const opts = {}; let missing = null;
    groups.forEach(g => { const v = valueOf(g); if (v) opts[g.dataset.key] = v; else if (!missing) missing = g; });
    if (missing) {
      missing.classList.add("is-missing");
      const label = ($(".pdp-opt__label, legend", missing) || {}).textContent || missing.dataset.key;
      msg.textContent = "Choose a " + label.toLowerCase() + " first.";
      const f = $("select, .chip-btn", missing); if (f) f.focus(); return;
    }
    const bag = window.CheckmatelaBag; if (!bag) return;
    bag.add({ id: root.dataset.id, name: root.dataset.name, tag: root.dataset.tag, price: Number(root.dataset.price), img: root.dataset.img, options: opts }, 1);
    msg.textContent = "";
    bag.open();
  });
})();
