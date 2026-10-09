(() => {
  "use strict";

  /* ---------------- Header solid-on-scroll ---------------- */
  const header = document.getElementById('siteHeader');
  const onScrollHeader = () => {
    if (!header) return;
    header.classList.toggle('solid', window.scrollY > 40);
  };
  document.addEventListener('scroll', onScrollHeader, { passive: true });
  onScrollHeader();

  /* ---------------- Scroll reveal ---------------- */
  const revealTargets = document.querySelectorAll('[data-reveal], [data-reveal-group]');
  if ('IntersectionObserver' in window && revealTargets.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    revealTargets.forEach(el => io.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('in'));
  }

  /* ---------------- Exploding suit diagram (triggers once on view) ---------------- */
  const explodeStage = document.getElementById('explodeStage');
  if (explodeStage) {
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            explodeStage.classList.add('exploded');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.4 });
      io.observe(explodeStage);
    } else {
      explodeStage.classList.add('exploded');
    }
  }

  /* ---------------- Newsletter / waitlist forms ---------------- */
  document.querySelectorAll('.newsletter-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const address = form.querySelector('input[type="email"]')?.value.trim();
      if (!address) return;
      const subject = document.title.includes('Queen') ? 'Queen collection enquiry' : document.title.includes('Pawn') ? 'Pawn collection enquiry' : 'Checkmate collection enquiry';
      const body = `Hello Checkmate,\n\nMy email is ${address}. I would like to hear about the collection.\n\nMy occasion / question: \n\n(Use code WELCOME10 for 10% off my first order.)`;
      form.classList.add('sent');
      window.location.href = `mailto:suit.shop.dtla@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  });

  /* ---------------- Product quick-view stub ---------------- */
  document.querySelectorAll('.product-card__quick .btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });
  });

  /* ---------------- Gallery thumbnail swap (model + plain shots) ---------------- */
  document.querySelectorAll('.gallery-card').forEach(card => {
    const main = card.querySelector('.gallery-card__main-img');
    const thumbs = card.querySelectorAll('.gallery-thumb');
    thumbs.forEach(btn => {
      const preload = () => { if (btn.dataset.src) { const im = new Image(); im.src = btn.dataset.src; } };
      btn.addEventListener('mouseenter', preload, { once: true });
      btn.addEventListener('focus', preload, { once: true });
      btn.addEventListener('click', () => {
        if (!main || !btn.dataset.src) return;
        main.src = btn.dataset.src;
        thumbs.forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
      });
    });
  });

  /* ---------------- Style subcategory jump (e.g. Pawn styles) ---------------- */
  document.querySelectorAll('.style-select').forEach(sel => {
    sel.addEventListener('change', () => {
      const val = sel.value;
      if (!val) return;
      if (val.includes('.html')) {
        window.location.href = val;
        return;
      }
      const target = document.getElementById(val);
      if (!target) return;
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.classList.add('is-highlighted');
      setTimeout(() => target.classList.remove('is-highlighted'), 1600);
    });
  });

  /* ---------------- mailto forms (Book a Fitting): no backend, so the request opens in the visitor's email app ---------------- */
  document.querySelectorAll('form[data-mailto]').forEach(form => {
    const look = new URLSearchParams(window.location.search).get('look');
    const notes = form.querySelector('textarea[name="Notes"]');
    if (look && notes) notes.value = `I'm interested in ${look}. `;
    const lookingFor = form.querySelector('select[name="Looking for"]');
    if (look && lookingFor) {
      if (/kid|pawn/i.test(look)) lookingFor.value = "A kids' look";
      else if (/tuxedo/i.test(look)) lookingFor.value = 'A tuxedo';
      else if (/queen/i.test(look)) lookingFor.value = 'The Queen collection';
      else if (/shoe|accessor|bishop|rook/i.test(look)) lookingFor.value = 'Accessories or shoes';
    }
    form.addEventListener('submit', e => {
      e.preventDefault();
      const lines = [...new FormData(form).entries()].filter(([, v]) => String(v).trim()).map(([k, v]) => `${k}: ${v}`);
      const href = `mailto:${form.dataset.mailto}?subject=${encodeURIComponent(form.dataset.subject || 'Checkmate request')}&body=${encodeURIComponent(lines.join('\n'))}`;
      const ok = form.querySelector('.fit-form__ok');
      if (ok) ok.hidden = false;
      window.location.href = href;
    });
  });
})();
