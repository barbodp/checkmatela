(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const catalog = window.CHECKMATELA_CATALOG || [];
  const products = new Map(catalog.map(item => [item.id, item]));
  const money = value => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const header = $('#siteHeader');
  const updateHeader = () => header?.classList.toggle('solid', scrollY > 40);
  document.addEventListener('scroll', updateHeader, {passive:true});
  updateHeader();
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  $$('#mainNav a').forEach(link => {
    if (link.getAttribute('href') === currentPage) link.setAttribute('aria-current', 'page');
  });

  // The mobile menu supports Escape and keeps keyboard focus inside while open.
  const navToggle = $('#navToggle');
  const mainNav = $('#mainNav');
  const mobile = matchMedia('(max-width: 980px)');
  const setMenu = open => {
    mainNav?.classList.toggle('open', open);
    navToggle?.classList.toggle('open', open);
    navToggle?.setAttribute('aria-expanded', String(open));
    navToggle?.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';
    if (mainNav) mainNav.inert = mobile.matches && !open;
    if (open) $('a', mainNav)?.focus();
  };
  navToggle?.addEventListener('click', () => setMenu(!mainNav.classList.contains('open')));
  $$('#mainNav a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  mobile.addEventListener('change', () => setMenu(false));
  setMenu(false);
  document.addEventListener('keydown', event => {
    if (!mainNav?.classList.contains('open')) return;
    if (event.key === 'Escape') { setMenu(false); navToggle.focus(); }
    if (event.key === 'Tab') {
      const targets = [...$$('a', mainNav), navToggle];
      const next = (targets.indexOf(document.activeElement) + (event.shiftKey ? -1 : 1) + targets.length) % targets.length;
      event.preventDefault(); targets[next].focus();
    }
  });

  const revealTargets = $$('[data-reveal], [data-reveal-group]');
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('in'); observer.unobserve(entry.target); }
    }), {threshold:0.08});
    revealTargets.forEach(target => observer.observe(target));
  } else revealTargets.forEach(target => target.classList.add('in'));

  const stage = $('#explodeStage');
  const diagramToggle = $('#diagramToggle');
  if (stage) {
    let manuallyChanged = false;
    const setExploded = state => {
      stage.classList.toggle('exploded', state);
      diagramToggle.setAttribute('aria-pressed', String(state));
      diagramToggle.textContent = state ? 'Assemble the look ↙' : 'Take the look apart ↗';
    };
    const resize = () => {
      const scale = Math.min(1, (stage.clientWidth - 12) / 720);
      stage.style.setProperty('--stage-scale', scale);
      stage.style.height = `${800 * scale + 20}px`;
    };
    resize();
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(stage);
    else window.addEventListener('resize', resize);
    diagramToggle.addEventListener('click', () => { manuallyChanged = true; setExploded(!stage.classList.contains('exploded')); });
    if ('IntersectionObserver' in window && !reducedMotion.matches) {
      const observer = new IntersectionObserver(entries => entries.forEach(entry => {
        if (entry.isIntersecting) {
          if (!manuallyChanged) setExploded(true);
          observer.disconnect();
        }
      }), {threshold:0.22});
      observer.observe(stage);
    } else setExploded(true);
  }

  $$('.newsletter-form').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    form.classList.add('sent');
    const success = form.parentElement.querySelector('.form-success');
    if (success) { success.setAttribute('tabindex','-1'); success.focus(); }
    form.reset();
  }));

  $$('.gallery-card').forEach(card => {
    const main = $('.gallery-card__main-img', card);
    const thumbs = $$('.gallery-thumb', card);
    thumbs.forEach((button, index) => {
      button.setAttribute('aria-pressed', String(index === 0));
      button.addEventListener('click', () => {
        main.src = button.dataset.src;
        main.alt = button.getAttribute('aria-label').replace(/^View /, '');
        thumbs.forEach(thumb => { thumb.classList.toggle('is-active', thumb === button); thumb.setAttribute('aria-pressed', String(thumb === button)); });
      });
    });
  });
  $$('.style-select').forEach(select => select.addEventListener('change', () => {
    if (select.value.endsWith('.html')) location.href = select.value;
    else document.getElementById(select.value)?.scrollIntoView({behavior:reducedMotion.matches ? 'auto' : 'smooth',block:'center'});
  }));
  $$('.filter-bar__sort select').forEach(select => {
    const grid = $('.product-grid, .gallery-grid');
    if (!grid) return;
    const cards = [...grid.children];
    select.addEventListener('change', () => {
      const sorted = [...cards];
      const label = select.value;
      const price = card => products.get(card.dataset.product)?.price || 0;
      if (label === 'Price: Low to High') sorted.sort((a,b) => price(a)-price(b));
      if (label === 'Price: High to Low') sorted.sort((a,b) => price(b)-price(a));
      if (label === 'Name: A to Z') sorted.sort((a,b) => $('h4',a).textContent.localeCompare($('h4',b).textContent));
      sorted.forEach(card => grid.append(card));
    });
  });

  // Only product ids, sample sizes and quantities are saved on this device.
  const storageKey = 'checkmatela-sample-bag-v1';
  let bag = [];
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(stored)) bag = stored.filter(item => item && products.has(item.id) && products.get(item.id).sizes.includes(item.size) && Number.isInteger(item.qty) && item.qty > 0 && item.qty <= 99);
  } catch { /* Browsing still works when device storage is unavailable. */ }
  const updateBag = () => {
    try { localStorage.setItem(storageKey, JSON.stringify(bag)); } catch { /* Keep the bag in memory. */ }
    const total = bag.reduce((sum,item) => sum + item.qty,0);
    $$('.bag-count').forEach(badge => { badge.textContent=total; badge.hidden=!total; });
    $('.bag-btn')?.setAttribute('aria-label', `Open sample bag${total ? `, ${total} items` : ''}`);
  };
  updateBag();

  const dialog = document.createElement('dialog');
  dialog.className = 'shop-dialog';
  dialog.setAttribute('aria-labelledby', 'dialogTitle');
  document.body.append(dialog);
  let returnFocus = null;
  const showDialog = markup => {
    if (!dialog.open) returnFocus = document.activeElement;
    dialog.innerHTML = '<button class="dialog-close" aria-label="Close dialog">×</button>' + markup;
    $('.dialog-close', dialog).addEventListener('click', () => dialog.close());
    if (!dialog.open) dialog.showModal();
    $('.dialog-close', dialog).focus();
  };
  dialog.addEventListener('close', () => { if (returnFocus?.isConnected) returnFocus.focus(); });
  dialog.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });

  const showProduct = id => {
    const item = products.get(id);
    if (!item) return;
    const photos = item.images || [item.image];
    showDialog(`<div class="preview-grid"><div><div class="preview-image"><img src="${escape(item.image)}" alt="${escape(item.name)}" id="previewImage"></div>${photos.length > 1 ? `<div class="preview-thumbs" aria-label="Product views">${photos.map((image,index) => `<button data-image="${escape(image)}" aria-label="View photo ${index+1}" aria-pressed="${index === 0}"><img src="${escape(image.replace(/(?:model|plain)-\d+\.jpg$/,`thumb-${index+1}.jpg`))}" alt=""></button>`).join('')}</div>` : ''}</div><div class="preview-copy"><span class="eyebrow">${escape(item.category)}</span><h2 id="dialogTitle">${escape(item.name)}</h2><p class="preview-tag">${escape(item.tag)}</p><p class="preview-price">${money(item.price)}<small>Sample price</small></p><p class="dialog-note">${escape(item.description)}</p><form id="addToBagForm"><label for="sampleSize">Choose a sample size</label><select id="sampleSize" required><option value="">Select a size</option>${item.sizes.map(size => `<option>${escape(size)}</option>`).join('')}</select><button class="btn" type="submit">Add to sample bag ↗</button></form><p class="dialog-message" role="status" id="bagMessage"></p><a class="text-link" href="${escape(item.page)}">Explore the collection ↗</a><p class="dialog-note">Collection preview. Prices and sizes are illustrative. No payment or order will be taken.</p></div></div>`);
    $$('[data-image]',dialog).forEach(button => button.addEventListener('click', () => {
      $('#previewImage',dialog).src=button.dataset.image;
      $$('[data-image]',dialog).forEach(thumb => thumb.setAttribute('aria-pressed',String(thumb===button)));
    }));
    $('#addToBagForm',dialog).addEventListener('submit', event => {
      event.preventDefault();
      const size = $('#sampleSize',dialog).value;
      if (!item.sizes.includes(size)) return;
      const existing = bag.find(entry => entry.id === id && entry.size === size);
      if (existing) existing.qty = Math.min(existing.qty+1,99);
      else bag.push({id,size,qty:1});
      updateBag();
      $('#bagMessage',dialog).textContent = 'Added to your sample bag.';
      const form = $('#addToBagForm',dialog);
      if (!$('[data-view-bag]',form)) {
        const button=document.createElement('button'); button.type='button'; button.className='text-link'; button.dataset.viewBag=''; button.textContent='View your bag →'; button.addEventListener('click',showBag); form.append(button);
      }
    });
  };
  function showBag() {
    showDialog(`<div class="dialog-body"><span class="eyebrow">Your considered collection</span><h2 id="dialogTitle">The sample bag.</h2>${bag.length ? bag.map((entry,index) => { const item=products.get(entry.id); return `<div class="bag-item"><img src="${escape(item.image)}" alt="${escape(item.name)}"><div><h3>${escape(item.name)}</h3><small>${escape(item.category)} · ${escape(entry.size)}</small><div class="bag-quantity"><button data-qty="${index}" data-change="-1" aria-label="Decrease ${escape(item.name)} quantity">−</button><span aria-label="Quantity">${entry.qty}</span><button data-qty="${index}" data-change="1" aria-label="Increase ${escape(item.name)} quantity">+</button></div><button class="remove" data-remove="${index}" aria-label="Remove ${escape(item.name)}">Remove</button></div><span class="bag-price">${money(item.price*entry.qty)}</span></div>`; }).join('')+`<div class="bag-total"><span>Illustrative subtotal</span><strong>${money(bag.reduce((sum,entry)=>sum+products.get(entry.id).price*entry.qty,0))}</strong></div><p class="dialog-note">This bag is for exploring combinations. Checkout is not available, and no order has been placed. Your choices are saved in this browser when device storage is available.</p><button class="text-link" id="continueBrowsing">Continue exploring ↗</button>` : '<div class="bag-empty"><p>Your next move is waiting. Explore the collection and add a piece to see your look take shape.</p><a class="btn" href="king.html">Explore King ↗</a><a class="text-link" href="pawn.html">Explore Pawn ↗</a></div>'}</div>`);
    $$('[data-qty]',dialog).forEach(button => button.addEventListener('click', () => {
      const index=Number(button.dataset.qty), change=Number(button.dataset.change);
      bag[index].qty=Math.min(bag[index].qty+change,99);
      if (bag[index].qty<=0) bag.splice(index,1);
      updateBag(); showBag();
      const focus=$(`[data-qty="${index}"][data-change="${change}"]`,dialog);
      focus?.focus();
    }));
    $$('[data-remove]',dialog).forEach(button => button.addEventListener('click', () => { bag.splice(Number(button.dataset.remove),1); updateBag(); showBag(); }));
    $('#continueBrowsing',dialog)?.addEventListener('click', () => dialog.close());
  }
  const showSearch = () => {
    showDialog('<div class="dialog-body"><span class="eyebrow">Find your next move</span><h2 id="dialogTitle">Search the collection.</h2><label for="collectionSearch" class="dialog-note">Search by piece, color, or collection</label><input class="search-input" id="collectionSearch" type="search" placeholder="Try navy, tuxedo, or kids" autocomplete="off"><p class="dialog-note" id="searchCount" role="status"></p><div class="search-results" id="searchResults"></div><p class="dialog-note">Looking for women’s formal wear? <a class="text-link" href="queen.html">Preview Queen ↗</a></p></div>');
    const input=$('#collectionSearch',dialog);
    const render = () => {
      const words=input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      const found=catalog.filter(item => words.every(word=>`${item.name} ${item.tag} ${item.category} ${item.image.replace(/[-_]/g, " ")}`.toLowerCase().includes(word)));
      const shown=words.length ? found : catalog.slice(0,6);
      $('#searchCount',dialog).textContent=words.length ? `${found.length} ${found.length===1?'piece':'pieces'} found` : 'A few opening moves to inspire you';
      $('#searchResults',dialog).innerHTML=shown.length ? shown.map(item=>`<button class="search-result" data-result="${escape(item.id)}"><img src="${escape(item.image)}" alt="" loading="lazy"><span><strong>${escape(item.name)}</strong><small>${escape(item.category)} · ${money(item.price)}</small></span></button>`).join('') : '<p class="dialog-note">No pieces found. Try “suit”, “navy”, “kids”, or “shoes”.</p>';
      $$('[data-result]',dialog).forEach(button=>button.addEventListener('click',()=>showProduct(button.dataset.result)));
    };
    input.addEventListener('input',render); render(); input.focus();
  };
  $('.search-ic')?.addEventListener('click',showSearch);
  $('.bag-btn')?.addEventListener('click',showBag);
  $$('a.product-card[data-product]').forEach(card=>card.addEventListener('click',event=>{
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); showProduct(card.dataset.product);
  }));
  $$('[data-preview]').forEach(button=>button.addEventListener('click',()=>showProduct(button.dataset.preview)));
  $$('[data-info="imagery"]').forEach(button=>button.addEventListener('click',()=>showDialog('<div class="dialog-body"><span class="eyebrow">About this concept</span><h2 id="dialogTitle">A first look at Checkmatela.</h2><p class="info-copy">The men’s collection uses photography supplied in the Antonio Uomo product folder. The kids’ collection uses photography supplied in the Magen Kids product folder. Accessory, footwear, and individual suit-component visuals are AI-generated concept imagery used to demonstrate the brand direction.</p><p class="dialog-note">Names, pricing, and sizing illustrate a possible store experience. Women’s formal wear is presented as a coming-soon collection.</p></div>')));
  const linkedProduct=decodeURIComponent(location.hash.slice(1));
  if (products.has(linkedProduct)) showProduct(linkedProduct);
})();
